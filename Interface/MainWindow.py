import copy
import json
import os

import mistune
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QColor, QIcon, QPalette, QPdfWriter, QTextCursor, QAction, QPageSize
from PyQt6.QtWidgets import QFileDialog, QLabel, QMainWindow, QInputDialog, QMessageBox, QSplitter, QApplication, QTextEdit, QFrame, QGridLayout

from Core.MarkdownRenderers import ConstructHTMLExportString, ConstructPDFExportHTMLString, Renderer
from Core.Notebook import Notebook
from Interface.Dialogs.AdvancedSearchDialog import AdvancedSearchDialog
from Interface.Dialogs.DefaultPopOutSizeDialog import DefaultPopOutSizeDialog
from Interface.Dialogs.DemotePageDialog import DemotePageDialog
from Interface.Dialogs.EditHeaderOrFooterDialog import EditHeaderOrFooterDialog
from Interface.Dialogs.FavoritesDialog import FavoritesDialog
from Interface.Dialogs.HighlightTextDialog import HighlightTextDialog
from Interface.Dialogs.ImageManagerDialog import ImageManagerDialog
from Interface.Dialogs.MovePageToDialog import MovePageToDialog
from Interface.Dialogs.NewPageDialog import NewPageDialog
from Interface.Dialogs.SearchForLinkedPagesDialog import SearchForLinkedPagesDialog
from Interface.Dialogs.SetDefaultNotebookDialog import SetDefaultNotebookDialog
from Interface.Dialogs.TemplateManagerDialog import TemplateManagerDialog
from Interface.Dialogs.AddToPageAndSubpagesDialog import AddToPageAndSubpagesDialog
from Interface.Dialogs.PopOutTextDialog import PopOutTextDialog
from Interface.Widgets.NavigationBar import NavigationBar
from Interface.Widgets.NotebookDisplayWidget import NotebookDisplayWidget
from Interface.Widgets.SearchWidget import SearchWidget
from Interface.Widgets.TextWidget import TextWidget
from SaveAndLoad.SaveAndOpenMixin import SaveAndOpenMixin


class MainWindow(QMainWindow, SaveAndOpenMixin):
    # Initialization Methods
    def __init__(self, ScriptName, AbsoluteDirectoryPath, AppInst):
        # Store Parameters
        self.ScriptName = ScriptName
        self.AbsoluteDirectoryPath = AbsoluteDirectoryPath
        self.AppInst = AppInst

        super().__init__()

        # Variables
        self.CurrentZoomLevel = 0
        self.BackList = []
        self.BackMaximum = 50
        self.ForwardList = []
        self.BackNavigation = False
        self.AutoScrollQueue = None
        self.ShowHitCounts = False
        self.SwapLeftAndMiddleClickForLinks = False
        self.MoveCursorToEndOfLinkText = True
        self.HighlightSyntax = True
        self.TextToHighlight = []
        self.TextToHighlightMatchCase = False
        self.AdvancedSearchHighlightText = True
        self.PopOutPages = []
        self.DefaultPopOutSize = {"Width": 0, "Height": 0}
        self.AdvancedSearchDialogInst = None
        self.SortIgnoresBlankLines = True

        # Set Up Save and Open
        self.SetUpSaveAndOpen(".ntbk", "Notebook", (Notebook,))

        # Create Notebook
        self.Notebook = Notebook()

        # Create Interface
        self.CreateInterface()
        self.show()

        # Create Pop-Out Markdown Parser
        self.PopOutMarkdownRenderer = Renderer(self.Notebook)
        self.PopOutMarkdownParser = mistune.Markdown(renderer=self.PopOutMarkdownRenderer)

        # Load Configs
        self.LoadConfigs()

        # Open Default Notebook if Set
        DefaultNotebookPath = (self.GzipDefaultNotebook if self.GzipMode else self.DefaultNotebook)
        if DefaultNotebookPath is not None:
            if os.path.isfile(DefaultNotebookPath):
                self.OpenActionTriggered(DefaultNotebookPath)

    def CreateInterface(self):
        # Load Theme
        self.LoadTheme()

        # Create Icons
        self.CreateIcons()

        # Toggle Read Mode Actions List
        self.ToggleReadModeActionsList = []

        # Create Frame
        self.Frame = QFrame()

        # Create Notebook Display Widget
        self.NotebookDisplayWidgetInst = NotebookDisplayWidget(self.Notebook, self)
        self.NotebookDisplayWidgetInst.itemSelectionChanged.connect(self.PageSelected)

        # Create Text Widget
        self.TextWidgetInst = TextWidget(self.Notebook, self)
        self.TextWidgetInst.textChanged.connect(self.TextChanged)

        # Create Search Widget
        self.SearchWidgetInst = SearchWidget(self.Notebook, self)

        # Create Navigation Bar
        self.NavigationBarInst = NavigationBar(self)

        # Create and Populate Layout
        self.FrameLayout = QGridLayout()
        self.NotebookAndTextSplitter = QSplitter(Qt.Orientation.Horizontal)
        self.NotebookAndTextSplitter.addWidget(self.NotebookDisplayWidgetInst)
        self.NotebookAndTextSplitter.addWidget(self.TextWidgetInst)
        self.NotebookAndTextSplitter.setStretchFactor(1, 1)
        self.NotebookAndTextSplitter.setChildrenCollapsible(False)
        self.NotebookAndSearchSplitter = QSplitter(Qt.Orientation.Vertical)
        self.NotebookAndSearchSplitter.addWidget(self.NotebookAndTextSplitter)
        self.NotebookAndSearchSplitter.addWidget(self.SearchWidgetInst)
        self.NotebookAndSearchSplitter.setStretchFactor(0, 1)
        self.NotebookAndSearchSplitter.setChildrenCollapsible(False)
        self.FrameLayout.addWidget(self.NotebookAndSearchSplitter, 0, 0)
        self.FrameLayout.addWidget(self.NavigationBarInst, 1, 0)
        self.FrameLayout.setRowStretch(0, 1)
        self.Frame.setLayout(self.FrameLayout)
        self.setCentralWidget(self.Frame)

        # Create Actions
        self.CreateActions()

        # Disable Edit-Only Actions and Widgets
        for Action in self.ToggleReadModeActionsList:
            Action.setEnabled(not self.TextWidgetInst.ReadMode)

        # Create Menu Bar
        self.CreateMenuBar()

        # Create Tool Bar
        self.CreateToolBar()

        # Create Status Bar
        self.StatusBar = self.statusBar()
        self.SearchResultsStatsLabel = QLabel("No search results.")
        self.SearchResultsStatsLabel.setVisible(False)
        self.SearchResultsStatsLabel.setEnabled(False)
        self.StatusBar.addPermanentWidget(self.SearchResultsStatsLabel)

        # Window Setup
        self.WindowSetup()

        # Initial Focus on NotebookDisplayWidgetInst
        self.NotebookDisplayWidgetInst.setFocus()

        # Initial Selection of Root Page
        self.PageSelected(IndexPath=[0], SkipUpdatingBackAndForward=True)

        # Set Up Tab Order
        self.setTabOrder(self.NotebookDisplayWidgetInst, self.TextWidgetInst)
        self.setTabOrder(self.TextWidgetInst, self.SearchWidgetInst)
        self.setTabOrder(self.SearchWidgetInst, self.NotebookDisplayWidgetInst)

        # Create Keybindings
        self.CreateKeybindings()

    def CreateIcons(self):
        self.WindowIcon = QIcon(self.GetResourcePath("Assets/SnakeNotes Icon.png"))
        self.NewPageIcon = QIcon(self.GetResourcePath("Assets/SnakeNotes New Page Icon.png"))
        self.DeletePageIcon = QIcon(self.GetResourcePath("Assets/SnakeNotes Delete Page Icon.png"))
        self.MovePageUpIcon = QIcon(self.GetResourcePath("Assets/SnakeNotes Move Page Up Icon.png"))
        self.MovePageDownIcon = QIcon(self.GetResourcePath("Assets/SnakeNotes Move Page Down Icon.png"))
        self.PromotePageIcon = QIcon(self.GetResourcePath("Assets/SnakeNotes Promote Page Icon.png"))
        self.DemotePageIcon = QIcon(self.GetResourcePath("Assets/SnakeNotes Demote Page Icon.png"))
        self.RenamePageIcon = QIcon(self.GetResourcePath("Assets/SnakeNotes Rename Page Icon.png"))
        self.ExpandAllIcon = QIcon(self.GetResourcePath("Assets/SnakeNotes Expand All Icon.png"))
        self.CollapseAllIcon = QIcon(self.GetResourcePath("Assets/SnakeNotes Collapse All Icon.png"))
        self.ToggleReadModeIcon = QIcon(self.GetResourcePath("Assets/SnakeNotes Toggle Read Mode Icon.png"))
        self.BackIcon = QIcon(self.GetResourcePath("Assets/SnakeNotes Back Icon.png"))
        self.ForwardIcon = QIcon(self.GetResourcePath("Assets/SnakeNotes Forward Icon.png"))
        self.ItalicsIcon = QIcon(self.GetResourcePath("Assets/SnakeNotes Italics Icon.png"))
        self.BoldIcon = QIcon(self.GetResourcePath("Assets/SnakeNotes Bold Icon.png"))
        self.StrikethroughIcon = QIcon(self.GetResourcePath("Assets/SnakeNotes Strikethrough Icon.png"))
        self.BulletListIcon = QIcon(self.GetResourcePath("Assets/SnakeNotes Bullet List Icon.png"))
        self.NumberListIcon = QIcon(self.GetResourcePath("Assets/SnakeNotes Number List Icon.png"))
        self.QuoteIcon = QIcon(self.GetResourcePath("Assets/SnakeNotes Quote Icon.png"))
        self.InsertLinksIcon = QIcon(self.GetResourcePath("Assets/SnakeNotes Insert Link(s) Icon.png"))
        self.InsertExternalLinkIcon = QIcon(self.GetResourcePath("Assets/SnakeNotes Insert External Link Icon.png"))
        self.InsertTableIcon = QIcon(self.GetResourcePath("Assets/SnakeNotes Insert Table Icon.png"))
        self.InsertImageIcon = QIcon(self.GetResourcePath("Assets/SnakeNotes Insert Image Icon.png"))
        self.ZoomOutIcon = QIcon(self.GetResourcePath("Assets/SnakeNotes Zoom Out Icon.png"))
        self.ZoomInIcon = QIcon(self.GetResourcePath("Assets/SnakeNotes Zoom In Icon.png"))
        self.PopOutPageIcon = QIcon(self.GetResourcePath("Assets/SnakeNotes Pop Out Page Icon.png"))
        self.FavoritesIcon = QIcon(self.GetResourcePath("Assets/SnakeNotes Favorites Icon.png"))
        self.SearchIcon = QIcon(self.GetResourcePath("Assets/SnakeNotes Search Icon.png"))
        self.ToggleSearchIcon = QIcon(self.GetResourcePath("Assets/SnakeNotes Toggle Search Icon.png"))

    def CreateActions(self):
        # File Actions
        self.NewAction = QAction("New")
        self.NewAction.triggered.connect(self.NewActionTriggered)

        self.OpenAction = QAction("Open")
        self.OpenAction.triggered.connect(lambda: self.OpenActionTriggered())

        self.FavoritesAction = QAction(self.FavoritesIcon, "Favorites")
        self.FavoritesAction.triggered.connect(self.Favorites)

        self.SetDefaultNotebookAction = QAction("Set Default Notebook")
        self.SetDefaultNotebookAction.triggered.connect(self.SetDefaultNotebook)

        self.SaveAction = QAction("Save")
        self.SaveAction.triggered.connect(lambda: self.SaveActionTriggered())

        self.SaveAsAction = QAction("Save As")
        self.SaveAsAction.triggered.connect(lambda: self.SaveActionTriggered(SaveAs=True))

        self.ExportHTMLAction = QAction("Export Notebook as HTML File")
        self.ExportHTMLAction.triggered.connect(self.ExportHTML)

        self.ExportPageAsPDFAction = QAction("Export Page as PDF File")
        self.ExportPageAsPDFAction.triggered.connect(self.ExportPageAsPDF)

        self.ExportNotebookAsPDFsAction = QAction("Export Notebook as PDF Files")
        self.ExportNotebookAsPDFsAction.triggered.connect(self.ExportNotebookAsPDFs)

        self.ExportPageAction = QAction("Export Page File")
        self.ExportPageAction.triggered.connect(self.ExportPage)

        self.ImportPageAction = QAction("Import Page File")
        self.ImportPageAction.triggered.connect(self.ImportPage)
        self.ToggleReadModeActionsList.append(self.ImportPageAction)

        self.GzipModeAction = QAction("Gzip Mode (Smaller Files)")
        self.GzipModeAction.setCheckable(True)
        self.GzipModeAction.setChecked(self.GzipMode)
        self.GzipModeAction.triggered.connect(self.ToggleGzipMode)

        self.ExitAction = QAction("Exit")
        self.ExitAction.triggered.connect(self.close)

        # Edit Actions
        self.ToggleReadModeAction = QAction(self.ToggleReadModeIcon, "Toggle Read Mode")
        self.ToggleReadModeAction.triggered.connect(self.ToggleReadMode)

        self.ItalicsAction = QAction(self.ItalicsIcon, "Italics")
        self.ItalicsAction.triggered.connect(self.TextWidgetInst.Italics)
        self.ToggleReadModeActionsList.append(self.ItalicsAction)

        self.BoldAction = QAction(self.BoldIcon, "Bold")
        self.BoldAction.triggered.connect(self.TextWidgetInst.Bold)
        self.ToggleReadModeActionsList.append(self.BoldAction)

        self.StrikethroughAction = QAction(self.StrikethroughIcon, "&Strikethrough")
        self.StrikethroughAction.triggered.connect(self.TextWidgetInst.Strikethrough)
        self.ToggleReadModeActionsList.append(self.StrikethroughAction)

        self.CodeSpanAction = QAction("&Code Span")
        self.CodeSpanAction.triggered.connect(self.TextWidgetInst.CodeSpan)
        self.ToggleReadModeActionsList.append(self.CodeSpanAction)

        self.HeaderOneAction = QAction("Header 1")
        self.HeaderOneAction.triggered.connect(lambda: self.TextWidgetInst.Header(1))
        self.ToggleReadModeActionsList.append(self.HeaderOneAction)

        self.HeaderTwoAction = QAction("Header 2")
        self.HeaderTwoAction.triggered.connect(lambda: self.TextWidgetInst.Header(2))
        self.ToggleReadModeActionsList.append(self.HeaderTwoAction)

        self.HeaderThreeAction = QAction("Header 3")
        self.HeaderThreeAction.triggered.connect(lambda: self.TextWidgetInst.Header(3))
        self.ToggleReadModeActionsList.append(self.HeaderThreeAction)

        self.HeaderFourAction = QAction("Header 4")
        self.HeaderFourAction.triggered.connect(lambda: self.TextWidgetInst.Header(4))
        self.ToggleReadModeActionsList.append(self.HeaderFourAction)

        self.HeaderFiveAction = QAction("Header 5")
        self.HeaderFiveAction.triggered.connect(lambda: self.TextWidgetInst.Header(5))
        self.ToggleReadModeActionsList.append(self.HeaderFiveAction)

        self.HeaderSixAction = QAction("Header 6")
        self.HeaderSixAction.triggered.connect(lambda: self.TextWidgetInst.Header(6))
        self.ToggleReadModeActionsList.append(self.HeaderSixAction)

        self.BulletListAction = QAction(self.BulletListIcon, "&Bullet List")
        self.BulletListAction.triggered.connect(self.TextWidgetInst.BulletList)
        self.ToggleReadModeActionsList.append(self.BulletListAction)

        self.NumberListAction = QAction(self.NumberListIcon, "&Number List")
        self.NumberListAction.triggered.connect(self.TextWidgetInst.NumberList)
        self.ToggleReadModeActionsList.append(self.NumberListAction)

        self.QuoteAction = QAction(self.QuoteIcon, "&Quote")
        self.QuoteAction.triggered.connect(self.TextWidgetInst.Quote)
        self.ToggleReadModeActionsList.append(self.QuoteAction)

        self.CodeBlockAction = QAction("C&ode Block")
        self.CodeBlockAction.triggered.connect(self.TextWidgetInst.CodeBlock)
        self.ToggleReadModeActionsList.append(self.CodeBlockAction)

        self.IndentAction = QAction("&Indent")
        self.IndentAction.triggered.connect(self.TextWidgetInst.Indent)
        self.ToggleReadModeActionsList.append(self.IndentAction)

        self.OutdentAction = QAction("O&utdent")
        self.OutdentAction.triggered.connect(self.TextWidgetInst.Outdent)
        self.ToggleReadModeActionsList.append(self.OutdentAction)

        self.HorizontalRuleAction = QAction("&Horizontal Rule")
        self.HorizontalRuleAction.triggered.connect(self.TextWidgetInst.HorizontalRule)
        self.ToggleReadModeActionsList.append(self.HorizontalRuleAction)

        self.FootnoteAction = QAction("Footnote")
        self.FootnoteAction.triggered.connect(self.TextWidgetInst.Footnote)
        self.ToggleReadModeActionsList.append(self.FootnoteAction)

        self.InlineFootnoteStyleAction = QAction("Inline Footnote Style")
        self.InlineFootnoteStyleAction.setCheckable(True)
        self.InlineFootnoteStyleAction.setChecked(True)
        self.InlineFootnoteStyleAction.triggered.connect(self.ToggleInlineFootnoteStyle)
        self.ToggleReadModeActionsList.append(self.InlineFootnoteStyleAction)

        self.InsertLinksAction = QAction(self.InsertLinksIcon, "Insert Link(s)")
        self.InsertLinksAction.triggered.connect(self.TextWidgetInst.InsertLinks)
        self.ToggleReadModeActionsList.append(self.InsertLinksAction)

        self.AddTitleToolTipsToLinksAction = QAction("Add Title Tool Tips to Links")
        self.AddTitleToolTipsToLinksAction.triggered.connect(self.AddTitleToolTipsToLinks)
        self.ToggleReadModeActionsList.append(self.AddTitleToolTipsToLinksAction)

        self.InsertExternalLinkAction = QAction(self.InsertExternalLinkIcon, "Insert External Link")
        self.InsertExternalLinkAction.triggered.connect(self.TextWidgetInst.InsertExternalLink)
        self.ToggleReadModeActionsList.append(self.InsertExternalLinkAction)

        self.TextToLinkAction = QAction("Convert Exact Title to Link")
        self.TextToLinkAction.triggered.connect(self.TextWidgetInst.TextToLink)
        self.ToggleReadModeActionsList.append(self.TextToLinkAction)

        self.MoveCursorToEndOfLinkTextAction = QAction("Move Cursor to End of Link Text")
        self.MoveCursorToEndOfLinkTextAction.setCheckable(True)
        self.MoveCursorToEndOfLinkTextAction.setChecked(True)
        self.MoveCursorToEndOfLinkTextAction.triggered.connect(self.ToggleMoveCursorToEndOfLinkText)
        self.ToggleReadModeActionsList.append(self.MoveCursorToEndOfLinkTextAction)

        self.InsertTableAction = QAction(self.InsertTableIcon, "Insert Table")
        self.InsertTableAction.triggered.connect(self.TextWidgetInst.InsertTable)
        self.ToggleReadModeActionsList.append(self.InsertTableAction)

        self.InsertImageAction = QAction(self.InsertImageIcon, "Insert Image")
        self.InsertImageAction.triggered.connect(self.TextWidgetInst.InsertImage)
        self.ToggleReadModeActionsList.append(self.InsertImageAction)

        self.PrependAction = QAction("Prepend Text to Page and Sub Pages")
        self.PrependAction.triggered.connect(lambda: self.AddTextToPageAndSubpages(Prepend=True))
        self.ToggleReadModeActionsList.append(self.PrependAction)

        self.AppendAction = QAction("Append Text to Page and Sub Pages")
        self.AppendAction.triggered.connect(self.AddTextToPageAndSubpages)
        self.ToggleReadModeActionsList.append(self.AppendAction)

        self.MoveLineUpAction = QAction("Move Line Up")
        self.MoveLineUpAction.triggered.connect(self.TextWidgetInst.MoveLineUp)
        self.ToggleReadModeActionsList.append(self.MoveLineUpAction)

        self.MoveLineDownAction = QAction("Move Line Down")
        self.MoveLineDownAction.triggered.connect(self.TextWidgetInst.MoveLineDown)
        self.ToggleReadModeActionsList.append(self.MoveLineDownAction)

        self.DuplicateLinesAction = QAction("Duplicate Line")
        self.DuplicateLinesAction.triggered.connect(self.TextWidgetInst.DuplicateLines)
        self.ToggleReadModeActionsList.append(self.DuplicateLinesAction)

        self.DeleteLineAction = QAction("Delete Line")
        self.DeleteLineAction.triggered.connect(self.TextWidgetInst.DeleteLine)
        self.ToggleReadModeActionsList.append(self.DeleteLineAction)

        self.SortLinesAction = QAction("Sort Lines")
        self.SortLinesAction.triggered.connect(self.TextWidgetInst.SortLines)
        self.ToggleReadModeActionsList.append(self.SortLinesAction)

        self.SortIgnoresBlankLinesAction = QAction("Sort Ignores Blank Lines")
        self.SortIgnoresBlankLinesAction.setCheckable(True)
        self.SortIgnoresBlankLinesAction.setChecked(True)
        self.SortIgnoresBlankLinesAction.triggered.connect(self.ToggleSortIgnoresBlankLines)
        self.ToggleReadModeActionsList.append(self.SortIgnoresBlankLinesAction)

        # View Actions
        self.BackAction = QAction(self.BackIcon, "Back")
        self.BackAction.triggered.connect(self.Back)
        self.BackAction.setEnabled(False)

        self.ForwardAction = QAction(self.ForwardIcon, "Forward")
        self.ForwardAction.triggered.connect(self.Forward)
        self.ForwardAction.setEnabled(False)

        self.SearchAction = QAction(self.SearchIcon, "Search")
        self.SearchAction.triggered.connect(self.SearchWidgetInst.GrabFocus)

        self.ToggleSearchAction = QAction(self.ToggleSearchIcon, "Toggle Search")
        self.ToggleSearchAction.triggered.connect(self.SearchWidgetInst.ToggleVisibility)

        self.SearchForLinkingPagesAction = QAction("&Search for Linking Pages")
        self.SearchForLinkingPagesAction.triggered.connect(self.SearchForLinkingPages)

        self.SearchForLinkedPagesAction = QAction("Search for &Linked Pages")
        self.SearchForLinkedPagesAction.triggered.connect(self.SearchForLinkedPages)

        self.CopySearchResultsAction = QAction("Copy Search Results")
        self.CopySearchResultsAction.triggered.connect(self.SearchWidgetInst.CopySearchResults)

        self.AdvancedSearchAction = QAction("Advanced Search")
        self.AdvancedSearchAction.triggered.connect(self.AdvancedSearch)

        self.ShowHitCountsAction = QAction("Show Hit Counts in Search Results")
        self.ShowHitCountsAction.setCheckable(True)
        self.ShowHitCountsAction.setChecked(False)
        self.ShowHitCountsAction.triggered.connect(self.ToggleShowHitCounts)

        self.ZoomOutAction = QAction(self.ZoomOutIcon, "Zoom Out")
        self.ZoomOutAction.triggered.connect(self.ZoomOut)

        self.ZoomInAction = QAction(self.ZoomInIcon, "Zoom In")
        self.ZoomInAction.triggered.connect(self.ZoomIn)

        self.DefaultZoomAction = QAction("Default Zoom")
        self.DefaultZoomAction.triggered.connect(self.DefaultZoom)

        self.PopOutPageAction = QAction(self.PopOutPageIcon, "Pop Out Page")
        self.PopOutPageAction.triggered.connect(lambda: self.PopOutPage())

        self.SetDefaultPopOutSizeAction = QAction("Set Default Pop-Out Page Size")
        self.SetDefaultPopOutSizeAction.triggered.connect(self.SetDefaultPopOutSize)

        self.SwapLeftAndMiddleClickForLinksAction = QAction("Swap Left and Middle Click for Links")
        self.SwapLeftAndMiddleClickForLinksAction.setCheckable(True)
        self.SwapLeftAndMiddleClickForLinksAction.setChecked(False)
        self.SwapLeftAndMiddleClickForLinksAction.triggered.connect(self.ToggleSwapLeftAndMiddleClickForLinks)

        self.GoToIndexPathAction = QAction("Go to Page by Index Path")
        self.GoToIndexPathAction.triggered.connect(self.GoToIndexPath)

        self.ExpandAllAction = QAction(self.ExpandAllIcon, "&Expand All")
        self.ExpandAllAction.triggered.connect(self.NotebookDisplayWidgetInst.expandAll)

        self.ExpandRecursivelyAction = QAction("Expand Current Page Recursively")
        self.ExpandRecursivelyAction.triggered.connect(self.NotebookDisplayWidgetInst.ExpandRecursively)

        self.CollapseAllAction = QAction(self.CollapseAllIcon, "&Collapse All")
        self.CollapseAllAction.triggered.connect(self.NotebookDisplayWidgetInst.collapseAll)

        self.HighlightSyntaxAction = QAction("Highlight Syntax")
        self.HighlightSyntaxAction.setCheckable(True)
        self.HighlightSyntaxAction.setChecked(True)
        self.HighlightSyntaxAction.triggered.connect(self.ToggleHighlightSyntax)
        self.ToggleReadModeActionsList.append(self.HighlightSyntaxAction)

        self.HighlightTextAction = QAction("Highlight Text")
        self.HighlightTextAction.triggered.connect(self.HighlightText)

        self.SetThemeAction = QAction("Set Theme")
        self.SetThemeAction.triggered.connect(self.SetTheme)

        self.SetStartupSizeAndPositionAction = QAction("Set Startup Size and Position")
        self.SetStartupSizeAndPositionAction.triggered.connect(self.SetStartupSizeAndPosition)

        # Notebook Actions
        self.NewPageAction = QAction(self.NewPageIcon, "New Page")
        self.NewPageAction.triggered.connect(self.NewPage)
        self.ToggleReadModeActionsList.append(self.NewPageAction)

        self.DeletePageAction = QAction(self.DeletePageIcon, "Delete Page")
        self.DeletePageAction.triggered.connect(self.DeletePage)
        self.ToggleReadModeActionsList.append(self.DeletePageAction)

        self.RenamePageAction = QAction(self.RenamePageIcon, "Rename Page")
        self.RenamePageAction.triggered.connect(self.RenamePage)
        self.ToggleReadModeActionsList.append(self.RenamePageAction)

        self.AddSiblingPageBeforeAction = QAction("Add Sibling Page Before Current Page")
        self.AddSiblingPageBeforeAction.triggered.connect(self.AddSiblingPageBefore)
        self.ToggleReadModeActionsList.append(self.AddSiblingPageBeforeAction)

        self.MovePageUpAction = QAction(self.MovePageUpIcon, "Move Page Up")
        self.MovePageUpAction.triggered.connect(lambda: self.MovePage(-1))
        self.ToggleReadModeActionsList.append(self.MovePageUpAction)

        self.MovePageDownAction = QAction(self.MovePageDownIcon, "Move Page Down")
        self.MovePageDownAction.triggered.connect(lambda: self.MovePage(1))
        self.ToggleReadModeActionsList.append(self.MovePageDownAction)

        self.PromotePageAction = QAction(self.PromotePageIcon, "Promote Page")
        self.PromotePageAction.triggered.connect(self.PromotePage)
        self.ToggleReadModeActionsList.append(self.PromotePageAction)

        self.PromoteAllSubPagesAction = QAction("Promote All Sub Pages")
        self.PromoteAllSubPagesAction.triggered.connect(self.PromoteAllSubPages)
        self.ToggleReadModeActionsList.append(self.PromoteAllSubPagesAction)

        self.DemotePageAction = QAction(self.DemotePageIcon, "Demote Page")
        self.DemotePageAction.triggered.connect(self.DemotePage)
        self.ToggleReadModeActionsList.append(self.DemotePageAction)

        self.DemoteAllSiblingPagesAction = QAction("Demote All Sibling Pages")
        self.DemoteAllSiblingPagesAction.triggered.connect(self.DemoteAllSiblingPages)
        self.ToggleReadModeActionsList.append(self.DemoteAllSiblingPagesAction)

        self.MovePageToAction = QAction("Move Page To...")
        self.MovePageToAction.triggered.connect(self.MovePageTo)
        self.ToggleReadModeActionsList.append(self.MovePageToAction)

        self.AlphabetizeSubPagesAction = QAction("Alphabetize Sub Pages")
        self.AlphabetizeSubPagesAction.triggered.connect(self.AlphabetizeSubPages)
        self.ToggleReadModeActionsList.append(self.AlphabetizeSubPagesAction)

        self.CopyLinkToCurrentPageAction = QAction("Copy Link to Current Page")
        self.CopyLinkToCurrentPageAction.triggered.connect(self.CopyLinkToCurrentPage)

        self.CopyIndexPathToCurrentPageAction = QAction("Copy Index Path to Current Page")
        self.CopyIndexPathToCurrentPageAction.triggered.connect(self.CopyIndexPathToCurrentPage)

        self.ImageManagerAction = QAction("&Image Manager")
        self.ImageManagerAction.triggered.connect(lambda: self.ImageManager())

        self.TemplateManagerAction = QAction("&Template Manager")
        self.TemplateManagerAction.triggered.connect(self.TemplateManager)
        self.ToggleReadModeActionsList.append(self.TemplateManagerAction)

        self.EditHeaderAction = QAction("Edit &Header")
        self.EditHeaderAction.triggered.connect(lambda: self.EditHeaderOrFooter("Header"))
        self.ToggleReadModeActionsList.append(self.EditHeaderAction)

        self.EditFooterAction = QAction("Edit &Footer")
        self.EditFooterAction.triggered.connect(lambda: self.EditHeaderOrFooter("Footer"))
        self.ToggleReadModeActionsList.append(self.EditFooterAction)

    def CreateMenuBar(self):
        self.MenuBar = self.menuBar()

        self.FileMenu = self.MenuBar.addMenu("&File")
        self.FileMenu.addAction(self.NewAction)
        self.FileMenu.addAction(self.OpenAction)
        self.FileMenu.addAction(self.FavoritesAction)
        self.FileMenu.addAction(self.SetDefaultNotebookAction)
        self.FileMenu.addSeparator()
        self.FileMenu.addAction(self.SaveAction)
        self.FileMenu.addAction(self.SaveAsAction)
        self.FileMenu.addSeparator()
        self.FileMenu.addAction(self.ExportHTMLAction)
        self.FileMenu.addAction(self.ExportPageAsPDFAction)
        self.FileMenu.addAction(self.ExportNotebookAsPDFsAction)
        self.FileMenu.addSeparator()
        self.FileMenu.addAction(self.ExportPageAction)
        self.FileMenu.addAction(self.ImportPageAction)
        self.FileMenu.addSeparator()
        self.FileMenu.addAction(self.GzipModeAction)
        self.FileMenu.addSeparator()
        self.FileMenu.addAction(self.ExitAction)

        self.EditMenu = self.MenuBar.addMenu("&Edit")
        self.EditMenu.addAction(self.ToggleReadModeAction)
        self.EditMenu.addSeparator()
        self.EditMenu.addAction(self.ItalicsAction)
        self.EditMenu.addAction(self.BoldAction)
        self.EditMenu.addAction(self.StrikethroughAction)
        self.EditMenu.addAction(self.CodeSpanAction)
        self.EditMenu.addSeparator()
        self.EditMenu.addAction(self.HeaderOneAction)
        self.EditMenu.addAction(self.HeaderTwoAction)
        self.EditMenu.addAction(self.HeaderThreeAction)
        self.EditMenu.addAction(self.HeaderFourAction)
        self.EditMenu.addAction(self.HeaderFiveAction)
        self.EditMenu.addAction(self.HeaderSixAction)
        self.EditMenu.addSeparator()
        self.EditMenu.addAction(self.BulletListAction)
        self.EditMenu.addAction(self.NumberListAction)
        self.EditMenu.addAction(self.QuoteAction)
        self.EditMenu.addAction(self.CodeBlockAction)
        self.EditMenu.addAction(self.IndentAction)
        self.EditMenu.addAction(self.OutdentAction)
        self.EditMenu.addSeparator()
        self.EditMenu.addAction(self.HorizontalRuleAction)
        self.EditMenu.addAction(self.FootnoteAction)
        self.EditMenu.addAction(self.InlineFootnoteStyleAction)
        self.EditMenu.addSeparator()
        self.EditMenu.addAction(self.InsertLinksAction)
        self.EditMenu.addAction(self.AddTitleToolTipsToLinksAction)
        self.EditMenu.addAction(self.InsertExternalLinkAction)
        self.EditMenu.addAction(self.TextToLinkAction)
        self.EditMenu.addAction(self.MoveCursorToEndOfLinkTextAction)
        self.EditMenu.addAction(self.InsertTableAction)
        self.EditMenu.addAction(self.InsertImageAction)
        self.EditMenu.addSeparator()
        self.EditMenu.addAction(self.PrependAction)
        self.EditMenu.addAction(self.AppendAction)
        self.EditMenu.addSeparator()
        self.EditMenu.addAction(self.MoveLineUpAction)
        self.EditMenu.addAction(self.MoveLineDownAction)
        self.EditMenu.addAction(self.DuplicateLinesAction)
        self.EditMenu.addAction(self.DeleteLineAction)
        self.EditMenu.addAction(self.SortLinesAction)
        self.EditMenu.addAction(self.SortIgnoresBlankLinesAction)

        self.ViewMenu = self.MenuBar.addMenu("&View")
        self.ViewMenu.addAction(self.BackAction)
        self.ViewMenu.addAction(self.ForwardAction)
        self.ViewMenu.addSeparator()
        self.ViewMenu.addAction(self.SearchAction)
        self.ViewMenu.addAction(self.ToggleSearchAction)
        self.ViewMenu.addAction(self.SearchForLinkingPagesAction)
        self.ViewMenu.addAction(self.SearchForLinkedPagesAction)
        self.ViewMenu.addAction(self.CopySearchResultsAction)
        self.ViewMenu.addAction(self.AdvancedSearchAction)
        self.ViewMenu.addAction(self.ShowHitCountsAction)
        self.ViewMenu.addSeparator()
        self.ViewMenu.addAction(self.ZoomOutAction)
        self.ViewMenu.addAction(self.ZoomInAction)
        self.ViewMenu.addAction(self.DefaultZoomAction)
        self.ViewMenu.addSeparator()
        self.ViewMenu.addAction(self.PopOutPageAction)
        self.ViewMenu.addAction(self.SetDefaultPopOutSizeAction)
        self.ViewMenu.addAction(self.SwapLeftAndMiddleClickForLinksAction)
        self.ViewMenu.addSeparator()
        self.ViewMenu.addAction(self.GoToIndexPathAction)
        self.ViewMenu.addSeparator()
        self.ViewMenu.addAction(self.ExpandAllAction)
        self.ViewMenu.addAction(self.ExpandRecursivelyAction)
        self.ViewMenu.addAction(self.CollapseAllAction)
        self.ViewMenu.addSeparator()
        self.ViewMenu.addAction(self.HighlightSyntaxAction)
        self.ViewMenu.addAction(self.HighlightTextAction)
        self.ViewMenu.addSeparator()
        self.ViewMenu.addAction(self.SetThemeAction)
        self.ViewMenu.addAction(self.SetStartupSizeAndPositionAction)

        self.NotebookMenu = self.MenuBar.addMenu("&Notebook")
        self.NotebookMenu.addAction(self.NewPageAction)
        self.NotebookMenu.addAction(self.DeletePageAction)
        self.NotebookMenu.addAction(self.RenamePageAction)
        self.NotebookMenu.addAction(self.AddSiblingPageBeforeAction)
        self.NotebookMenu.addSeparator()
        self.NotebookMenu.addAction(self.MovePageUpAction)
        self.NotebookMenu.addAction(self.MovePageDownAction)
        self.NotebookMenu.addAction(self.PromotePageAction)
        self.NotebookMenu.addAction(self.DemotePageAction)
        self.NotebookMenu.addAction(self.PromoteAllSubPagesAction)
        self.NotebookMenu.addAction(self.DemoteAllSiblingPagesAction)
        self.NotebookMenu.addAction(self.MovePageToAction)
        self.NotebookMenu.addAction(self.AlphabetizeSubPagesAction)
        self.NotebookMenu.addSeparator()
        self.NotebookMenu.addAction(self.CopyLinkToCurrentPageAction)
        self.NotebookMenu.addAction(self.CopyIndexPathToCurrentPageAction)
        self.NotebookMenu.addSeparator()
        self.NotebookMenu.addAction(self.ImageManagerAction)
        self.NotebookMenu.addAction(self.TemplateManagerAction)
        self.NotebookMenu.addSeparator()
        self.NotebookMenu.addAction(self.EditHeaderAction)
        self.NotebookMenu.addAction(self.EditFooterAction)

    def CreateToolBar(self):
        self.ToolBar = self.addToolBar("Actions")
        self.ToolBar.addAction(self.ToggleReadModeAction)
        self.ToolBar.addAction(self.BackAction)
        self.ToolBar.addAction(self.ForwardAction)
        self.ToolBar.addSeparator()
        self.ToolBar.addAction(self.NewPageAction)
        self.ToolBar.addAction(self.DeletePageAction)
        self.ToolBar.addAction(self.RenamePageAction)
        self.ToolBar.addSeparator()
        self.ToolBar.addAction(self.MovePageUpAction)
        self.ToolBar.addAction(self.MovePageDownAction)
        self.ToolBar.addAction(self.PromotePageAction)
        self.ToolBar.addAction(self.DemotePageAction)
        self.ToolBar.addSeparator()
        self.ToolBar.addAction(self.ItalicsAction)
        self.ToolBar.addAction(self.BoldAction)
        self.ToolBar.addAction(self.StrikethroughAction)
        self.ToolBar.addSeparator()
        self.ToolBar.addAction(self.BulletListAction)
        self.ToolBar.addAction(self.NumberListAction)
        self.ToolBar.addAction(self.QuoteAction)
        self.ToolBar.addSeparator()
        self.ToolBar.addAction(self.InsertLinksAction)
        self.ToolBar.addAction(self.InsertExternalLinkAction)
        self.ToolBar.addAction(self.InsertTableAction)
        self.ToolBar.addAction(self.InsertImageAction)
        self.ToolBar.addSeparator()
        self.ToolBar.addAction(self.SearchAction)
        self.ToolBar.addAction(self.ToggleSearchAction)
        self.ToolBar.addSeparator()
        self.ToolBar.addAction(self.ZoomOutAction)
        self.ToolBar.addAction(self.ZoomInAction)
        self.ToolBar.addAction(self.PopOutPageAction)
        self.ToolBar.addSeparator()
        self.ToolBar.addAction(self.FavoritesAction)

    def CreateKeybindings(self):
        self.DefaultKeybindings = {}
        self.DefaultKeybindings["NewAction"] = "Ctrl+Shift+N"
        self.DefaultKeybindings["OpenAction"] = "Ctrl+O"
        self.DefaultKeybindings["FavoritesAction"] = "Ctrl+Shift+O"
        self.DefaultKeybindings["SaveAction"] = "Ctrl+S"
        self.DefaultKeybindings["SaveAsAction"] = "Ctrl+Shift+S"
        self.DefaultKeybindings["ExitAction"] = "Ctrl+Q"
        self.DefaultKeybindings["ToggleReadModeAction"] = "Ctrl+E"
        self.DefaultKeybindings["BackAction"] = "Ctrl+,"
        self.DefaultKeybindings["ForwardAction"] = "Ctrl+."
        self.DefaultKeybindings["NewPageAction"] = "Ctrl+N"
        self.DefaultKeybindings["DeletePageAction"] = "Ctrl+D"
        self.DefaultKeybindings["MovePageUpAction"] = "Ctrl+PgUp"
        self.DefaultKeybindings["MovePageDownAction"] = "Ctrl+PgDown"
        self.DefaultKeybindings["PromotePageAction"] = "Ctrl+Shift+PgUp"
        self.DefaultKeybindings["DemotePageAction"] = "Ctrl+Shift+PgDown"
        self.DefaultKeybindings["MovePageToAction"] = "Ctrl+M"
        self.DefaultKeybindings["RenamePageAction"] = "Ctrl+R"
        self.DefaultKeybindings["ItalicsAction"] = "Ctrl+I"
        self.DefaultKeybindings["BoldAction"] = "Ctrl+B"
        self.DefaultKeybindings["HeaderOneAction"] = "Ctrl+1"
        self.DefaultKeybindings["HeaderTwoAction"] = "Ctrl+2"
        self.DefaultKeybindings["HeaderThreeAction"] = "Ctrl+3"
        self.DefaultKeybindings["HeaderFourAction"] = "Ctrl+4"
        self.DefaultKeybindings["HeaderFiveAction"] = "Ctrl+5"
        self.DefaultKeybindings["HeaderSixAction"] = "Ctrl+6"
        self.DefaultKeybindings["FootnoteAction"] = "Ctrl+T"
        self.DefaultKeybindings["InsertLinksAction"] = "Ctrl+L"
        self.DefaultKeybindings["InsertExternalLinkAction"] = "Ctrl+Shift+L"
        self.DefaultKeybindings["TextToLinkAction"] = "Ctrl+Alt+L"
        self.DefaultKeybindings["InsertTableAction"] = "Ctrl+Shift+T"
        self.DefaultKeybindings["InsertImageAction"] = "Ctrl+Shift+I"
        self.DefaultKeybindings["MoveLineUpAction"] = "Ctrl+Up"
        self.DefaultKeybindings["MoveLineDownAction"] = "Ctrl+Down"
        self.DefaultKeybindings["DuplicateLinesAction"] = "Ctrl+Shift+D"
        self.DefaultKeybindings["DeleteLineAction"] = "Ctrl+Shift+K"
        self.DefaultKeybindings["ZoomOutAction"] = "Ctrl+-"
        self.DefaultKeybindings["ZoomInAction"] = "Ctrl+="
        self.DefaultKeybindings["DefaultZoomAction"] = "Ctrl+0"
        self.DefaultKeybindings["SearchAction"] = "Ctrl+F"
        self.DefaultKeybindings["ToggleSearchAction"] = "Ctrl+Shift+F"
        self.DefaultKeybindings["AdvancedSearchAction"] = "Ctrl+Alt+F"
        self.DefaultKeybindings["PopOutPageAction"] = "Ctrl+P"
        self.DefaultKeybindings["GoToIndexPathAction"] = "Ctrl+G"

    def GetResourcePath(self, RelativeLocation):
        return os.path.join(self.AbsoluteDirectoryPath, RelativeLocation)

    def LoadConfigs(self):
        # Tool Bar Area
        ToolBarAreas = {}
        ToolBarAreas["LeftToolBarArea"] = Qt.ToolBarArea.LeftToolBarArea
        ToolBarAreas["RightToolBarArea"] = Qt.ToolBarArea.RightToolBarArea
        ToolBarAreas["TopToolBarArea"] = Qt.ToolBarArea.TopToolBarArea
        ToolBarAreas["BottomToolBarArea"] = Qt.ToolBarArea.BottomToolBarArea
        ToolBarAreaFile = self.GetResourcePath("Configs/ToolBarArea.cfg")
        if os.path.isfile(ToolBarAreaFile):
            with open(ToolBarAreaFile, "r") as ConfigFile:
                ToolBarArea = json.loads(ConfigFile.read())
        else:
            ToolBarArea = "TopToolBarArea"
        if ToolBarArea not in ToolBarAreas:
            ToolBarArea = "TopToolBarArea"
        self.removeToolBar(self.ToolBar)
        self.addToolBar(ToolBarAreas[ToolBarArea], self.ToolBar)
        self.ToolBar.show()

        # Favorites
        FavoritesFile = self.GetResourcePath("Configs/Favorites.cfg")
        if os.path.isfile(FavoritesFile):
            with open(FavoritesFile, "r") as ConfigFile:
                self.FavoritesData = json.loads(ConfigFile.read())
        else:
            self.FavoritesData = {}
        GzipFavoritesFile = self.GetResourcePath("Configs/GzipFavorites.cfg")
        if os.path.isfile(GzipFavoritesFile):
            with open(GzipFavoritesFile, "r") as ConfigFile:
                self.GzipFavoritesData = json.loads(ConfigFile.read())
        else:
            self.GzipFavoritesData = {}

        # Display Settings
        DisplaySettingsFile = self.GetResourcePath("Configs/DisplaySettings.cfg")
        if os.path.isfile(DisplaySettingsFile):
            with open(DisplaySettingsFile, "r") as ConfigFile:
                DisplaySettings = json.loads(ConfigFile.read())
            if "CurrentZoomLevel" in DisplaySettings:
                if DisplaySettings["CurrentZoomLevel"] > 0:
                    for ZoomLevel in range(DisplaySettings["CurrentZoomLevel"]):
                        self.ZoomIn()
                elif DisplaySettings["CurrentZoomLevel"] < 0:
                    for ZoomLevel in range(-DisplaySettings["CurrentZoomLevel"]):
                        self.ZoomOut()
            if "HorizontalSplit" in DisplaySettings:
                self.NotebookAndTextSplitter.setSizes(DisplaySettings["HorizontalSplit"])

        # Keybindings
        KeybindingsFile = self.GetResourcePath("Configs/Keybindings.cfg")
        if os.path.isfile(KeybindingsFile):
            with open(KeybindingsFile, "r") as ConfigFile:
                self.Keybindings = json.loads(ConfigFile.read())
        else:
            self.Keybindings = copy.deepcopy(self.DefaultKeybindings)
        for Action, Keybinding in self.DefaultKeybindings.items():
            if Action not in self.Keybindings:
                self.Keybindings[Action] = Keybinding
        InvalidBindings = []
        for Action in self.Keybindings.keys():
            if Action not in self.DefaultKeybindings:
                InvalidBindings.append(Action)
        for InvalidBinding in InvalidBindings:
            del self.Keybindings[InvalidBinding]
        for Action, Keybinding in self.Keybindings.items():
            getattr(self, Action).setShortcut(Keybinding)

        # Inline Footnote Style
        InlineFootnoteStyleFile = self.GetResourcePath("Configs/InlineFootnoteStyle.cfg")
        if os.path.isfile(InlineFootnoteStyleFile):
            with open(InlineFootnoteStyleFile, "r") as ConfigFile:
                self.InlineFootnoteStyle = json.loads(ConfigFile.read())
        else:
            self.InlineFootnoteStyle = True
        self.InlineFootnoteStyleAction.setChecked(self.InlineFootnoteStyle)

        # Show Hit Counts
        ShowHitCountsFile = self.GetResourcePath("Configs/ShowHitCounts.cfg")
        if os.path.isfile(ShowHitCountsFile):
            with open(ShowHitCountsFile, "r") as ConfigFile:
                self.ShowHitCounts = json.loads(ConfigFile.read())
        else:
            self.ShowHitCounts = False
        self.ShowHitCountsAction.setChecked(self.ShowHitCounts)

        # Swap Left and Middle Click for Links
        SwapLeftAndMiddleClickForLinksFile = self.GetResourcePath("Configs/SwapLeftAndMiddleClickForLinks.cfg")
        if os.path.isfile(SwapLeftAndMiddleClickForLinksFile):
            with open(SwapLeftAndMiddleClickForLinksFile, "r") as ConfigFile:
                self.SwapLeftAndMiddleClickForLinks = json.loads(ConfigFile.read())
        else:
            self.SwapLeftAndMiddleClickForLinks = False
        self.SwapLeftAndMiddleClickForLinksAction.setChecked(self.SwapLeftAndMiddleClickForLinks)

        # Move Cursor to End of Link Text
        MoveCursorToEndOfLinkTextFile = self.GetResourcePath("Configs/MoveCursorToEndOfLinkText.cfg")
        if os.path.isfile(MoveCursorToEndOfLinkTextFile):
            with open(MoveCursorToEndOfLinkTextFile, "r") as ConfigFile:
                self.MoveCursorToEndOfLinkText = json.loads(ConfigFile.read())
        else:
            self.MoveCursorToEndOfLinkText = True
        self.MoveCursorToEndOfLinkTextAction.setChecked(self.MoveCursorToEndOfLinkText)

        # Sort Ignores Blank Lines
        SortIgnoresBlankLinesFile = self.GetResourcePath("Configs/SortIgnoresBlankLines.cfg")
        if os.path.isfile(SortIgnoresBlankLinesFile):
            with open(SortIgnoresBlankLinesFile, "r") as ConfigFile:
                self.SortIgnoresBlankLines = json.loads(ConfigFile.read())
        else:
            self.SortIgnoresBlankLines = True
        self.SortIgnoresBlankLinesAction.setChecked(self.SortIgnoresBlankLines)

        # Highlight Syntax
        HighlightSyntaxFile = self.GetResourcePath("Configs/HighlightSyntax.cfg")
        if os.path.isfile(HighlightSyntaxFile):
            with open(HighlightSyntaxFile, "r") as ConfigFile:
                self.HighlightSyntax = json.loads(ConfigFile.read())
        else:
            self.HighlightSyntax = True
        self.HighlightSyntaxAction.setChecked(self.HighlightSyntax)

        # Highlight Text
        HighlightTextFile = self.GetResourcePath("Configs/HighlightText.cfg")
        if os.path.isfile(HighlightTextFile):
            with open(HighlightTextFile, "r") as ConfigFile:
                HighlightTextSettings = json.loads(ConfigFile.read())
                self.TextToHighlight = HighlightTextSettings["TextToHighlight"]
                self.TextToHighlightMatchCase = HighlightTextSettings["TextToHighlightMatchCase"]
        else:
            self.TextToHighlight = []
            self.TextToHighlightMatchCase = False

        # Search Highlight
        SearchHighlightFile = self.GetResourcePath("Configs/SearchHighlight.cfg")
        if os.path.isfile(SearchHighlightFile):
            with open(SearchHighlightFile, "r") as ConfigFile:
                self.SearchWidgetInst.HighlightCheckBox.setChecked(json.loads(ConfigFile.read()))

        # Advanced Search Highlight
        AdvancedSearchHighlightFile = self.GetResourcePath("Configs/AdvancedSearchHighlight.cfg")
        if os.path.isfile(AdvancedSearchHighlightFile):
            with open(AdvancedSearchHighlightFile, "r") as ConfigFile:
                self.AdvancedSearchHighlightText = json.loads(ConfigFile.read())

        # Highlight Pages
        HighlightPagesFile = self.GetResourcePath("Configs/HighlightPages.cfg")
        if os.path.isfile(HighlightPagesFile):
            with open(HighlightPagesFile, "r") as ConfigFile:
                self.SearchWidgetInst.HighlightPagesCheckBox.setChecked(json.loads(ConfigFile.read()))

        # Default Pop-Out Size
        DefaultPopOutSizeFile = self.GetResourcePath("Configs/DefaultPopOutSize.cfg")
        if os.path.isfile(DefaultPopOutSizeFile):
            with open(DefaultPopOutSizeFile, "r") as ConfigFile:
                self.DefaultPopOutSize = json.loads(ConfigFile.read())

        # Default Notebook
        DefaultNotebookFile = self.GetResourcePath("Configs/DefaultNotebook.cfg")
        if os.path.isfile(DefaultNotebookFile):
            with open(DefaultNotebookFile, "r") as ConfigFile:
                self.DefaultNotebook = json.loads(ConfigFile.read())
        else:
            self.DefaultNotebook = None
        GzipDefaultNotebookFile = self.GetResourcePath("Configs/GzipDefaultNotebook.cfg")
        if os.path.isfile(GzipDefaultNotebookFile):
            with open(GzipDefaultNotebookFile, "r") as ConfigFile:
                self.GzipDefaultNotebook = json.loads(ConfigFile.read())
        else:
            self.GzipDefaultNotebook = None

        # Size and Position
        SizeAndPositionFile = self.GetResourcePath("Configs/SizeAndPosition.cfg")
        if os.path.isfile(SizeAndPositionFile):
            with open(SizeAndPositionFile, "r") as ConfigFile:
                self.SizeAndPosition = json.loads(ConfigFile.read())
        else:
            self.SizeAndPosition = {}
            self.SizeAndPosition["Size"] = None
            self.SizeAndPosition["Position"] = None
            self.SizeAndPosition["SavedSizeAndPosition"] = False
        if self.SizeAndPosition["SavedSizeAndPosition"] and self.SizeAndPosition["Size"] is not None and self.SizeAndPosition["Position"] is not None:
            self.resize(self.SizeAndPosition["Size"][0], self.SizeAndPosition["Size"][1])
            self.move(self.SizeAndPosition["Position"][0], self.SizeAndPosition["Position"][1])

    def SaveConfigs(self):
        if not os.path.isdir(self.GetResourcePath("Configs")):
            os.mkdir(self.GetResourcePath("Configs"))

        # Tool Bar Area
        with open(self.GetResourcePath("Configs/ToolBarArea.cfg"), "w") as ConfigFile:
            ConfigFile.write(json.dumps(self.toolBarArea(self.ToolBar).name))

        # Favorites
        with open(self.GetResourcePath("Configs/Favorites.cfg"), "w") as ConfigFile:
            ConfigFile.write(json.dumps(self.FavoritesData, indent=2))
        with open(self.GetResourcePath("Configs/GzipFavorites.cfg"), "w") as ConfigFile:
            ConfigFile.write(json.dumps(self.GzipFavoritesData, indent=2))

        # Display Settings
        DisplaySettings = {}
        DisplaySettings["CurrentZoomLevel"] = self.CurrentZoomLevel
        DisplaySettings["HorizontalSplit"] = self.NotebookAndTextSplitter.sizes()
        with open(self.GetResourcePath("Configs/DisplaySettings.cfg"), "w") as ConfigFile:
            ConfigFile.write(json.dumps(DisplaySettings, indent=2))

        # Keybindings
        with open(self.GetResourcePath("Configs/Keybindings.cfg"), "w") as ConfigFile:
            ConfigFile.write(json.dumps(self.Keybindings, indent=2))

        # Inline Footnote Style
        with open(self.GetResourcePath("Configs/InlineFootnoteStyle.cfg"), "w") as ConfigFile:
            ConfigFile.write(json.dumps(self.InlineFootnoteStyle))

        # Show Hit Counts
        with open(self.GetResourcePath("Configs/ShowHitCounts.cfg"), "w") as ConfigFile:
            ConfigFile.write(json.dumps(self.ShowHitCounts))

        # Swap Left and Middle Click for Links
        with open(self.GetResourcePath("Configs/SwapLeftAndMiddleClickForLinks.cfg"), "w") as ConfigFile:
            ConfigFile.write(json.dumps(self.SwapLeftAndMiddleClickForLinks))

        # Move Cursor to End of Link Text
        with open(self.GetResourcePath("Configs/MoveCursorToEndOfLinkText.cfg"), "w") as ConfigFile:
            ConfigFile.write(json.dumps(self.MoveCursorToEndOfLinkText))

        # Sort Ignores Blank Lines
        with open(self.GetResourcePath("Configs/SortIgnoresBlankLines.cfg"), "w") as ConfigFile:
            ConfigFile.write(json.dumps(self.SortIgnoresBlankLines))

        # Highlight Syntax
        with open(self.GetResourcePath("Configs/HighlightSyntax.cfg"), "w") as ConfigFile:
            ConfigFile.write(json.dumps(self.HighlightSyntax))

        # Highlight Text
        HighlightTextSettings = {}
        HighlightTextSettings["TextToHighlight"] = self.TextToHighlight
        HighlightTextSettings["TextToHighlightMatchCase"] = self.TextToHighlightMatchCase
        with open(self.GetResourcePath("Configs/HighlightText.cfg"), "w") as ConfigFile:
            ConfigFile.write(json.dumps(HighlightTextSettings, indent=2))

        # Search Highlight
        with open(self.GetResourcePath("Configs/SearchHighlight.cfg"), "w") as ConfigFile:
            ConfigFile.write(json.dumps(self.SearchWidgetInst.HighlightCheckBox.isChecked()))

        # Advanced Search Highlight
        with open(self.GetResourcePath("Configs/AdvancedSearchHighlight.cfg"), "w") as ConfigFile:
            ConfigFile.write(json.dumps(self.AdvancedSearchHighlightText))

        # Highlight Pages
        with open(self.GetResourcePath("Configs/HighlightPages.cfg"), "w") as ConfigFile:
            ConfigFile.write(json.dumps(self.SearchWidgetInst.HighlightPagesCheckBox.isChecked()))

        # Default Pop-Out Size
        with open(self.GetResourcePath("Configs/DefaultPopOutSize.cfg"), "w") as ConfigFile:
            ConfigFile.write(json.dumps(self.DefaultPopOutSize))

        # Theme
        with open(self.GetResourcePath("Configs/Theme.cfg"), "w") as ConfigFile:
            ConfigFile.write(json.dumps(self.Theme))

        # Size and Position
        with open(self.GetResourcePath("Configs/SizeAndPosition.cfg"), "w") as ConfigFile:
            ConfigFile.write(json.dumps(self.SizeAndPosition))

        # Last Opened Directory
        self.SaveLastOpenedDirectory()

        # Gzip Mode
        self.SaveGzipMode()

        # Default Notebook
        with open(self.GetResourcePath("Configs/DefaultNotebook.cfg"), "w") as ConfigFile:
            ConfigFile.write(json.dumps(self.DefaultNotebook))
        with open(self.GetResourcePath("Configs/GzipDefaultNotebook.cfg"), "w") as ConfigFile:
            ConfigFile.write(json.dumps(self.GzipDefaultNotebook))

    # Notebook Methods
    def UpdateNotebook(self, Notebook):
        self.Notebook = Notebook
        self.NotebookDisplayWidgetInst.Notebook = self.Notebook
        self.TextWidgetInst.Notebook = self.Notebook
        self.TextWidgetInst.Renderer.Notebook = self.Notebook
        self.SearchWidgetInst.Notebook = self.Notebook
        self.PopOutMarkdownRenderer.Notebook = self.Notebook
        self.CloseAllPopOutPages()

    def PageSelected(self, IndexPath=None, SkipUpdatingBackAndForward=False):
        IndexPath = IndexPath if IndexPath is not None else self.NotebookDisplayWidgetInst.GetCurrentPageIndexPath()
        if IndexPath is not None:
            if not SkipUpdatingBackAndForward:
                self.UpdateBackAndForward()
            self.TextWidgetInst.SetCurrentPage(self.Notebook.GetPageFromIndexPath(IndexPath))
            self.NavigationBarInst.UpdateFromIndexPath(IndexPath)
            self.UpdateWindowTitle()

    def UpdateBackAndForward(self):
        if not self.BackNavigation and self.TextWidgetInst.ReadMode:
            PreviousPageIndexPath = self.TextWidgetInst.CurrentPage["IndexPath"]
            PreviousPageScrollPosition = self.TextWidgetInst.verticalScrollBar().value()
            PreviousPageScrollMaximum = self.TextWidgetInst.verticalScrollBar().maximum()
            PreviousPageData = (PreviousPageIndexPath, PreviousPageScrollPosition, PreviousPageScrollMaximum)
            if self.BackList != []:
                if self.BackList[-1][0] != PreviousPageIndexPath:
                    self.BackList.append(PreviousPageData)
            else:
                self.BackList.append(PreviousPageData)
            if len(self.BackList) > self.BackMaximum:
                self.BackList = self.BackList[-self.BackMaximum:]
            self.ForwardList.clear()
        self.BackAction.setEnabled(len(self.BackList) > 0 and self.TextWidgetInst.ReadMode)
        self.ForwardAction.setEnabled(len(self.ForwardList) > 0 and self.TextWidgetInst.ReadMode)

    def ClearBackAndForward(self):
        self.BackList.clear()
        self.ForwardList.clear()
        self.BackAction.setEnabled(len(self.BackList) > 0 and self.TextWidgetInst.ReadMode)
        self.ForwardAction.setEnabled(len(self.ForwardList) > 0 and self.TextWidgetInst.ReadMode)

    def Back(self):
        if len(self.BackList) > 0:
            self.BackNavigation = True
            TargetPageIndexPath = self.BackList[-1][0]
            TargetPageScrollPosition = self.BackList[-1][1]
            TargetPageScrollMaximum = self.BackList[-1][2]
            self.AutoScrollQueue = {}
            self.AutoScrollQueue["TargetScrollPosition"] = TargetPageScrollPosition
            self.AutoScrollQueue["ScrollBarMaximum"] = TargetPageScrollMaximum
            del self.BackList[-1]
            CurrentPageIndexPath = self.NotebookDisplayWidgetInst.GetCurrentPageIndexPath()
            CurrentPageScrollPosition = self.TextWidgetInst.verticalScrollBar().value()
            CurrentPageScrollMaximum = self.TextWidgetInst.verticalScrollBar().maximum()
            CurrentPageData = (CurrentPageIndexPath, CurrentPageScrollPosition, CurrentPageScrollMaximum)
            self.ForwardList.append(CurrentPageData)
            self.NotebookDisplayWidgetInst.SelectTreeItemFromIndexPath(TargetPageIndexPath)
            self.TextWidgetInst.verticalScrollBar().setValue(int(TargetPageScrollPosition))
            self.BackNavigation = False
            self.NotebookDisplayWidgetInst.setFocus()

    def Forward(self):
        if len(self.ForwardList) > 0:
            self.BackNavigation = True
            TargetPageIndexPath = self.ForwardList[-1][0]
            TargetPageScrollPosition = self.ForwardList[-1][1]
            TargetPageScrollMaximum = self.ForwardList[-1][2]
            self.AutoScrollQueue = {}
            self.AutoScrollQueue["TargetScrollPosition"] = TargetPageScrollPosition
            self.AutoScrollQueue["ScrollBarMaximum"] = TargetPageScrollMaximum
            del self.ForwardList[-1]
            CurrentPageIndexPath = self.NotebookDisplayWidgetInst.GetCurrentPageIndexPath()
            CurrentPageScrollPosition = self.TextWidgetInst.verticalScrollBar().value()
            CurrentPageScrollMaximum = self.TextWidgetInst.verticalScrollBar().maximum()
            CurrentPageData = (CurrentPageIndexPath, CurrentPageScrollPosition, CurrentPageScrollMaximum)
            self.BackList.append(CurrentPageData)
            self.NotebookDisplayWidgetInst.SelectTreeItemFromIndexPath(TargetPageIndexPath)
            self.TextWidgetInst.verticalScrollBar().setValue(int(TargetPageScrollPosition))
            self.BackNavigation = False
            self.NotebookDisplayWidgetInst.setFocus()

    def NewPage(self):
        if not self.TextWidgetInst.ReadMode:
            CurrentPageIndexPath = self.NotebookDisplayWidgetInst.GetCurrentPageIndexPath()
            CurrentPage = self.Notebook.GetPageFromIndexPath(CurrentPageIndexPath)
            NewPageDialogInst = NewPageDialog(CurrentPage["Title"], self.Notebook.GetTemplateNames(), self)
            if NewPageDialogInst.NewPageAdded:
                OldLinkData = self.GetLinkData()
                self.Notebook.AddSubPage(NewPageDialogInst.NewPageName, "" if NewPageDialogInst.TemplateName == "None" else self.Notebook.GetTemplate(NewPageDialogInst.TemplateName), CurrentPageIndexPath)
                NewLinkData = self.GetLinkData()
                self.UpdateLinks(OldLinkData, NewLinkData)
                self.NotebookDisplayWidgetInst.FillFromRootPage()
                self.NotebookDisplayWidgetInst.SelectTreeItemFromIndexPath(CurrentPageIndexPath, ScrollToLastChild=True)
                self.SearchWidgetInst.RefreshSearch()
                self.RefreshAdvancedSearch()
                self.UpdateUnsavedChangesFlag(True)
            self.NotebookDisplayWidgetInst.setFocus()

    def DeletePage(self):
        if not self.TextWidgetInst.ReadMode:
            CurrentPageIndexPath = self.NotebookDisplayWidgetInst.GetCurrentPageIndexPath()
            CurrentPage = self.Notebook.GetPageFromIndexPath(CurrentPageIndexPath)
            if CurrentPage["IndexPath"] == [0]:
                self.DisplayMessageBox("The root page of a notebook cannot be deleted.")
            elif self.DisplayMessageBox("Are you sure you want to delete this page?  This cannot be undone.", Icon=QMessageBox.Icon.Question, Buttons=(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)) == QMessageBox.StandardButton.Yes:
                self.RemoveDeletedPageFromAdvancedSearch(CurrentPage)
                OldLinkData = self.GetLinkData()
                self.Notebook.DeleteSubPage(CurrentPageIndexPath)
                self.CloseDeletedPopOutPages(CurrentPage)
                self.UpdateDeletedPageLinks(CurrentPage)
                NewLinkData = self.GetLinkData()
                self.UpdateLinks(OldLinkData, NewLinkData)
                self.NotebookDisplayWidgetInst.FillFromRootPage()
                SelectParent = False
                SelectDelta = 0
                CurrentPageSuperSubPagesLength = len(self.Notebook.GetSuperOfPageFromIndexPath(CurrentPageIndexPath)["SubPages"])
                if CurrentPageSuperSubPagesLength < 1:
                    SelectParent = True
                elif CurrentPageSuperSubPagesLength == CurrentPageIndexPath[-1]:
                    SelectDelta = -1
                self.NotebookDisplayWidgetInst.SelectTreeItemFromIndexPath(CurrentPageIndexPath, SelectParent=SelectParent, SelectDelta=SelectDelta)
                self.SearchWidgetInst.RefreshSearch()
                self.RefreshAdvancedSearch()
                self.UpdateUnsavedChangesFlag(True)
            self.NotebookDisplayWidgetInst.setFocus()

    def RenamePage(self):
        if not self.TextWidgetInst.ReadMode:
            CurrentPageIndexPath = self.NotebookDisplayWidgetInst.GetCurrentPageIndexPath()
            CurrentPage = self.Notebook.GetPageFromIndexPath(CurrentPageIndexPath)
            NewName, OK = QInputDialog.getText(self, f"Rename \"{CurrentPage["Title"]}\"", "Enter a title:", text=CurrentPage["Title"])
            if OK:
                if NewName == "":
                    self.DisplayMessageBox("Page names cannot be blank.")
                else:
                    OldLinkData = self.GetLinkData()
                    CurrentPage["Title"] = NewName
                    NewLinkData = self.GetLinkData()
                    self.UpdateLinks(OldLinkData, NewLinkData)
                    self.NotebookDisplayWidgetInst.FillFromRootPage()
                    self.NotebookDisplayWidgetInst.SelectTreeItemFromIndexPath(CurrentPageIndexPath)
                    self.SearchWidgetInst.RefreshSearch()
                    self.RefreshAdvancedSearch()
                    self.UpdateUnsavedChangesFlag(True)
            self.NotebookDisplayWidgetInst.setFocus()

    def AddSiblingPageBefore(self):
        if not self.TextWidgetInst.ReadMode:
            CurrentPageIndexPath = self.NotebookDisplayWidgetInst.GetCurrentPageIndexPath()
            CurrentPage = self.Notebook.GetPageFromIndexPath(CurrentPageIndexPath)
            if CurrentPage["IndexPath"] == [0]:
                self.DisplayMessageBox("The root page of a notebook cannot have sibling pages.")
            else:
                NewPageDialogInst = NewPageDialog(CurrentPage["Title"], self.Notebook.GetTemplateNames(), self, BeforeSibling=True)
                if NewPageDialogInst.NewPageAdded:
                    OldLinkData = self.GetLinkData()
                    self.Notebook.AddSiblingPageBefore(CurrentPageIndexPath, NewPageDialogInst.NewPageName, "" if NewPageDialogInst.TemplateName == "None" else self.Notebook.GetTemplate(NewPageDialogInst.TemplateName))
                    NewLinkData = self.GetLinkData()
                    self.UpdateLinks(OldLinkData, NewLinkData)
                    self.NotebookDisplayWidgetInst.FillFromRootPage()
                    self.NotebookDisplayWidgetInst.SelectTreeItemFromIndexPath(CurrentPageIndexPath)
                    self.SearchWidgetInst.RefreshSearch()
                    self.RefreshAdvancedSearch()
                    self.UpdateUnsavedChangesFlag(True)
                self.NotebookDisplayWidgetInst.setFocus()

    def MovePage(self, Delta):
        if not self.TextWidgetInst.ReadMode:
            CurrentPageIndexPath = self.NotebookDisplayWidgetInst.GetCurrentPageIndexPath()
            CurrentPage = self.Notebook.GetPageFromIndexPath(CurrentPageIndexPath)
            OldLinkData = self.GetLinkData()
            if CurrentPage["IndexPath"] == [0]:
                self.DisplayMessageBox("The root page of a notebook cannot be moved.")
            elif self.Notebook.MoveSubPage(CurrentPageIndexPath, Delta):
                NewLinkData = self.GetLinkData()
                self.UpdateLinks(OldLinkData, NewLinkData)
                self.NotebookDisplayWidgetInst.FillFromRootPage()
                self.NotebookDisplayWidgetInst.SelectTreeItemFromIndexPath(CurrentPageIndexPath, SelectDelta=Delta)
                self.SearchWidgetInst.RefreshSearch()
                self.RefreshAdvancedSearch()
                self.UpdateUnsavedChangesFlag(True)
            self.NotebookDisplayWidgetInst.setFocus()

    def PromotePage(self):
        if not self.TextWidgetInst.ReadMode:
            CurrentPageIndexPath = self.NotebookDisplayWidgetInst.GetCurrentPageIndexPath()
            SuperOfCurrentPageIndexPath = self.Notebook.GetSuperOfPageFromIndexPath(CurrentPageIndexPath)["IndexPath"]
            if CurrentPageIndexPath == [0]:
                self.DisplayMessageBox("The root page of a notebook cannot be promoted.")
            elif SuperOfCurrentPageIndexPath == [0]:
                self.DisplayMessageBox("A page cannot be promoted to the same level as the root page.")
            else:
                CurrentPage = self.Notebook.GetPageFromIndexPath(CurrentPageIndexPath)
                OldLinkData = self.GetLinkData()
                self.Notebook.PromoteSubPage(CurrentPageIndexPath)
                NewLinkData = self.GetLinkData()
                self.UpdateLinks(OldLinkData, NewLinkData)
                self.NotebookDisplayWidgetInst.FillFromRootPage()
                self.NotebookDisplayWidgetInst.SelectTreeItemFromIndexPath(CurrentPage["IndexPath"])
                self.SearchWidgetInst.RefreshSearch()
                self.RefreshAdvancedSearch()
                self.UpdateUnsavedChangesFlag(True)
            self.NotebookDisplayWidgetInst.setFocus()

    def DemotePage(self):
        if not self.TextWidgetInst.ReadMode:
            CurrentPageIndexPath = self.NotebookDisplayWidgetInst.GetCurrentPageIndexPath()
            SuperOfCurrentPage = self.Notebook.GetSuperOfPageFromIndexPath(CurrentPageIndexPath)
            if CurrentPageIndexPath == [0]:
                self.DisplayMessageBox("The root page of a notebook cannot be demoted.")
            elif len(SuperOfCurrentPage["SubPages"]) < 2:
                self.DisplayMessageBox("No valid page to demote to.")
            else:
                CurrentPage = self.Notebook.GetPageFromIndexPath(CurrentPageIndexPath)
                SiblingPages = SuperOfCurrentPage["SubPages"].copy()
                SiblingPages.remove(CurrentPage)
                SiblingPageTitles = [Sibling["Title"] for Sibling in SiblingPages]
                SiblingPageIndex = DemotePageDialog(CurrentPage, SiblingPageTitles, self).SiblingPageIndex
                if SiblingPageIndex is not None:
                    OldLinkData = self.GetLinkData()
                    self.Notebook.DemoteSubPage(CurrentPageIndexPath, SiblingPageIndex)
                    NewLinkData = self.GetLinkData()
                    self.UpdateLinks(OldLinkData, NewLinkData)
                    self.NotebookDisplayWidgetInst.FillFromRootPage()
                    self.NotebookDisplayWidgetInst.SelectTreeItemFromIndexPath(CurrentPage["IndexPath"])
                    self.SearchWidgetInst.RefreshSearch()
                    self.RefreshAdvancedSearch()
                    self.UpdateUnsavedChangesFlag(True)
            self.NotebookDisplayWidgetInst.setFocus()

    def PromoteAllSubPages(self):
        if not self.TextWidgetInst.ReadMode:
            CurrentPageIndexPath = self.NotebookDisplayWidgetInst.GetCurrentPageIndexPath()
            CurrentPage = self.Notebook.GetPageFromIndexPath(CurrentPageIndexPath)
            if CurrentPageIndexPath == [0]:
                self.DisplayMessageBox("Pages cannot be promoted to the same level as the root page.")
            elif len(CurrentPage["SubPages"]) == 0:
                self.DisplayMessageBox("This page has no sub pages.")
            else:
                OldLinkData = self.GetLinkData()
                self.Notebook.PromoteAllSubPages(CurrentPageIndexPath)
                NewLinkData = self.GetLinkData()
                self.UpdateLinks(OldLinkData, NewLinkData)
                self.NotebookDisplayWidgetInst.FillFromRootPage()
                self.NotebookDisplayWidgetInst.SelectTreeItemFromIndexPath(CurrentPageIndexPath)
                self.SearchWidgetInst.RefreshSearch()
                self.RefreshAdvancedSearch()
                self.UpdateUnsavedChangesFlag(True)
            self.NotebookDisplayWidgetInst.setFocus()

    def DemoteAllSiblingPages(self):
        if not self.TextWidgetInst.ReadMode:
            CurrentPageIndexPath = self.NotebookDisplayWidgetInst.GetCurrentPageIndexPath()
            SuperOfCurrentPage = self.Notebook.GetSuperOfPageFromIndexPath(CurrentPageIndexPath)
            if CurrentPageIndexPath == [0]:
                self.DisplayMessageBox("The root page of a notebook has no sibling pages.")
            elif len(SuperOfCurrentPage["SubPages"]) < 2:
                self.DisplayMessageBox("This page has no sibling pages.")
            else:
                CurrentPage = self.Notebook.GetPageFromIndexPath(CurrentPageIndexPath)
                OldLinkData = self.GetLinkData()
                self.Notebook.DemoteAllSiblingPages(CurrentPageIndexPath)
                NewLinkData = self.GetLinkData()
                self.UpdateLinks(OldLinkData, NewLinkData)
                self.NotebookDisplayWidgetInst.FillFromRootPage()
                self.NotebookDisplayWidgetInst.SelectTreeItemFromIndexPath(CurrentPage["IndexPath"])
                self.SearchWidgetInst.RefreshSearch()
                self.RefreshAdvancedSearch()
                self.UpdateUnsavedChangesFlag(True)
            self.NotebookDisplayWidgetInst.setFocus()

    def MovePageTo(self):
        if not self.TextWidgetInst.ReadMode:
            CurrentPageIndexPath = self.NotebookDisplayWidgetInst.GetCurrentPageIndexPath()
            if CurrentPageIndexPath == [0]:
                self.DisplayMessageBox("The root page of a notebook cannot be moved.")
            else:
                CurrentPage = self.Notebook.GetPageFromIndexPath(CurrentPageIndexPath)
                DestinationIndexPath = MovePageToDialog(CurrentPageIndexPath, self.Notebook, self).DestinationIndexPath
                if DestinationIndexPath is not None:
                    OldLinkData = self.GetLinkData()
                    self.Notebook.MoveSubPageTo(CurrentPageIndexPath, DestinationIndexPath)
                    NewLinkData = self.GetLinkData()
                    self.UpdateLinks(OldLinkData, NewLinkData)
                    self.NotebookDisplayWidgetInst.FillFromRootPage()
                    self.NotebookDisplayWidgetInst.SelectTreeItemFromIndexPath(CurrentPage["IndexPath"])
                    self.SearchWidgetInst.RefreshSearch()
                    self.RefreshAdvancedSearch()
                    self.UpdateUnsavedChangesFlag(True)
            self.NotebookDisplayWidgetInst.setFocus()

    def AlphabetizeSubPages(self):
        if not self.TextWidgetInst.ReadMode:
            CurrentPageIndexPath = self.NotebookDisplayWidgetInst.GetCurrentPageIndexPath()
            if len(self.Notebook.GetPageFromIndexPath(CurrentPageIndexPath)["SubPages"]) < 2:
                return
            OldLinkData = self.GetLinkData()
            self.Notebook.AlphabetizeSubPages(CurrentPageIndexPath)
            NewLinkData = self.GetLinkData()
            self.UpdateLinks(OldLinkData, NewLinkData)
            self.NotebookDisplayWidgetInst.FillFromRootPage()
            self.NotebookDisplayWidgetInst.SelectTreeItemFromIndexPath(CurrentPageIndexPath)
            self.SearchWidgetInst.RefreshSearch()
            self.RefreshAdvancedSearch()
            self.UpdateUnsavedChangesFlag(True)
            self.NotebookDisplayWidgetInst.setFocus()

    def CopyLinkToCurrentPage(self):
        IndexPathToCurrentPage = self.NotebookDisplayWidgetInst.GetCurrentPageIndexPath()
        IndexPathStringToCurrentPage = json.dumps(IndexPathToCurrentPage)
        CurrentPageTitle = self.Notebook.GetPageFromIndexPath(IndexPathToCurrentPage)["Title"]
        LinkToCurrentPage = f"[{CurrentPageTitle}]({IndexPathStringToCurrentPage} \"{CurrentPageTitle}\")"
        QApplication.clipboard().setText(LinkToCurrentPage)

    def CopyIndexPathToCurrentPage(self):
        IndexPathStringToCurrentPage = json.dumps(self.NotebookDisplayWidgetInst.GetCurrentPageIndexPath())
        QApplication.clipboard().setText(IndexPathStringToCurrentPage)

    def GetLinkData(self, Page=None):
        LinkData = {}
        Page = Page if Page is not None else self.Notebook.RootPage
        LinkData[id(Page)] = {"NoToolTip": f"]({json.dumps(Page["IndexPath"])})", "ToolTip": f"]({json.dumps(Page["IndexPath"])} \"{Page["Title"]}\")"}
        self.AddSubPageLinkData(Page, LinkData)
        return LinkData

    def AddSubPageLinkData(self, CurrentPage, LinkData):
        for SubPage in CurrentPage["SubPages"]:
            LinkData[id(SubPage)] = {"NoToolTip": f"]({json.dumps(SubPage["IndexPath"])})", "ToolTip": f"]({json.dumps(SubPage["IndexPath"])} \"{SubPage["Title"]}\")"}
            self.AddSubPageLinkData(SubPage, LinkData)

    def UpdateLinks(self, OldLinkData, NewLinkData, Page=None):
        ReplaceQueue = []
        for PageID in NewLinkData:
            if PageID in OldLinkData:
                if NewLinkData[PageID] != OldLinkData[PageID]:
                    ReplaceStrings = (OldLinkData[PageID]["NoToolTip"], f"<<LINK UPDATE TOKEN WITHOUT TOOL TIP {str(PageID)}>>", NewLinkData[PageID]["NoToolTip"])
                    ReplaceQueue.append(ReplaceStrings)
                    ReplaceStrings = (OldLinkData[PageID]["ToolTip"], f"<<LINK UPDATE TOKEN WITH TOOL TIP {str(PageID)}>>", NewLinkData[PageID]["ToolTip"])
                    ReplaceQueue.append(ReplaceStrings)
        for ReplaceStrings in ReplaceQueue:
            if Page is None:
                self.SearchWidgetInst.ReplaceAllInNotebook(SearchText=ReplaceStrings[0], ReplaceText=ReplaceStrings[1], MatchCase=True, DelayTextUpdate=True)
            else:
                self.SearchWidgetInst.ReplaceAllInPageAndSubPages(Page, SearchText=ReplaceStrings[0], ReplaceText=ReplaceStrings[1], MatchCase=True)
        for ReplaceStrings in ReplaceQueue:
            if Page is None:
                self.SearchWidgetInst.ReplaceAllInNotebook(SearchText=ReplaceStrings[1], ReplaceText=ReplaceStrings[2], MatchCase=True, DelayTextUpdate=True)
            else:
                self.SearchWidgetInst.ReplaceAllInPageAndSubPages(Page, SearchText=ReplaceStrings[1], ReplaceText=ReplaceStrings[2], MatchCase=True)

    def UpdateDeletedPageLinks(self, CurrentPage):
        CurrentPageLinkString = f"]({json.dumps(CurrentPage["IndexPath"])})"
        self.SearchWidgetInst.ReplaceAllInNotebook(CurrentPageLinkString, "]([deleted])", MatchCase=True, DelayTextUpdate=True)
        CurrentPageLinkString = f"]({json.dumps(CurrentPage["IndexPath"])} \"{CurrentPage["Title"]}\")"
        self.SearchWidgetInst.ReplaceAllInNotebook(CurrentPageLinkString, "]([deleted])", MatchCase=True, DelayTextUpdate=True)
        for SubPage in CurrentPage["SubPages"]:
            self.UpdateDeletedPageLinks(SubPage)

    def ImageManager(self, SearchImageName=None):
        ImageManagerDialogInst = ImageManagerDialog(self.Notebook, self, SearchImageName)
        if ImageManagerDialogInst.UnsavedChanges:
            self.UpdateUnsavedChangesFlag(True)
        if ImageManagerDialogInst.ActivatedLinkingPageIndexPath is not None:
            self.NotebookDisplayWidgetInst.SelectTreeItemFromIndexPath(ImageManagerDialogInst.ActivatedLinkingPageIndexPath)

    def TemplateManager(self):
        if not self.TextWidgetInst.ReadMode:
            TemplateManagerDialogInst = TemplateManagerDialog(self.Notebook, self)
            if TemplateManagerDialogInst.UnsavedChanges:
                self.UpdateUnsavedChangesFlag(True)

    def EditHeaderOrFooter(self, Mode):
        if not self.TextWidgetInst.ReadMode:
            EditHeaderOrFooterDialogInst = EditHeaderOrFooterDialog(Mode, self.Notebook, self)
            if EditHeaderOrFooterDialogInst.UnsavedChanges:
                if EditHeaderOrFooterDialogInst.Mode == "Header":
                    self.Notebook.Header = EditHeaderOrFooterDialogInst.HeaderOrFooterString
                elif EditHeaderOrFooterDialogInst.Mode == "Footer":
                    self.Notebook.Footer = EditHeaderOrFooterDialogInst.HeaderOrFooterString
                self.UpdateUnsavedChangesFlag(True)

    def SearchForLinkingPages(self):
        self.SearchAction.trigger()
        self.SearchWidgetInst.SearchTextLineEdit.setText(f"]({json.dumps(self.NotebookDisplayWidgetInst.GetCurrentPageIndexPath())}")
        self.SearchWidgetInst.SearchButton.click()

    def SearchForLinkedPages(self):
        SearchForLinkedPagesDialogInst = SearchForLinkedPagesDialog(self)
        if SearchForLinkedPagesDialogInst.DestinationIndexPath is not None:
            self.NotebookDisplayWidgetInst.SelectTreeItemFromIndexPath(SearchForLinkedPagesDialogInst.DestinationIndexPath)

    def AdvancedSearch(self):
        if self.AdvancedSearchDialogInst is None:
            self.AdvancedSearchDialogInst = AdvancedSearchDialog(self)
        else:
            self.AdvancedSearchDialogInst.activateWindow()
            self.AdvancedSearchDialogInst.raise_()
            self.AdvancedSearchDialogInst.setFocus()

    def ClearAdvancedSearch(self):
        if self.AdvancedSearchDialogInst is None:
            return
        self.AdvancedSearchDialogInst.ClearSearch()

    def RefreshAdvancedSearch(self):
        if self.AdvancedSearchDialogInst is None:
            return
        self.AdvancedSearchDialogInst.RefreshSearch()

    def RemoveDeletedPageFromAdvancedSearch(self, DeletedPage):
        if self.AdvancedSearchDialogInst is None:
            return
        if self.AdvancedSearchDialogInst.WithinPage is None:
            return
        if DeletedPage["IndexPath"] == self.AdvancedSearchDialogInst.WithinPage["IndexPath"][:len(DeletedPage["IndexPath"])]:
            self.AdvancedSearchDialogInst.ClearWithinPage()

    def GoToIndexPath(self):
        IndexPathString, OK = QInputDialog.getText(self, "Go to Page by Index Path", "Go to page by index path:")
        if OK:
            if self.Notebook.StringIsValidIndexPath(IndexPathString):
                self.NotebookDisplayWidgetInst.SelectTreeItemFromIndexPathString(IndexPathString)
            else:
                self.DisplayMessageBox("Not a valid index path.")

    # Text Methods
    def TextChanged(self):
        if self.TextWidgetInst.DisplayChanging or self.TextWidgetInst.ReadMode:
            return
        CurrentText = self.TextWidgetInst.toPlainText()
        if CurrentText != self.TextWidgetInst.CurrentPage["Content"]:
            self.TextWidgetInst.CurrentPage["Content"] = CurrentText
            self.Notebook.SearchIndexUpToDate = False
            self.UpdateUnsavedChangesFlag(True)

    def ToggleReadMode(self):
        self.TextWidgetInst.setFocus() if self.TextWidgetInst.ReadMode else self.NotebookDisplayWidgetInst.setFocus()
        self.TextWidgetInst.SetReadMode(not self.TextWidgetInst.ReadMode)
        for Action in self.ToggleReadModeActionsList:
            Action.setEnabled(not self.TextWidgetInst.ReadMode)
        self.ClearBackAndForward()

    def ZoomOut(self):
        self.TextWidgetInst.zoomOut(1)
        self.CurrentZoomLevel -= 1

    def ZoomIn(self):
        self.TextWidgetInst.zoomIn(1)
        self.CurrentZoomLevel += 1

    def DefaultZoom(self):
        if self.CurrentZoomLevel > 0:
            self.TextWidgetInst.zoomOut(self.CurrentZoomLevel)
            self.CurrentZoomLevel = 0
        elif self.CurrentZoomLevel < 0:
            self.TextWidgetInst.zoomIn(-self.CurrentZoomLevel)
            self.CurrentZoomLevel = 0

    def ToggleInlineFootnoteStyle(self):
        self.InlineFootnoteStyle = not self.InlineFootnoteStyle

    def ToggleShowHitCounts(self):
        self.ShowHitCounts = not self.ShowHitCounts
        self.SearchWidgetInst.RefreshSearch()
        self.RefreshAdvancedSearch()

    def ToggleSwapLeftAndMiddleClickForLinks(self):
        self.SwapLeftAndMiddleClickForLinks = not self.SwapLeftAndMiddleClickForLinks
        if self.SwapLeftAndMiddleClickForLinks:
            self.DisplayMessageBox("Left click and middle click for links have been swapped; double left click to open a pop-up of the linked page, and middle click to navigate to it.")
        else:
            self.DisplayMessageBox("Left click and middle click for links have been swapped; double left click to navigate to the linked page, and middle click to open a pop-up of it.")

    def ToggleMoveCursorToEndOfLinkText(self):
        self.MoveCursorToEndOfLinkText = not self.MoveCursorToEndOfLinkText
        if self.MoveCursorToEndOfLinkText:
            self.DisplayMessageBox("After inserting a link, the cursor will now move to the end of the text wrapped in the link.")
        else:
            self.DisplayMessageBox("After inserting a link, the cursor will now move to the end of the link itself.")

    def ToggleSortIgnoresBlankLines(self):
        self.SortIgnoresBlankLines = not self.SortIgnoresBlankLines

    def ToggleHighlightSyntax(self):
        self.HighlightSyntax = not self.HighlightSyntax
        if self.HighlightSyntax:
            self.DisplayMessageBox("Syntax highlighting is intended only as a rough guide, and may not capture all valid Markdown syntax perfectly.", Icon=QMessageBox.Icon.Warning)
        self.TextWidgetInst.SyntaxHighlighter.rehighlight()

    def HighlightText(self):
        HighlightTextDialogInst = HighlightTextDialog(self)
        self.TextWidgetInst.SyntaxHighlighter.rehighlight()

    def AddTextToPageAndSubpages(self, Prepend=False):
        if not self.TextWidgetInst.ReadMode:
            CurrentPageIndexPath = self.NotebookDisplayWidgetInst.GetCurrentPageIndexPath()
            CurrentPage = self.Notebook.GetPageFromIndexPath(CurrentPageIndexPath)
            Mode = "Prepend" if Prepend else "Append"
            AddToPageAndSubpagesDialogInst = AddToPageAndSubpagesDialog(Mode, self.Notebook, self)
            Text = AddToPageAndSubpagesDialogInst.TextToAdd
            if Text is not None:
                self.Notebook.AddTextToPageAndSubpages(Text, CurrentPage=CurrentPage, Prepend=Prepend)
                self.TextWidgetInst.UpdateText()
                self.SearchWidgetInst.RefreshSearch()
                self.RefreshAdvancedSearch()
                self.UpdateUnsavedChangesFlag(True)
                self.TextWidgetInst.setFocus()
                if not Prepend:
                    self.TextWidgetInst.moveCursor(QTextCursor.MoveOperation.End)

    def AddTitleToolTipsToLinks(self):
        if not self.TextWidgetInst.ReadMode:
            LinkData = self.GetLinkData()
            ReplaceQueue = []
            for PageID in LinkData:
                ReplaceStrings = (LinkData[PageID]["NoToolTip"], LinkData[PageID]["ToolTip"])
                ReplaceQueue.append(ReplaceStrings)
            for ReplaceStrings in ReplaceQueue:
                self.SearchWidgetInst.ReplaceAllInNotebook(SearchText=ReplaceStrings[0], ReplaceText=ReplaceStrings[1], MatchCase=True, DelayTextUpdate=True)
            self.TextWidgetInst.UpdateText()
            self.SearchWidgetInst.RefreshSearch()
            self.RefreshAdvancedSearch()
            self.UpdateUnsavedChangesFlag(True)

    # Interface Methods
    def DisplayMessageBox(self, Message, Icon=QMessageBox.Icon.Information, Buttons=QMessageBox.StandardButton.Ok, Parent=None):
        MessageBox = QMessageBox(self if Parent is None else Parent)
        MessageBox.setWindowIcon(self.WindowIcon)
        MessageBox.setWindowTitle(self.ScriptName)
        MessageBox.setIcon(Icon)
        MessageBox.setText(Message)
        MessageBox.setStandardButtons(Buttons)
        return MessageBox.exec()

    def FlashStatusBar(self, Status, Duration=2000):
        self.StatusBar.showMessage(Status)
        QTimer.singleShot(Duration, self.StatusBar.clearMessage)

    def UpdateWindowTitle(self):
        CurrentOpenFileNameString = f" - [{os.path.basename(self.CurrentOpenFileName)}]" if self.CurrentOpenFileName != "" else ""
        UnsavedChangesString = " *" if self.UnsavedChanges else ""
        self.setWindowTitle(f"{self.ScriptName}{CurrentOpenFileNameString} - \"{self.TextWidgetInst.CurrentPage["Title"]}\"{UnsavedChangesString}")

    def PopOutPage(self, IndexPath=None):
        Page = self.TextWidgetInst.CurrentPage if IndexPath is None else self.Notebook.GetPageFromIndexPath(IndexPath)
        for PopOut in self.PopOutPages:
            if Page is PopOut[0]:
                PopOut[1].activateWindow()
                PopOut[1].raise_()
                PopOut[1].setFocus()
                return
        NewPopOut = PopOutTextDialog(Page, self.Notebook, self.PopOutMarkdownParser, self)
        self.PopOutPages.append((Page, NewPopOut))

    def SetDefaultPopOutSize(self):
        DefaultPopOutSizeDialogInst = DefaultPopOutSizeDialog(self)
        if DefaultPopOutSizeDialogInst.SizeChanged:
            self.DefaultPopOutSize["Width"] = DefaultPopOutSizeDialogInst.Width
            self.DefaultPopOutSize["Height"] = DefaultPopOutSizeDialogInst.Height

    def CloseDeletedPopOutPages(self, Page):
        CloseQueue = []
        for PopOut in self.PopOutPages:
            if Page is PopOut[0]:
                CloseQueue.append(PopOut)
        for PopOut in CloseQueue:
            PopOut[1].close()
        for SubPage in Page["SubPages"]:
            self.CloseDeletedPopOutPages(SubPage)

    def CloseAllPopOutPages(self):
        CloseQueue = []
        for PopOut in self.PopOutPages:
            CloseQueue.append(PopOut)
        for PopOut in CloseQueue:
            PopOut[1].close()

    # Save and Open Methods
    def SaveActionTriggered(self, SaveAs=False):
        if self.Save(self.Notebook, SaveAs=SaveAs):
            self.Notebook.BuildSearchIndex()
            self.SearchWidgetInst.RefreshSearch()
            self.RefreshAdvancedSearch()
            self.UpdateUnsavedChangesFlag(False)
        else:
            self.UpdateWindowTitle()

    def OpenActionTriggered(self, FilePath=None):
        NewNotebook = self.Open(self.Notebook, FilePath=FilePath)
        if NewNotebook is not None:
            self.UpdateNotebook(NewNotebook)
            self.NotebookDisplayWidgetInst.FillFromRootPage()
            self.Notebook.BuildSearchIndex()
            self.SearchWidgetInst.ClearSearch()
            self.ClearAdvancedSearch()
            self.ClearBackAndForward()
            self.UpdateUnsavedChangesFlag(False)
        else:
            self.UpdateWindowTitle()

    def Favorites(self):
        FavoritesDialogInst = FavoritesDialog(self.FavoritesData if not self.GzipMode else self.GzipFavoritesData, self)
        if FavoritesDialogInst.OpenFilePath is not None:
            self.OpenActionTriggered(FavoritesDialogInst.OpenFilePath)

    def SetDefaultNotebook(self):
        SetDefaultNotebookDialog(self)

    def NewActionTriggered(self):
        if not self.New(self.Notebook):
            self.UpdateWindowTitle()
            return
        self.UpdateNotebook(Notebook())
        self.NotebookDisplayWidgetInst.FillFromRootPage()
        self.Notebook.BuildSearchIndex()
        self.SearchWidgetInst.ClearSearch()
        self.ClearAdvancedSearch()
        self.ClearBackAndForward()
        self.UpdateUnsavedChangesFlag(False)

    def ToggleGzipMode(self):
        self.GzipMode = not self.GzipMode

    def closeEvent(self, event):
        Close = True
        if self.UnsavedChanges:
            SavePrompt = self.DisplayMessageBox("Save unsaved work before closing?", Icon=QMessageBox.Icon.Warning, Buttons=(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel))
            if SavePrompt == QMessageBox.StandardButton.Yes:
                if not self.Save(self.Notebook):
                    Close = False
            elif SavePrompt == QMessageBox.StandardButton.No:
                pass
            elif SavePrompt == QMessageBox.StandardButton.Cancel:
                Close = False
        if not Close:
            event.ignore()
        else:
            self.SaveConfigs()
            event.accept()

    def UpdateUnsavedChangesFlag(self, UnsavedChanges):
        self.UnsavedChanges = UnsavedChanges
        self.UpdateWindowTitle()

    # Import and Export Methods
    def ExportHTML(self):
        AssetPaths = {}
        AssetPaths["TemplatePath"] = self.GetResourcePath("Assets/HTMLExportTemplate.template")
        AssetPaths["BackButtonPath"] = self.GetResourcePath("Assets/SnakeNotes Back Icon.png")
        AssetPaths["ForwardButtonPath"] = self.GetResourcePath("Assets/SnakeNotes Forward Icon.png")
        AssetPaths["ExpandButtonPath"] = self.GetResourcePath("Assets/SnakeNotes Expand All Icon.png")
        AssetPaths["CollapseButtonPath"] = self.GetResourcePath("Assets/SnakeNotes Collapse All Icon.png")
        HTMLText = ConstructHTMLExportString(self.Notebook, AssetPaths)
        self.Save(HTMLText, SaveAs=True, AlternateFileDescription="HTML", AlternateFileExtension=".html", SkipSerialization=True, ExportMode=True)

    def CreatePDFFileFromPage(self, Page, Notebook, ExportFileName):
        PDFWriter = QPdfWriter(ExportFileName)
        PDFWriter.setPageSize(QPageSize(QPageSize.PageSizeId.Letter))
        PDFTextWidget = QTextEdit()
        PDFTextWidget.setHtml(ConstructPDFExportHTMLString(Page, Notebook))
        PDFTextWidget.print(PDFWriter)
        PDFTextWidget.destroy()

    def ExportPageAsPDF(self):
        ExportFileName = QFileDialog.getSaveFileName(caption="Export PDF File", filter="PDF files (*.pdf)", directory=self.LastOpenedDirectory)[0]
        if ExportFileName != "":
            if not ExportFileName.endswith(".pdf"):
                ExportFileName += ".pdf"
            try:
                self.CreatePDFFileFromPage(self.TextWidgetInst.CurrentPage, self.Notebook, ExportFileName)
            except FileNotFoundError as Error:
                self.DisplayMessageBox(f"The page export failed with the following error:\n\n{str(Error)}\n\nThis is most likely due to the excessive length of the file paths needed.  Try exporting to a different location.")
                self.FlashStatusBar("Page not exported.")
                return
            ExportFileNameShort = os.path.basename(ExportFileName)
            self.FlashStatusBar(f"Page exported as:  \"{ExportFileNameShort}\"")
        else:
            self.FlashStatusBar("Page not exported.")

    def ExportNotebookAsPDFs(self):
        ExportFolderName = QFileDialog.getExistingDirectory(caption="Export Notebook as PDF Files", directory=self.LastOpenedDirectory)
        if ExportFolderName != "":
            if len(os.listdir(ExportFolderName)) > 0:
                self.DisplayMessageBox("Select an empty folder to export the entire notebook as PDF files.")
                self.FlashStatusBar("Notebook not exported.")
                return
            try:
                self.ExportNotebookPagesAsPDFs(self.Notebook.RootPage, ExportFolderName)
            except FileNotFoundError as Error:
                self.DisplayMessageBox(f"The notebook export failed with the following error:\n\n{str(Error)}\n\nThis is most likely due to the excessive length of the file paths needed.  Try exporting to a different location.")
                self.FlashStatusBar("Notebook not exported.")
                return
            ExportFolderNameShort = os.path.basename(ExportFolderName)
            self.FlashStatusBar(f"Notebook exported to:  \"{ExportFolderNameShort}\"")
        else:
            self.FlashStatusBar("Notebook not exported.")

    def ExportNotebookPagesAsPDFs(self, CurrentPage, CurrentFolderName):
        if not os.path.isdir(CurrentFolderName):
            os.mkdir(CurrentFolderName)
        PageFileName = os.path.join(CurrentFolderName, f"{str(CurrentPage["IndexPath"])} {CurrentPage["Title"]}.pdf")
        self.CreatePDFFileFromPage(CurrentPage, self.Notebook, PageFileName)
        SubPageFolderName = os.path.join(CurrentFolderName, f"{str(CurrentPage["IndexPath"])} {CurrentPage["Title"]}")
        for SubPage in CurrentPage["SubPages"]:
            self.ExportNotebookPagesAsPDFs(SubPage, SubPageFolderName)

    def ExportPage(self):
        self.Save(self.TextWidgetInst.CurrentPage, SaveAs=True, AlternateFileDescription="Page", AlternateFileExtension=".ntbkpg", ExportMode=True)

    def ImportPage(self):
        ImportedPage = self.Open(None, RespectUnsavedChanges=False, AlternateFileDescription="Page", AlternateFileExtension=".ntbkpg", ImportMode=True)
        if ImportedPage is not None:
            OldLinkData = self.GetLinkData(ImportedPage)
            self.Notebook.AddSubPage(PageToAdd=ImportedPage)
            NewLinkData = self.GetLinkData(ImportedPage)
            self.UpdateLinks(OldLinkData, NewLinkData, ImportedPage)
            self.NotebookDisplayWidgetInst.FillFromRootPage()
            self.NotebookDisplayWidgetInst.SelectTreeItemFromIndexPath(self.Notebook.RootPage["IndexPath"], ScrollToLastChild=True)
            self.SearchWidgetInst.RefreshSearch()
            self.RefreshAdvancedSearch()
            self.UpdateUnsavedChangesFlag(True)
            self.DisplayMessageBox("Check page links in imported pages carefully!  Some may point to unexpected pages.")

    # Window Management Methods
    def WindowSetup(self):
        self.setWindowIcon(self.WindowIcon)
        self.UpdateWindowTitle()
        self.Resize()
        self.Center()

    def Resize(self):
        ScreenGeometry = QApplication.primaryScreen().availableGeometry()
        Width = int(ScreenGeometry.width() * 0.5)
        Height = int(ScreenGeometry.height() * 0.75)
        self.resize(Width, Height)

    def Center(self):
        FrameGeometryRectangle = self.frameGeometry()
        DesktopCenterPoint = QApplication.primaryScreen().availableGeometry().center()
        FrameGeometryRectangle.moveCenter(DesktopCenterPoint)
        self.move(FrameGeometryRectangle.topLeft())

    def SetStartupSizeAndPosition(self):
        SetStartupSizeAndPosition = self.DisplayMessageBox(Message="Save current size and position for startup?", Icon=QMessageBox.Icon.Question, Buttons=(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Reset))
        if SetStartupSizeAndPosition == QMessageBox.StandardButton.Yes:
            self.SizeAndPosition = {}
            self.SizeAndPosition["Size"] = (self.width(), self.height())
            self.SizeAndPosition["Position"] = (self.pos().x(), self.pos().y())
            self.SizeAndPosition["SavedSizeAndPosition"] = True
        elif SetStartupSizeAndPosition == QMessageBox.StandardButton.Reset:
            self.SizeAndPosition = {}
            self.SizeAndPosition["Size"] = None
            self.SizeAndPosition["Position"] = None
            self.SizeAndPosition["SavedSizeAndPosition"] = False

    def CreateThemes(self):
        self.Themes = {}

        # Light
        self.Themes["Light"] = QPalette()
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, QColor(240, 240, 240, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(120, 120, 120, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, QColor(240, 240, 240, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.AlternateBase, QColor(247, 247, 247, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ToolTipBase, QColor(255, 255, 220, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ToolTipText, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.PlaceholderText, QColor(0, 0, 0, 128))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(120, 120, 120, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, QColor(240, 240, 240, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(120, 120, 120, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.BrightText, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Light, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Midlight, QColor(247, 247, 247, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Dark, QColor(160, 160, 160, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Mid, QColor(160, 160, 160, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Shadow, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight, QColor(0, 120, 215, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.HighlightedText, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Link, QColor(0, 0, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.LinkVisited, QColor(255, 0, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, QColor(240, 240, 240, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.AlternateBase, QColor(233, 231, 227, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipBase, QColor(255, 255, 220, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipText, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.PlaceholderText, QColor(0, 0, 0, 128))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, QColor(240, 240, 240, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.BrightText, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Light, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Midlight, QColor(227, 227, 227, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Dark, QColor(160, 160, 160, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Mid, QColor(160, 160, 160, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Shadow, QColor(105, 105, 105, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Highlight, QColor(0, 120, 215, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.HighlightedText, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Link, QColor(0, 0, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.LinkVisited, QColor(255, 0, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, QColor(240, 240, 240, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.AlternateBase, QColor(233, 231, 227, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ToolTipBase, QColor(255, 255, 220, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ToolTipText, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.PlaceholderText, QColor(0, 0, 0, 128))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, QColor(240, 240, 240, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.BrightText, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Light, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Midlight, QColor(227, 227, 227, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Dark, QColor(160, 160, 160, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Mid, QColor(160, 160, 160, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Shadow, QColor(105, 105, 105, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Highlight, QColor(240, 240, 240, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.HighlightedText, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Link, QColor(0, 0, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.LinkVisited, QColor(255, 0, 255, 255))

        # Dark
        self.Themes["Dark"] = QPalette()
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(98, 108, 118, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.AlternateBase, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ToolTipBase, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ToolTipText, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.PlaceholderText, QColor(239, 240, 241, 128))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(98, 108, 118, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(98, 108, 118, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.BrightText, QColor(255, 255, 255, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Light, QColor(24, 27, 29, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Midlight, QColor(36, 40, 44, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Dark, QColor(98, 108, 118, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Mid, QColor(65, 72, 78, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Shadow, QColor(0, 0, 0, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight, QColor(65, 72, 78, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.HighlightedText, QColor(36, 40, 44, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Link, QColor(41, 128, 185, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.LinkVisited, QColor(127, 140, 141, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, QColor(35, 38, 41, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.AlternateBase, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipBase, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipText, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.PlaceholderText, QColor(239, 240, 241, 128))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.BrightText, QColor(255, 255, 255, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Light, QColor(24, 27, 29, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Midlight, QColor(36, 40, 44, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Dark, QColor(98, 108, 118, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Mid, QColor(65, 72, 78, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Shadow, QColor(0, 0, 0, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Highlight, QColor(61, 174, 233, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.HighlightedText, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Link, QColor(41, 128, 185, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.LinkVisited, QColor(127, 140, 141, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, QColor(35, 38, 41, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.AlternateBase, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ToolTipBase, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ToolTipText, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.PlaceholderText, QColor(239, 240, 241, 128))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.BrightText, QColor(255, 255, 255, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Light, QColor(24, 27, 29, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Midlight, QColor(36, 40, 44, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Dark, QColor(98, 108, 118, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Mid, QColor(65, 72, 78, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Shadow, QColor(0, 0, 0, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Highlight, QColor(61, 174, 233, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.HighlightedText, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Link, QColor(41, 128, 185, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.LinkVisited, QColor(127, 140, 141, 255))

    def LoadTheme(self):
        self.CreateThemes()
        ThemeFile = self.GetResourcePath("Configs/Theme.cfg")
        if os.path.isfile(ThemeFile):
            with open(ThemeFile, "r") as ConfigFile:
                self.Theme = json.loads(ConfigFile.read())
        else:
            self.Theme = "Light"
        self.AppInst.setStyle("Fusion")
        self.AppInst.setPalette(self.Themes[self.Theme])

    def SetTheme(self):
        Themes = list(self.Themes.keys())
        Themes.sort()
        CurrentThemeIndex = Themes.index(self.Theme)
        Theme, OK = QInputDialog.getItem(self, "Set Theme", "Set theme (requires restart to take effect):", Themes, current=CurrentThemeIndex, editable=False)
        if OK:
            self.Theme = Theme
            self.DisplayMessageBox(f"The new theme will be active after {self.ScriptName} is restarted.")
