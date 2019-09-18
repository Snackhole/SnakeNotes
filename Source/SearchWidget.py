import re

from PyQt5 import QtCore
from PyQt5.QtGui import QTextCursor, QTextDocument
from PyQt5.QtWidgets import QFrame, QLineEdit, QListWidget, QGridLayout, QListWidgetItem, QPushButton, QCheckBox


class SearchWidget(QFrame):
    def __init__(self, RootPage, SearchIndexer, NotebookDisplayWidget, TextWidget, MainWindow):
        super().__init__()

        # Store Parameters
        self.RootPage = RootPage
        self.SearchIndexer = SearchIndexer
        self.NotebookDisplayWidget = NotebookDisplayWidget
        self.TextWidget = TextWidget
        self.MainWindow = MainWindow
        self.ToggleReadModeActionsList = self.MainWindow.ToggleReadModeActionsList

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
        self.ToggleReadModeActionsList.append(self.ReplaceTextLineEdit)

        # Buttons
        self.SearchButton = QPushButton("Search Notebook")
        self.SearchButton.clicked.connect(self.Search)
        self.FindInPageButton = QPushButton("Find In Page")
        self.FindInPageButton.clicked.connect(self.FindInPage)
        self.ReplaceButton = QPushButton("Replace\nCurrent Hit")
        self.ReplaceButton.clicked.connect(self.Replace)
        self.ToggleReadModeActionsList.append(self.ReplaceButton)
        self.ReplaceAllInPageButton = QPushButton("Replace All\nIn Page")
        self.ReplaceAllInPageButton.clicked.connect(self.ReplaceAllInPage)
        self.ToggleReadModeActionsList.append(self.ReplaceAllInPageButton)
        self.ReplaceAllInNotebookButton = QPushButton("Replace All\nIn Notebook")
        self.ReplaceAllInNotebookButton.clicked.connect(lambda: self.ReplaceAllInNotebook())
        self.ToggleReadModeActionsList.append(self.ReplaceAllInNotebookButton)

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
        Results = self.SearchIndexer.GetSearchResults(SearchText, MatchCase=MatchCase)
        for Result in Results:
            self.ResultsList.addItem(SearchResult(Result[0], Result[1]))
        self.ResultsList.setCurrentIndex(self.ResultsList.model().index(0))
        if not self.RefreshingSearchResults:
            self.ResultsList.setFocus()

    def SearchResultSelected(self):
        SelectedItems = self.ResultsList.selectedItems()
        if len(SelectedItems) > 0 and not self.RefreshingSearchResults:
            SelectedItem = SelectedItems[0]
            if self.NotebookDisplayWidget.GetCurrentPageIndexPath() != SelectedItem.IndexPath:
                self.NotebookDisplayWidget.SelectTreeItemFromIndexPath(SelectedItem.IndexPath)

    def SearchResultActivated(self):
        self.SearchResultSelected()
        self.FindInPage()

    def FindInPage(self):
        SearchText = self.SearchTextLineEdit.text()
        MatchCase = self.MatchCaseCheckBox.isChecked()
        if MatchCase:
            if not self.TextWidget.find(SearchText, QTextDocument.FindCaseSensitively):
                self.TextWidget.moveCursor(QTextCursor.Start)
                self.TextWidget.find(SearchText, QTextDocument.FindCaseSensitively)
        else:
            if not self.TextWidget.find(SearchText):
                self.TextWidget.moveCursor(QTextCursor.Start)
                self.TextWidget.find(SearchText)

    def Replace(self):
        if not self.TextWidget.ReadMode:
            SearchText = self.SearchTextLineEdit.text()
            if SearchText == "":
                return
            ReplaceText = self.ReplaceTextLineEdit.text()
            Cursor = self.TextWidget.textCursor()
            CurrentHitText = Cursor.selectedText()
            MatchCase = self.MatchCaseCheckBox.isChecked()
            if not MatchCase:
                SearchText = SearchText.casefold()
                CurrentHitText = CurrentHitText.casefold()
            if SearchText == CurrentHitText:
                self.TextWidget.insertPlainText(ReplaceText)
            self.FindInPage()
            self.RefreshSearch()

    def ReplaceAllInPage(self):
        if not self.TextWidget.ReadMode:
            SearchText = self.SearchTextLineEdit.text()
            if SearchText == "":
                return
            ReplaceText = self.ReplaceTextLineEdit.text()
            MatchCase = self.MatchCaseCheckBox.isChecked()
            PageText = self.TextWidget.toPlainText()
            if MatchCase:
                PageText = PageText.replace(SearchText, ReplaceText)
            else:
                PageText = re.sub(re.escape(SearchText), lambda x: ReplaceText, PageText, flags=re.IGNORECASE)
            self.TextWidget.setPlainText(PageText)
            self.RefreshSearch()

    def ReplaceAllInNotebook(self, SearchText=None, ReplaceText=None, MatchCase=None, DelayTextUpdate=False):
        if not self.TextWidget.ReadMode:
            if SearchText is None:
                SearchText = self.SearchTextLineEdit.text()
            if SearchText == "":
                return
            if ReplaceText is None:
                ReplaceText = self.ReplaceTextLineEdit.text()
            if MatchCase is None:
                MatchCase = self.MatchCaseCheckBox.isChecked()
            if MatchCase:
                self.RootPage.Content = self.RootPage.Content.replace(SearchText, ReplaceText)
            else:
                self.RootPage.Content = re.sub(re.escape(SearchText), lambda x: ReplaceText, self.RootPage.Content, flags=re.IGNORECASE)
            self.ReplaceAllInSubPages(self.RootPage, SearchText, ReplaceText, MatchCase)
            if not DelayTextUpdate:
                self.TextWidget.UpdateText()
                self.MainWindow.UpdateUnsavedChangesFlag(True)
            self.RefreshSearch()

    def ReplaceAllInSubPages(self, CurrentPage, SearchText, ReplaceText, MatchCase):
        for SubPage in CurrentPage.SubPages:
            if MatchCase:
                SubPage.Content = SubPage.Content.replace(SearchText, ReplaceText)
            else:
                SubPage.Content = re.sub(re.escape(SearchText), lambda x: ReplaceText, SubPage.Content, flags=re.IGNORECASE)
            self.ReplaceAllInSubPages(SubPage, SearchText, ReplaceText, MatchCase)

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
        self.SearchIndexer.IndexUpToDate = False
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
