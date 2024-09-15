import mistune
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QDialog, QHeaderView, QTextEdit, QPushButton, QCheckBox, QGridLayout, QLineEdit, QTreeWidget, QTreeWidgetItem

from Core import MarkdownRenderers


class MovePageToDialog(QDialog):
    def __init__(self, CurrentPageIndexPath, Notebook, MainWindow):
        # Store Parameters
        self.CurrentPageIndexPath = CurrentPageIndexPath
        self.Notebook = Notebook
        self.MainWindow = MainWindow

        # Create Markdown Parser
        self.Renderer = MarkdownRenderers.Renderer(self.Notebook)
        self.MarkdownParser = mistune.Markdown(renderer=self.Renderer)

        # QDialog Init
        super().__init__(parent=self.MainWindow)

        # Variables
        self.DestinationIndexPath = None
        self.Width = max(self.MainWindow.width() - 100, 100)
        self.Height = max(self.MainWindow.height() - 100, 100)

        # Search Line Edit
        self.SearchLineEdit = SearchLineEdit(self)
        self.SearchLineEdit.setPlaceholderText("Search")
        self.SearchLineEdit.textChanged.connect(self.PopulateNotebookDisplay)
        self.SearchLineEdit.setFocus()

        # Match Case Check Box
        self.MatchCaseCheckBox = QCheckBox("Match Case")
        self.MatchCaseCheckBox.stateChanged.connect(self.PopulateNotebookDisplay)

        # Notebook Display
        self.NotebookDisplay = NotebookDisplay(self)
        self.NotebookDisplay.setHeaderHidden(True)
        self.NotebookDisplay.header().setStretchLastSection(False)
        self.NotebookDisplay.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.NotebookDisplay.itemSelectionChanged.connect(self.UpdatePreview)

        # Preview Text Edit
        self.PreviewTextEdit = QTextEdit()
        self.PreviewTextEdit.setReadOnly(True)

        # Buttons
        self.MoveButton = QPushButton("Move")
        self.MoveButton.clicked.connect(self.Move)
        self.CancelButton = QPushButton("Cancel")
        self.CancelButton.clicked.connect(self.Cancel)

        # Create, Populate, and Set Layout
        self.Layout = QGridLayout()
        self.SearchLayout = QGridLayout()
        self.SearchLayout.addWidget(self.SearchLineEdit, 0, 0)
        self.SearchLayout.addWidget(self.MatchCaseCheckBox, 0, 1)
        self.Layout.addLayout(self.SearchLayout, 0, 0)
        self.NotebookDisplayLayout = QGridLayout()
        self.NotebookDisplayLayout.addWidget(self.NotebookDisplay, 0, 0)
        self.NotebookDisplayLayout.addWidget(self.PreviewTextEdit, 0, 1)
        self.NotebookDisplayLayout.setColumnStretch(1, 1)
        self.Layout.addLayout(self.NotebookDisplayLayout, 1, 0)
        self.ButtonsLayout = QGridLayout()
        self.ButtonsLayout.addWidget(self.MoveButton, 0, 0)
        self.ButtonsLayout.addWidget(self.CancelButton, 0, 1)
        self.Layout.addLayout(self.ButtonsLayout, 2, 0)
        self.setLayout(self.Layout)

        # Set Window Title and Icon
        self.setWindowTitle(f"Move Page \"{self.Notebook.GetPageFromIndexPath(self.CurrentPageIndexPath)["Title"]}\" To...")
        self.setWindowIcon(self.MainWindow.WindowIcon)

        # Window Resize
        self.Resize()

        # Populate Notebook Display
        self.PopulateNotebookDisplay()

        # Execute Dialog
        self.exec_()

    def Move(self):
        SelectedItems = self.NotebookDisplay.selectedItems()
        if len(SelectedItems) < 1:
            return
        SelectedItem = SelectedItems[0]
        if SelectedItem.IsInvalidTarget or SelectedItem.IsPageToMove:
            self.MainWindow.DisplayMessageBox("The selected destination is invalid.", Parent=self)
            return
        self.DestinationIndexPath = SelectedItem.IndexPath
        self.close()

    def Cancel(self):
        self.close()

    def PopulateNotebookDisplay(self):
        SearchTerm = self.SearchLineEdit.text()
        self.NotebookDisplay.clear()
        if SearchTerm == "":
            self.NotebookDisplay.setRootIsDecorated(True)
            self.FillNotebookWidgetItem(self.NotebookDisplay.invisibleRootItem(), self.Notebook.RootPage, self.CurrentPageIndexPath[:-1] == [0], False, IsRootPage=True)
        else:
            MatchCase = self.MatchCaseCheckBox.isChecked()
            SearchResults = self.Notebook.GetSearchResults(SearchTerm, MatchCase=MatchCase)
            self.NotebookDisplay.setRootIsDecorated(False)
            self.FillNotebookWidgetItemFromSearchResults(SearchResults)

    def FillNotebookWidgetItem(self, CurrentTreeItem, CurrentPage, IsInvalidTarget, IsPageToMove, IsRootPage=False):
        ChildTreeItem = NotebookDisplayItem(CurrentPage["Title"], CurrentPage["IndexPath"], IsInvalidTarget, IsPageToMove)
        CurrentTreeItem.addChild(ChildTreeItem)

        for SubPage in CurrentPage["SubPages"]:
            self.FillNotebookWidgetItem(ChildTreeItem, SubPage, SubPage["IndexPath"][:len(self.CurrentPageIndexPath)] == self.CurrentPageIndexPath or SubPage["IndexPath"] == self.CurrentPageIndexPath[:-1], SubPage["IndexPath"] == self.CurrentPageIndexPath)

        if IsRootPage:
            ChildTreeItem.setExpanded(True)
            self.NotebookDisplay.setCurrentIndex(self.NotebookDisplay.model().index(0, 0))

    def FillNotebookWidgetItemFromSearchResults(self, SearchResults):
        for Result in SearchResults["ResultsList"]:
            ChildTreeItem = NotebookDisplayItem(Result[0], Result[1], Result[1][:len(self.CurrentPageIndexPath)] == self.CurrentPageIndexPath or Result[1] == self.CurrentPageIndexPath[:-1], Result[1] == self.CurrentPageIndexPath)
            self.NotebookDisplay.invisibleRootItem().addChild(ChildTreeItem)
        self.NotebookDisplay.setCurrentIndex(self.NotebookDisplay.model().index(0, 0))

    def UpdatePreview(self):
        self.PreviewTextEdit.clear()
        SelectedItems = self.NotebookDisplay.selectedItems()
        if len(SelectedItems) < 1:
            return
        SelectedItem = SelectedItems[0]
        CurrentPage = self.Notebook.GetPageFromIndexPath(SelectedItem.IndexPath)
        DisplayText = MarkdownRenderers.ConstructMarkdownStringFromPage(CurrentPage, self.Notebook)
        HTMLText = self.MarkdownParser(DisplayText)
        self.PreviewTextEdit.setHtml(HTMLText)

    def Resize(self):
        self.resize(self.Width, self.Height)


class NotebookDisplayItem(QTreeWidgetItem):
    def __init__(self, Title, IndexPath, IsInvalidTarget, IsPageToMove):
        super().__init__()

        # Store Parameters
        self.Title = Title
        self.IndexPath = IndexPath
        self.IsInvalidTarget = IsInvalidTarget
        self.IsPageToMove = IsPageToMove

        # Set Text
        self.setText(0, Title)

        # Set Background
        if self.IsPageToMove:
            self.setBackground(0, QColor("darkblue"))
            self.setForeground(0, QColor("white"))
        elif self.IsInvalidTarget:
            self.setBackground(0, QColor("darkred"))
            self.setForeground(0, QColor("white"))


class SearchLineEdit(QLineEdit):
    def __init__(self, Dialog):
        # QLineEdit Init
        super().__init__()

        # Store Parameters
        self.Dialog = Dialog

    def keyPressEvent(self, QKeyEvent):
        KeyPressed = QKeyEvent.key()
        if KeyPressed == Qt.Key_Down:
            self.Dialog.NotebookDisplay.setFocus()
        else:
            super().keyPressEvent(QKeyEvent)


class NotebookDisplay(QTreeWidget):
    def __init__(self, Dialog):
        # QTreeWidget Init
        super().__init__()

        # Store Parameters
        self.Dialog = Dialog

    def keyPressEvent(self, QKeyEvent):
        KeyPressed = QKeyEvent.key()
        ItemBefore = self.currentItem()
        super().keyPressEvent(QKeyEvent)
        ItemAfter = self.currentItem()
        if ItemBefore == ItemAfter and KeyPressed == Qt.Key_Up:
            self.Dialog.SearchLineEdit.setFocus()
