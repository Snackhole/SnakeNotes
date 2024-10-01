import re

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor, QTextDocument
from PyQt5.QtWidgets import QFrame, QLineEdit, QListWidget, QGridLayout, QListWidgetItem, QPushButton, QCheckBox, QSizePolicy, QApplication


class SearchWidget(QFrame):
    def __init__(self, Notebook, MainWindow):
        super().__init__()

        # Store Parameters
        self.Notebook = Notebook
        self.MainWindow = MainWindow

        # Variables
        self.RefreshingSearchResults = False

        # Inputs Size Policy
        self.InputsSizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        # Search Text Line Edit
        self.SearchTextLineEdit = SearchLineEdit(self)
        self.SearchTextLineEdit.setPlaceholderText("Search (Ctrl+F)")
        self.SearchTextLineEdit.returnPressed.connect(self.Search)
        self.SearchTextLineEdit.textChanged.connect(self.RehighlightTextWidget)

        # Highlight Text Check Box
        self.HighlightCheckBox = QCheckBox("Highlight Text")
        self.HighlightCheckBox.stateChanged.connect(self.RehighlightTextWidget)

        # Highlight Pages Check Box
        self.HighlightPagesCheckBox = QCheckBox("Highlight Pages")
        self.HighlightPagesCheckBox.stateChanged.connect(lambda: self.HighlightPages(Clear=True))

        # Match Case Check Box
        self.MatchCaseCheckBox = QCheckBox("Match Case")
        self.MatchCaseCheckBox.stateChanged.connect(self.RehighlightTextWidget)

        # Replace Text Line Edit
        self.ReplaceTextLineEdit = SearchLineEdit(self)
        self.ReplaceTextLineEdit.setPlaceholderText("Replace With")
        self.MainWindow.ToggleReadModeActionsList.append(self.ReplaceTextLineEdit)

        # Buttons
        self.SearchButton = QPushButton("Search\nNotebook")
        self.SearchButton.setSizePolicy(self.InputsSizePolicy)
        self.SearchButton.clicked.connect(self.Search)
        self.FindInPageButton = QPushButton("Find\nIn Page")
        self.FindInPageButton.setSizePolicy(self.InputsSizePolicy)
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

        # Results List
        self.ResultsList = QListWidget()
        self.ResultsList.itemSelectionChanged.connect(self.SearchResultSelected)
        self.ResultsList.itemActivated.connect(self.SearchResultActivated)

        # Layout
        self.Layout = QGridLayout()
        self.Layout.addWidget(self.SearchTextLineEdit, 0, 0, 1, 3)
        self.Layout.addWidget(self.SearchButton, 1, 0, 3, 1)
        self.Layout.addWidget(self.FindInPageButton, 1, 1, 3, 1)
        self.Layout.addWidget(self.MatchCaseCheckBox, 1, 2)
        self.Layout.addWidget(self.HighlightCheckBox, 2, 2)
        self.Layout.addWidget(self.HighlightPagesCheckBox, 3, 2)
        self.Layout.addWidget(self.ReplaceTextLineEdit, 4, 0, 1, 3)
        self.Layout.addWidget(self.ReplaceButton, 5, 0)
        self.Layout.addWidget(self.ReplaceAllInPageButton, 5, 1)
        self.Layout.addWidget(self.ReplaceAllInNotebookButton, 5, 2)
        self.Layout.addWidget(self.ResultsList, 0, 3, 6, 1)
        self.setLayout(self.Layout)

        # Start Invisible
        self.setVisible(False)

    def Search(self):
        SearchText = self.SearchTextLineEdit.text()
        MatchCase = self.MatchCaseCheckBox.isChecked()
        self.ResultsList.clear()
        self.MainWindow.NotebookDisplayWidgetInst.ClearPageHighlighting()
        if SearchText == "":
            return
        Results = self.Notebook.GetSearchResults(SearchText, MatchCase=MatchCase)
        for Result in Results["ResultsList"]:
            self.ResultsList.addItem(SearchResult(Result[0], Result[1], Result[3], Result[4], self.MainWindow.ShowHitCounts))
        if len(Results["ResultsList"]) > 0:
            TotalHits = str(Results["TotalHits"])
            PluralizeHits = ("" if Results["TotalHits"] == 1 else "s")
            TotalPages = str(Results["TotalPages"])
            PluralizePages = ("" if Results["TotalPages"] == 1 else "s")
            ResultsStatsString = f"{TotalHits} hit{PluralizeHits} in {TotalPages} page{PluralizePages}."
        else:
            ResultsStatsString = "No search results."
        self.MainWindow.SearchResultsStatsLabel.setText(ResultsStatsString)
        self.HighlightPages()
        self.ResultsList.setCurrentRow(0)
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

    def RehighlightTextWidget(self):
        self.MainWindow.TextWidgetInst.SyntaxHighlighter.rehighlight()

    def HighlightPages(self, Clear=False):
        if Clear:
            self.MainWindow.NotebookDisplayWidgetInst.ClearPageHighlighting()
        if self.HighlightPagesCheckBox.isChecked():
            HighlightedPageIndexPaths = []
            for Result in range(self.ResultsList.count()):
                HighlightedPageIndexPaths.append(self.ResultsList.item(Result).IndexPath)
            self.MainWindow.NotebookDisplayWidgetInst.HighlightPages(HighlightedPageIndexPaths)

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
            self.MainWindow.RefreshAdvancedSearch()

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
            self.MainWindow.RefreshAdvancedSearch()

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
            self.MainWindow.RefreshAdvancedSearch()

    def ReplaceAllInPageAndSubPages(self, CurrentPage, SearchText, ReplaceText, MatchCase):
        if MatchCase:
            CurrentPage["Content"] = CurrentPage["Content"].replace(SearchText, ReplaceText)
        else:
            CurrentPage["Content"] = re.sub(re.escape(SearchText), lambda x: ReplaceText, CurrentPage["Content"], flags=re.IGNORECASE)
        for SubPage in CurrentPage["SubPages"]:
            self.ReplaceAllInPageAndSubPages(SubPage, SearchText, ReplaceText, MatchCase)

    def CopySearchResults(self):
        ResultsCount = self.ResultsList.count()
        if ResultsCount > 0:
            ResultsString = ""
            for ResultIndex in range(ResultsCount):
                Result = self.ResultsList.item(ResultIndex)
                ResultsString += f"{Result.Title} | Index Path:  {str(Result.IndexPath)} | Title Hits:  {str(Result.TitleHits)} | Content Hits:  {str(Result.ContentHits)}\n"
            ResultsString = ResultsString.rstrip()
            QApplication.clipboard().setText(ResultsString)

    def ClearSearch(self):
        self.SearchTextLineEdit.clear()
        self.ReplaceTextLineEdit.clear()
        self.MatchCaseCheckBox.setChecked(False)
        self.MainWindow.SearchResultsStatsLabel.setText("No search results.")
        self.ResultsList.clear()
        self.RehighlightTextWidget()
        self.MainWindow.NotebookDisplayWidgetInst.ClearPageHighlighting()

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
        self.MainWindow.SearchResultsStatsLabel.setVisible(not VisibleState)
        self.MainWindow.SearchResultsStatsLabel.setEnabled(not VisibleState)

    def GrabFocus(self):
        if not self.isVisible():
            self.ToggleVisibility()
        self.NewSearch()


class SearchResult(QListWidgetItem):
    def __init__(self, Title, IndexPath, TitleHits, ContentHits, ShowHitCounts):
        super().__init__()

        # Store Parameters
        self.Title = Title
        self.IndexPath = IndexPath
        self.TitleHits = TitleHits
        self.ContentHits = ContentHits
        self.ShowHitCounts = ShowHitCounts

        # Set Text
        if self.ShowHitCounts:
            TitleHitsString = str(self.TitleHits)
            PluralizeTitleHits = ("" if self.TitleHits == 1 else "s")
            ContentHitsString = str(self.ContentHits)
            PluralizeContentHits = ("" if self.ContentHits == 1 else "s")
            HitCountsString = f"\n        [{TitleHitsString} title hit{PluralizeTitleHits}; {ContentHitsString} content hit{PluralizeContentHits}]"
            self.setText(f"{self.Title}{HitCountsString}")
        else:
            self.setText(self.Title)


class SearchLineEdit(QLineEdit):
    def __init__(self, SearchWidget):
        # QLineEdit Init
        super().__init__()

        # Store Parameters
        self.SearchWidget = SearchWidget

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == Qt.Key_Escape:
            self.SearchWidget.ClearSearch()
        else:
            super().keyPressEvent(QKeyEvent)
