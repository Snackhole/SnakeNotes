import re

from PyQt5 import QtCore
from PyQt5.QtGui import QTextCursor, QTextDocument
from PyQt5.QtWidgets import QFrame, QLineEdit, QListWidget, QGridLayout, QListWidgetItem, QPushButton, QCheckBox


class SearchWidget(QFrame):
    def __init__(self, Notebook, MainWindow):
        super().__init__()

        # Store Parameters
        self.Notebook = Notebook
        self.MainWindow = MainWindow

        # Variables
        self.RefreshingSearchResults = False

        # Search Text Line Edit
        self.SearchTextLineEdit = SearchLineEdit(self)
        self.SearchTextLineEdit.setPlaceholderText("Search (Ctrl+F)")
        self.SearchTextLineEdit.returnPressed.connect(self.Search)

        # Match Case Check Box
        self.MatchCaseCheckBox = QCheckBox("Match Case")

        # Results List
        self.ResultsList = QListWidget()
        self.ResultsList.itemSelectionChanged.connect(self.SearchResultSelected)
        self.ResultsList.itemActivated.connect(self.SearchResultActivated)

        # Replace Text Line Edit
        self.ReplaceTextLineEdit = SearchLineEdit(self)
        self.ReplaceTextLineEdit.setPlaceholderText("Replace With")
        self.MainWindow.ToggleReadModeActionsList.append(self.ReplaceTextLineEdit)

        # Buttons
        self.SearchButton = QPushButton("Search Notebook")
        self.SearchButton.clicked.connect(self.Search)
        self.FindInPageButton = QPushButton("Find In Page")
        self.FindInPageButton.clicked.connect(self.FindInPage)
        self.ReplaceButton = QPushButton("Replace\nCurrent Hit")
        self.ReplaceButton.clicked.connect(self.Replace)
        self.MainWindow.ToggleReadModeActionsList.append(self.ReplaceButton)
        self.ReplaceAllInPageButton = QPushButton("Replace All\nIn Page")
        self.ReplaceAllInPageButton.clicked.connect(self.ReplaceAllInPage)
        self.MainWindow.ToggleReadModeActionsList.append(self.ReplaceAllInPageButton)
        self.ReplaceAllInNotebookButton = QPushButton("Replace All\nIn Notebook")
        self.ReplaceAllInNotebookButton.clicked.connect(lambda: self.ReplaceAllInNotebook())
        self.MainWindow.ToggleReadModeActionsList.append(self.ReplaceAllInNotebookButton)

        # Layout
        self.Layout = QGridLayout()
        self.Layout.addWidget(self.SearchTextLineEdit, 0, 0, 1, 3)
        self.Layout.addWidget(self.SearchButton, 1, 0)
        self.Layout.addWidget(self.FindInPageButton, 1, 1)
        self.Layout.addWidget(self.MatchCaseCheckBox, 1, 2)
        self.Layout.addWidget(self.ResultsList, 2, 0, 1, 3)
        self.Layout.addWidget(self.ReplaceTextLineEdit, 3, 0, 1, 3)
        self.Layout.addWidget(self.ReplaceButton, 4, 0)
        self.Layout.addWidget(self.ReplaceAllInPageButton, 4, 1)
        self.Layout.addWidget(self.ReplaceAllInNotebookButton, 4, 2)
        self.setLayout(self.Layout)

        # Start Invisible
        self.setVisible(False)

    def Search(self):
        SearchText = self.SearchTextLineEdit.text()
        MatchCase = self.MatchCaseCheckBox.isChecked()
        self.ResultsList.clear()
        if SearchText == "":
            return
        Results = self.Notebook.GetSearchResults(SearchText, MatchCase=MatchCase)
        for Result in Results:
            self.ResultsList.addItem(SearchResult(Result[0], Result[1]))
        self.ResultsList.setCurrentIndex(self.ResultsList.model().index(0))
        if not self.RefreshingSearchResults:
            self.ResultsList.setFocus()

    def SearchResultSelected(self):
        SelectedItems = self.ResultsList.selectedItems()
        if len(SelectedItems) > 0 and not self.RefreshingSearchResults:
            SelectedItem = SelectedItems[0]
            if self.MainWindow.NotebookDisplayWidgetInst.GetCurrentPageIndexPath() != SelectedItem.IndexPath:
                self.MainWindow.NotebookDisplayWidgetInst.SelectTreeItemFromIndexPath(SelectedItem.IndexPath)

    def SearchResultActivated(self):
        self.SearchResultSelected()
        self.FindInPage()

    def FindInPage(self):
        SearchText = self.SearchTextLineEdit.text()
        MatchCase = self.MatchCaseCheckBox.isChecked()
        if MatchCase:
            if not self.MainWindow.TextWidgetInst.find(SearchText, QTextDocument.FindCaseSensitively):
                self.MainWindow.TextWidgetInst.moveCursor(QTextCursor.Start)
                self.MainWindow.TextWidgetInst.find(SearchText, QTextDocument.FindCaseSensitively)
        else:
            if not self.MainWindow.TextWidgetInst.find(SearchText):
                self.MainWindow.TextWidgetInst.moveCursor(QTextCursor.Start)
                self.MainWindow.TextWidgetInst.find(SearchText)

    def Replace(self):
        if not self.MainWindow.TextWidgetInst.ReadMode:
            SearchText = self.SearchTextLineEdit.text()
            if SearchText == "":
                return
            ReplaceText = self.ReplaceTextLineEdit.text()
            Cursor = self.MainWindow.TextWidgetInst.textCursor()
            CurrentHitText = Cursor.selectedText()
            MatchCase = self.MatchCaseCheckBox.isChecked()
            if not MatchCase:
                SearchText = SearchText.casefold()
                CurrentHitText = CurrentHitText.casefold()
            if SearchText == CurrentHitText:
                self.MainWindow.TextWidgetInst.insertPlainText(ReplaceText)
            self.FindInPage()
            self.RefreshSearch()

    def ReplaceAllInPage(self):
        if not self.MainWindow.TextWidgetInst.ReadMode:
            SearchText = self.SearchTextLineEdit.text()
            if SearchText == "":
                return
            ReplaceText = self.ReplaceTextLineEdit.text()
            MatchCase = self.MatchCaseCheckBox.isChecked()
            PageText = self.MainWindow.TextWidgetInst.toPlainText()
            if MatchCase:
                PageText = PageText.replace(SearchText, ReplaceText)
            else:
                PageText = re.sub(re.escape(SearchText), lambda x: ReplaceText, PageText, flags=re.IGNORECASE)
            self.MainWindow.TextWidgetInst.setPlainText(PageText)
            self.RefreshSearch()

    def ReplaceAllInNotebook(self, SearchText=None, ReplaceText=None, MatchCase=None, DelayTextUpdate=False):
        if not self.MainWindow.TextWidgetInst.ReadMode:
            if SearchText is None:
                SearchText = self.SearchTextLineEdit.text()
            if SearchText == "":
                return
            if ReplaceText is None:
                ReplaceText = self.ReplaceTextLineEdit.text()
            if MatchCase is None:
                MatchCase = self.MatchCaseCheckBox.isChecked()
            self.ReplaceAllInPageAndSubPages(self.Notebook.RootPage, SearchText, ReplaceText, MatchCase)
            if not DelayTextUpdate:
                self.MainWindow.TextWidgetInst.UpdateText()
                self.MainWindow.UpdateUnsavedChangesFlag(True)
            self.RefreshSearch()

    def ReplaceAllInPageAndSubPages(self, CurrentPage, SearchText, ReplaceText, MatchCase):
        if MatchCase:
            CurrentPage["Content"] = CurrentPage["Content"].replace(SearchText, ReplaceText)
        else:
            CurrentPage["Content"] = re.sub(re.escape(SearchText), lambda x: ReplaceText, CurrentPage["Content"], flags=re.IGNORECASE)
        for SubPage in CurrentPage["SubPages"]:
            self.ReplaceAllInPageAndSubPages(SubPage, SearchText, ReplaceText, MatchCase)

    def ClearSearch(self):
        self.SearchTextLineEdit.clear()
        self.ReplaceTextLineEdit.clear()
        self.MatchCaseCheckBox.setChecked(False)
        self.ResultsList.clear()

    def NewSearch(self):
        self.SearchTextLineEdit.setFocus()
        self.SearchTextLineEdit.selectAll()

    def RefreshSearch(self):
        self.RefreshingSearchResults = True
        self.Notebook.SearchIndexUpToDate = False
        self.Search()
        self.RefreshingSearchResults = False

    def ToggleVisibility(self):
        VisibleState = self.isVisible()
        self.setVisible(not VisibleState)
        self.setEnabled(not VisibleState)

    def GrabFocus(self):
        if not self.isVisible():
            self.ToggleVisibility()
        self.NewSearch()


class SearchResult(QListWidgetItem):
    def __init__(self, Title, IndexPath):
        super().__init__()

        # Store Parameters
        self.Title = Title
        self.IndexPath = IndexPath

        # Set Text
        self.setText(self.Title)


class SearchLineEdit(QLineEdit):
    def __init__(self, SearchWidget):
        # QLineEdit Init
        super().__init__()

        # Store Parameters
        self.SearchWidget = SearchWidget

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == QtCore.Qt.Key_Escape:
            self.SearchWidget.ClearSearch()
        else:
            super().keyPressEvent(QKeyEvent)
