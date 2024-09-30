from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QGridLayout, QPushButton, QApplication, QLineEdit, QCheckBox, QListWidget, QLabel, QSizePolicy, QListWidgetItem, QTreeWidget, QTreeWidgetItem, QHeaderView


class AdvancedSearchDialog(QDialog):
    def __init__(self, MainWindow):
        super().__init__(parent=MainWindow)

        # Store Parameters
        self.MainWindow = MainWindow

        # Variables
        self.RefreshingSearchResults = False
        self.WithinPage = None

        # Inputs Size Policy
        self.InputsSizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        # Advanced Search Text Line Edit
        self.SearchTextLineEdit = QLineEdit()
        self.SearchTextLineEdit.setPlaceholderText("Search")
        self.SearchTextLineEdit.setSizePolicy(self.InputsSizePolicy)

        # Match Case Check Box
        self.MatchCaseCheckBox = QCheckBox("Match Case")
        self.MatchCaseCheckBox.setSizePolicy(self.InputsSizePolicy)

        # Content Filtering Inputs
        self.ContentContainsLabel = QLabel("Content Contains:")
        self.ContentContainsLineEdit = QLineEdit()
        self.ContentContainsLineEdit.setSizePolicy(self.InputsSizePolicy)
        self.ContentContainsMatchCaseCheckBox = QCheckBox("Match Case")
        self.ContentContainsMatchCaseCheckBox.setSizePolicy(self.InputsSizePolicy)
        self.ContentDoesNotContainLabel = QLabel("Content Does Not Contain:")
        self.ContentDoesNotContainLineEdit = QLineEdit()
        self.ContentDoesNotContainLineEdit.setSizePolicy(self.InputsSizePolicy)
        self.ContentDoesNotContainMatchCaseCheckBox = QCheckBox("Match Case")
        self.ContentDoesNotContainMatchCaseCheckBox.setSizePolicy(self.InputsSizePolicy)
        self.ContentStartsWithLabel = QLabel("Content Starts With:")
        self.ContentStartsWithLineEdit = QLineEdit()
        self.ContentStartsWithLineEdit.setSizePolicy(self.InputsSizePolicy)
        self.ContentStartsWithMatchCaseCheckBox = QCheckBox("Match Case")
        self.ContentStartsWithMatchCaseCheckBox.setSizePolicy(self.InputsSizePolicy)
        self.ContentEndsWithLabel = QLabel("Content Ends With:")
        self.ContentEndsWithLineEdit = QLineEdit()
        self.ContentEndsWithLineEdit.setSizePolicy(self.InputsSizePolicy)
        self.ContentEndsWithMatchCaseCheckBox = QCheckBox("Match Case")
        self.ContentEndsWithMatchCaseCheckBox.setSizePolicy(self.InputsSizePolicy)

        # Title Filtering Inputs
        self.TitleContainsLabel = QLabel("Title Contains:")
        self.TitleContainsLineEdit = QLineEdit()
        self.TitleContainsLineEdit.setSizePolicy(self.InputsSizePolicy)
        self.TitleContainsMatchCaseCheckBox = QCheckBox("Match Case")
        self.TitleContainsMatchCaseCheckBox.setSizePolicy(self.InputsSizePolicy)
        self.TitleDoesNotContainLabel = QLabel("Title Does Not Contain:")
        self.TitleDoesNotContainLineEdit = QLineEdit()
        self.TitleDoesNotContainLineEdit.setSizePolicy(self.InputsSizePolicy)
        self.TitleDoesNotContainMatchCaseCheckBox = QCheckBox("Match Case")
        self.TitleDoesNotContainMatchCaseCheckBox.setSizePolicy(self.InputsSizePolicy)
        self.TitleStartsWithLabel = QLabel("Title Starts With:")
        self.TitleStartsWithLineEdit = QLineEdit()
        self.TitleStartsWithLineEdit.setSizePolicy(self.InputsSizePolicy)
        self.TitleStartsWithMatchCaseCheckBox = QCheckBox("Match Case")
        self.TitleStartsWithMatchCaseCheckBox.setSizePolicy(self.InputsSizePolicy)
        self.TitleEndsWithLabel = QLabel("Title Ends With:")
        self.TitleEndsWithLineEdit = QLineEdit()
        self.TitleEndsWithLineEdit.setSizePolicy(self.InputsSizePolicy)
        self.TitleEndsWithMatchCaseCheckBox = QCheckBox("Match Case")
        self.TitleEndsWithMatchCaseCheckBox.setSizePolicy(self.InputsSizePolicy)

        # Within Page Inputs
        self.WithinPageButton = QPushButton("Within Page...")
        self.WithinPageButton.setSizePolicy(self.InputsSizePolicy)
        self.WithinPageButton.clicked.connect(self.SelectWithinPage)
        self.WithinPageLineEdit = QLineEdit()
        self.WithinPageLineEdit.setSizePolicy(self.InputsSizePolicy)
        self.WithinPageLineEdit.setReadOnly(True)

        # Results List
        self.ResultsList = QListWidget()
        self.ResultsList.setMinimumWidth(300)
        self.ResultsList.itemActivated.connect(self.GoTo)

        # Search Results Stats Label
        self.SearchResultsStatsLabel = QLabel("No search results.")
        self.SearchResultsStatsLabel.setAlignment(Qt.AlignCenter)

        # Buttons
        self.SearchButton = QPushButton("Search")
        self.SearchButton.clicked.connect(self.Search)
        self.SearchButton.setDefault(True)
        self.GoToButton = QPushButton("Go To")
        self.GoToButton.clicked.connect(self.GoTo)
        self.CopySearchResultsButton = QPushButton("Copy Search Results")
        self.CopySearchResultsButton.clicked.connect(self.CopySearchResults)
        self.ClearButton = QPushButton("Clear")
        self.ClearButton.clicked.connect(self.ClearSearch)
        self.CloseButton = QPushButton("Close")
        self.CloseButton.clicked.connect(self.close)

        # Create, Populate, and Set Layout
        self.Layout = QGridLayout()

        self.SearchLayout = QGridLayout()
        self.SearchLayout.addWidget(self.SearchTextLineEdit, 0, 0, 1, 2)
        self.SearchLayout.addWidget(self.MatchCaseCheckBox, 0, 2)
        self.SearchLayout.addWidget(self.ContentContainsLabel, 1, 0)
        self.SearchLayout.addWidget(self.ContentContainsLineEdit, 1, 1)
        self.SearchLayout.addWidget(self.ContentContainsMatchCaseCheckBox, 1, 2)
        self.SearchLayout.addWidget(self.ContentDoesNotContainLabel, 2, 0)
        self.SearchLayout.addWidget(self.ContentDoesNotContainLineEdit, 2, 1)
        self.SearchLayout.addWidget(self.ContentDoesNotContainMatchCaseCheckBox, 2, 2)
        self.SearchLayout.addWidget(self.ContentStartsWithLabel, 3, 0)
        self.SearchLayout.addWidget(self.ContentStartsWithLineEdit, 3, 1)
        self.SearchLayout.addWidget(self.ContentStartsWithMatchCaseCheckBox, 3, 2)
        self.SearchLayout.addWidget(self.ContentEndsWithLabel, 4, 0)
        self.SearchLayout.addWidget(self.ContentEndsWithLineEdit, 4, 1)
        self.SearchLayout.addWidget(self.ContentEndsWithMatchCaseCheckBox, 4, 2)
        self.SearchLayout.addWidget(self.TitleContainsLabel, 5, 0)
        self.SearchLayout.addWidget(self.TitleContainsLineEdit, 5, 1)
        self.SearchLayout.addWidget(self.TitleContainsMatchCaseCheckBox, 5, 2)
        self.SearchLayout.addWidget(self.TitleDoesNotContainLabel, 6, 0)
        self.SearchLayout.addWidget(self.TitleDoesNotContainLineEdit, 6, 1)
        self.SearchLayout.addWidget(self.TitleDoesNotContainMatchCaseCheckBox, 6, 2)
        self.SearchLayout.addWidget(self.TitleStartsWithLabel, 7, 0)
        self.SearchLayout.addWidget(self.TitleStartsWithLineEdit, 7, 1)
        self.SearchLayout.addWidget(self.TitleStartsWithMatchCaseCheckBox, 7, 2)
        self.SearchLayout.addWidget(self.TitleEndsWithLabel, 8, 0)
        self.SearchLayout.addWidget(self.TitleEndsWithLineEdit, 8, 1)
        self.SearchLayout.addWidget(self.TitleEndsWithMatchCaseCheckBox, 8, 2)
        self.SearchLayout.addWidget(self.WithinPageButton, 9, 0)
        self.SearchLayout.addWidget(self.WithinPageLineEdit, 9, 1, 1, 2)
        self.Layout.addLayout(self.SearchLayout, 0, 0, 2, 1)

        self.Layout.addWidget(self.ResultsList, 0, 1)

        self.Layout.addWidget(self.SearchResultsStatsLabel, 1, 1)

        self.ButtonsLayout = QGridLayout()
        self.ButtonsLayout.addWidget(self.SearchButton, 0, 0)
        self.ButtonsLayout.addWidget(self.GoToButton, 0, 1)
        self.ButtonsLayout.addWidget(self.CopySearchResultsButton, 0, 2)
        self.ButtonsLayout.addWidget(self.ClearButton, 0, 3)
        self.ButtonsLayout.addWidget(self.CloseButton, 0, 4)
        self.Layout.addLayout(self.ButtonsLayout, 2, 0, 1, 2)

        self.setLayout(self.Layout)

        # Set Window Title and Icon
        self.setWindowTitle("Advanced Search")
        self.setWindowIcon(self.MainWindow.WindowIcon)

        # Show Window
        self.show()

        # Set Geometry to Minimum and Center
        self.SetGeometryToMinimum()
        self.Center()

    def Search(self):
        SearchText = self.SearchTextLineEdit.text()
        MatchCase = self.MatchCaseCheckBox.isChecked()
        self.ResultsList.clear()
        if SearchText == "":
            return
        UnfilteredResults = self.MainWindow.Notebook.GetSearchResults(SearchText, MatchCase=MatchCase)
        Filters = self.GetFilters()
        FilteredResults = self.MainWindow.Notebook.GetFilteredSearchResults(UnfilteredResults, Filters)
        for Result in FilteredResults["ResultsList"]:
            self.ResultsList.addItem(SearchResult(Result[0], Result[1], Result[3], Result[4], self.MainWindow.ShowHitCounts))
        if len(FilteredResults["ResultsList"]) > 0:
            TotalHits = str(FilteredResults["TotalHits"])
            PluralizeHits = ("" if FilteredResults["TotalHits"] == 1 else "s")
            TotalPages = str(FilteredResults["TotalPages"])
            PluralizePages = ("" if FilteredResults["TotalPages"] == 1 else "s")
            ResultsStatsString = f"{TotalHits} hit{PluralizeHits} in {TotalPages} page{PluralizePages}."
        else:
            ResultsStatsString = "No search results."
        self.SearchResultsStatsLabel.setText(ResultsStatsString)
        self.ResultsList.setCurrentRow(0)
        if not self.RefreshingSearchResults:
            self.ResultsList.setFocus()

    def GetFilters(self):
        Filters = {}

        ContentContains = self.ContentContainsLineEdit.text()
        ContentContainsMatchCase = self.ContentContainsMatchCaseCheckBox.isChecked()
        if ContentContains != "":
            Filters["ContentContains"] = {}
            Filters["ContentContains"]["Text"] = ContentContains
            Filters["ContentContains"]["MatchCase"] = ContentContainsMatchCase

        ContentDoesNotContain = self.ContentDoesNotContainLineEdit.text()
        ContentDoesNotContainMatchCase = self.ContentDoesNotContainMatchCaseCheckBox.isChecked()
        if ContentDoesNotContain != "":
            Filters["ContentDoesNotContain"] = {}
            Filters["ContentDoesNotContain"]["Text"] = ContentDoesNotContain
            Filters["ContentDoesNotContain"]["MatchCase"] = ContentDoesNotContainMatchCase

        ContentStartsWith = self.ContentStartsWithLineEdit.text()
        ContentStartsWithMatchCase = self.ContentStartsWithMatchCaseCheckBox.isChecked()
        if ContentStartsWith != "":
            Filters["ContentStartsWith"] = {}
            Filters["ContentStartsWith"]["Text"] = ContentStartsWith
            Filters["ContentStartsWith"]["MatchCase"] = ContentStartsWithMatchCase

        ContentEndsWith = self.ContentEndsWithLineEdit.text()
        ContentEndsWithMatchCase = self.ContentEndsWithMatchCaseCheckBox.isChecked()
        if ContentEndsWith != "":
            Filters["ContentEndsWith"] = {}
            Filters["ContentEndsWith"]["Text"] = ContentEndsWith
            Filters["ContentEndsWith"]["MatchCase"] = ContentEndsWithMatchCase

        TitleContains = self.TitleContainsLineEdit.text()
        TitleContainsMatchCase = self.TitleContainsMatchCaseCheckBox.isChecked()
        if TitleContains != "":
            Filters["TitleContains"] = {}
            Filters["TitleContains"]["Text"] = TitleContains
            Filters["TitleContains"]["MatchCase"] = TitleContainsMatchCase

        TitleDoesNotContain = self.TitleDoesNotContainLineEdit.text()
        TitleDoesNotContainMatchCase = self.TitleDoesNotContainMatchCaseCheckBox.isChecked()
        if TitleDoesNotContain != "":
            Filters["TitleDoesNotContain"] = {}
            Filters["TitleDoesNotContain"]["Text"] = TitleDoesNotContain
            Filters["TitleDoesNotContain"]["MatchCase"] = TitleDoesNotContainMatchCase

        TitleStartsWith = self.TitleStartsWithLineEdit.text()
        TitleStartsWithMatchCase = self.TitleStartsWithMatchCaseCheckBox.isChecked()
        if TitleStartsWith != "":
            Filters["TitleStartsWith"] = {}
            Filters["TitleStartsWith"]["Text"] = TitleStartsWith
            Filters["TitleStartsWith"]["MatchCase"] = TitleStartsWithMatchCase

        TitleEndsWith = self.TitleEndsWithLineEdit.text()
        TitleEndsWithMatchCase = self.TitleEndsWithMatchCaseCheckBox.isChecked()
        if TitleEndsWith != "":
            Filters["TitleEndsWith"] = {}
            Filters["TitleEndsWith"]["Text"] = TitleEndsWith
            Filters["TitleEndsWith"]["MatchCase"] = TitleEndsWithMatchCase

        if self.WithinPage is not None:
            Filters["WithinPageIndexPath"] = self.WithinPage["IndexPath"]

        return Filters

    def RefreshSearch(self):
        if self.WithinPage is None:
            self.WithinPageLineEdit.clear()
        else:
            self.WithinPageLineEdit.setText(f"{self.WithinPage["Title"]} | Index Path:  {str(self.WithinPage["IndexPath"])}")
        self.RefreshingSearchResults = True
        self.Search()
        self.RefreshingSearchResults = False

    def GoTo(self):
        SelectedItems = self.ResultsList.selectedItems()
        if len(SelectedItems) > 0 and not self.RefreshingSearchResults:
            SelectedItem = SelectedItems[0]
            if self.MainWindow.NotebookDisplayWidgetInst.GetCurrentPageIndexPath() != SelectedItem.IndexPath:
                self.MainWindow.NotebookDisplayWidgetInst.SelectTreeItemFromIndexPath(SelectedItem.IndexPath)

    def SelectWithinPage(self):
        GetWithinPageDialog(self.MainWindow.Notebook, self)
        self.RefreshSearch()

    def ClearWithinPage(self):
        self.WithinPage = None

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
        for LineEdit in [self.SearchTextLineEdit, self.ContentContainsLineEdit, self.ContentDoesNotContainLineEdit, self.ContentStartsWithLineEdit, self.ContentEndsWithLineEdit, self.TitleContainsLineEdit, self.TitleDoesNotContainLineEdit, self.TitleStartsWithLineEdit, self.TitleEndsWithLineEdit]:
            LineEdit.clear()
        for CheckBox in [self.MatchCaseCheckBox, self.ContentContainsMatchCaseCheckBox, self.ContentDoesNotContainMatchCaseCheckBox, self.ContentStartsWithMatchCaseCheckBox, self.ContentEndsWithMatchCaseCheckBox, self.TitleContainsMatchCaseCheckBox, self.TitleDoesNotContainMatchCaseCheckBox, self.TitleStartsWithMatchCaseCheckBox, self.TitleEndsWithMatchCaseCheckBox]:
            CheckBox.setChecked(False)
        self.WithinPage = None
        self.SearchResultsStatsLabel.setText("No search results.")
        self.RefreshSearch()

    def SetGeometryToMinimum(self):
        FrameGeometryRectangle = self.frameGeometry()
        FrameGeometryRectangle.setWidth(self.minimumWidth())
        FrameGeometryRectangle.setHeight(self.minimumHeight())
        self.setGeometry(FrameGeometryRectangle)

    def Center(self):
        FrameGeometryRectangle = self.frameGeometry()
        MainWindowCenterPoint = self.MainWindow.frameGeometry().center()
        FrameGeometryRectangle.moveCenter(MainWindowCenterPoint)
        self.move(FrameGeometryRectangle.topLeft())

    def closeEvent(self, event):
        self.MainWindow.AdvancedSearchDialogInst = None
        return super().closeEvent(event)

    def keyPressEvent(self, QKeyEvent):
        KeyPressed = QKeyEvent.key()
        if KeyPressed == Qt.Key_Escape:
            self.close()
        elif KeyPressed == Qt.Key_Return and self.ResultsList.hasFocus():
            return
        else:
            super().keyPressEvent(QKeyEvent)


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


class GetWithinPageDialog(QDialog):
    def __init__(self, Notebook, AdvancedSearchDialog) -> None:
        super().__init__(parent=AdvancedSearchDialog)

        # Store Parameters
        self.Notebook = Notebook
        self.AdvancedSearchDialog = AdvancedSearchDialog

        # Label
        self.WithinPagePrompt = QLabel("Search within which page?")

        # Notebook Display Tree Widget
        self.NotebookDisplay = QTreeWidget()
        self.NotebookDisplay.setHeaderHidden(True)
        self.NotebookDisplay.header().setStretchLastSection(False)
        self.NotebookDisplay.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.NotebookDisplay.itemActivated.connect(self.Done)

        # Buttons
        self.DoneButton = QPushButton("Done")
        self.DoneButton.clicked.connect(self.Done)
        self.ClearButton = QPushButton("Clear")
        self.ClearButton.clicked.connect(self.Clear)
        self.CancelButton = QPushButton("Cancel")
        self.CancelButton.clicked.connect(self.Cancel)

        # Create, Populate, and Set Layout
        self.Layout = QGridLayout()
        self.Layout.addWidget(self.WithinPagePrompt, 0, 0, 1, 3)
        self.Layout.addWidget(self.NotebookDisplay, 1, 0, 1, 3)
        self.Layout.addWidget(self.DoneButton, 2, 0)
        self.Layout.addWidget(self.ClearButton, 2, 1)
        self.Layout.addWidget(self.CancelButton, 2, 2)
        self.setLayout(self.Layout)

        # Populate Notebook Display
        self.PopulateNotebookDisplay()

        # Execute Dialog
        self.exec_()

    def PopulateNotebookDisplay(self):
        self.NotebookDisplay.clear()
        self.FillNotebookWidgetItem(self.NotebookDisplay.invisibleRootItem(), self.Notebook.RootPage, IsRootPage=True)

    def FillNotebookWidgetItem(self, CurrentTreeItem, CurrentPage, IsRootPage=False):
        ChildTreeItem = NotebookDisplayItem(CurrentPage["Title"], CurrentPage["IndexPath"])
        CurrentTreeItem.addChild(ChildTreeItem)

        for SubPage in CurrentPage["SubPages"]:
            self.FillNotebookWidgetItem(ChildTreeItem, SubPage)

        if IsRootPage:
            ChildTreeItem.setExpanded(True)
            self.NotebookDisplay.setCurrentIndex(self.NotebookDisplay.model().index(0, 0))

    def Done(self):
        SelectedItems = self.NotebookDisplay.selectedItems()
        if len(SelectedItems) < 1:
            return
        SelectedItem = SelectedItems[0]
        self.AdvancedSearchDialog.WithinPage = self.Notebook.GetPageFromIndexPath(SelectedItem.IndexPath)
        self.close()

    def Clear(self):
        self.AdvancedSearchDialog.WithinPage = None
        self.close()

    def Cancel(self):
        self.close()


class NotebookDisplayItem(QTreeWidgetItem):
    def __init__(self, Title, IndexPath):
        super().__init__()

        # Store Parameters
        self.Title = Title
        self.IndexPath = IndexPath

        # Set Text
        self.setText(0, Title)
