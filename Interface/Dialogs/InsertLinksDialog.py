import mistune
from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QLineEdit, QTextEdit, QTreeWidget, QHeaderView, QTreeWidgetItem, QGridLayout, QPushButton, QCheckBox, QLabel, QComboBox

from Core import MarkdownRenderers


class InsertLinksDialog(QDialog):
    def __init__(self, Notebook, MainWindow, Parent):
        # Store Parameters
        self.Notebook = Notebook
        self.MainWindow = MainWindow
        self.Parent = Parent

        # Create Markdown Parser
        self.Renderer = MarkdownRenderers.Renderer(self.Notebook)
        self.MarkdownParser = mistune.Markdown(renderer=self.Renderer)

        # QDialog Init
        super().__init__(parent=self.Parent)

        # Variables
        self.InsertAccepted = False
        self.InsertSubPageLinks = False
        self.SubPageLinksSeparator = None
        self.InsertIndexPath = None
        self.InsertIndexPaths = None
        self.Separators = {}
        self.Separators["Paragraph"] = "\n\n"
        self.Separators["New Line"] = "  \n"
        self.Width = max(self.Parent.width() - 100, 100)
        self.Height = max(self.Parent.height() - 100, 100)

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

        # Insert Sub Page Links Check Box
        self.InsertSubPageLinksCheckBox = QCheckBox("Insert Sub Page Links")

        # Sub Page Links Separator
        self.SubPageLinksSeparatorLabel = QLabel("Sub Page Links Separator:  ")
        self.SubPageLinksSeparatorComboBox = QComboBox()
        self.SubPageLinksSeparatorComboBox.addItems(["Paragraph", "New Line"])
        self.SubPageLinksSeparatorComboBox.setEditable(False)

        # Buttons
        self.InsertButton = QPushButton("Insert")
        self.InsertButton.clicked.connect(self.Insert)
        self.CancelButton = QPushButton("Cancel")
        self.CancelButton.clicked.connect(self.Cancel)

        # Create, Populate, and Set Layout
        self.Layout = QGridLayout()
        self.SearchLayout = QGridLayout()
        self.SearchLayout.addWidget(self.SearchLineEdit, 0, 0)
        self.SearchLayout.addWidget(self.MatchCaseCheckBox, 0, 1)
        self.Layout.addLayout(self.SearchLayout, 0, 0, 1, 3)
        self.NotebookDisplayLayout = QGridLayout()
        self.NotebookDisplayLayout.addWidget(self.NotebookDisplay, 0, 0)
        self.NotebookDisplayLayout.addWidget(self.PreviewTextEdit, 0, 1)
        self.NotebookDisplayLayout.setColumnStretch(1, 1)
        self.Layout.addLayout(self.NotebookDisplayLayout, 1, 0, 1, 3)
        self.Layout.addWidget(self.InsertSubPageLinksCheckBox, 2, 0)
        self.Layout.addWidget(self.SubPageLinksSeparatorLabel, 2, 1)
        self.Layout.addWidget(self.SubPageLinksSeparatorComboBox, 2, 2)
        self.ButtonsLayout = QGridLayout()
        self.ButtonsLayout.addWidget(self.InsertButton, 0, 0)
        self.ButtonsLayout.addWidget(self.CancelButton, 0, 1)
        self.Layout.addLayout(self.ButtonsLayout, 3, 0, 1, 3)
        self.setLayout(self.Layout)

        # Set Window Title and Icon
        self.setWindowTitle("Insert Link(s)")
        self.setWindowIcon(self.MainWindow.WindowIcon)

        # Window Resize
        self.Resize()

        # Populate Notebook Display
        self.PopulateNotebookDisplay()

        # Execute Dialog
        self.exec_()

    def Insert(self):
        SelectedItems = self.NotebookDisplay.selectedItems()
        if len(SelectedItems) < 1:
            return
        self.InsertSubPageLinks = self.InsertSubPageLinksCheckBox.isChecked()
        if self.InsertSubPageLinks:
            self.InsertIndexPaths = SelectedItems[0].SubPageIndexPaths
            self.SubPageLinksSeparator = self.Separators[self.SubPageLinksSeparatorComboBox.currentText()]
        else:
            self.InsertIndexPath = SelectedItems[0].IndexPath
        self.InsertAccepted = True
        self.close()

    def Cancel(self):
        self.close()

    def PopulateNotebookDisplay(self):
        SearchTerm = self.SearchLineEdit.text()
        self.NotebookDisplay.clear()
        if SearchTerm == "":
            self.FillNotebookWidgetItem(self.NotebookDisplay.invisibleRootItem(), self.Notebook.RootPage, IsRootPage=True)
        else:
            MatchCase = self.MatchCaseCheckBox.isChecked()
            SearchResults = self.Notebook.GetSearchResults(SearchTerm, MatchCase=MatchCase)
            self.FillNotebookWidgetItemFromSearchResults(SearchResults)

    def FillNotebookWidgetItem(self, CurrentTreeItem, CurrentPage, IsRootPage=False):
        SubPageIndexPaths = []
        for SubPage in CurrentPage["SubPages"]:
            SubPageIndexPaths.append((SubPage["Title"], SubPage["IndexPath"]))

        ChildTreeItem = NotebookDisplayItem(CurrentPage["Title"], CurrentPage["IndexPath"], SubPageIndexPaths)
        CurrentTreeItem.addChild(ChildTreeItem)

        for SubPage in CurrentPage["SubPages"]:
            self.FillNotebookWidgetItem(ChildTreeItem, SubPage)

        if IsRootPage:
            ChildTreeItem.setExpanded(True)
            self.NotebookDisplay.setCurrentIndex(self.NotebookDisplay.model().index(0, 0))

    def FillNotebookWidgetItemFromSearchResults(self, SearchResults):
        for Result in SearchResults:
            CurrentPage = self.Notebook.GetPageFromIndexPath(Result[1])
            SubPageIndexPaths = []
            for SubPage in CurrentPage["SubPages"]:
                SubPageIndexPaths.append((SubPage["Title"], SubPage["IndexPath"]))
            ChildTreeItem = NotebookDisplayItem(Result[0], Result[1], SubPageIndexPaths)
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
    def __init__(self, Title, IndexPath, SubPageIndexPaths):
        super().__init__()
        self.setText(0, Title)
        self.IndexPath = IndexPath
        self.SubPageIndexPaths = SubPageIndexPaths


class SearchLineEdit(QLineEdit):
    def __init__(self, Dialog):
        # QLineEdit Init
        super().__init__()

        # Store Parameters
        self.Dialog = Dialog

    def keyPressEvent(self, QKeyEvent):
        KeyPressed = QKeyEvent.key()
        if KeyPressed == QtCore.Qt.Key_Down:
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
        if ItemBefore == ItemAfter and KeyPressed == QtCore.Qt.Key_Up:
            self.Dialog.SearchLineEdit.setFocus()
