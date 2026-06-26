from PyQt6.QtWidgets import QDialog, QListWidget, QGridLayout, QPushButton, QListWidgetItem, QApplication


class FindFilesAndImagesNotLinkedInPagesDialog(QDialog):
    def __init__(self, Notebook, MainWindow):
        super().__init__(parent=MainWindow)

        # Store Parameters
        self.Notebook = Notebook
        self.MainWindow = MainWindow

        # Variables
        self.Results = []

        # Result List
        self.ResultList = QListWidget()

        # Buttons
        self.CopyButton = QPushButton("Copy Results")
        self.CopyButton.clicked.connect(self.CopyResults)
        self.DoneButton = QPushButton("Done")
        self.DoneButton.clicked.connect(self.close)

        # Create, Populate, and Set Layout
        self.Layout = QGridLayout()
        self.Layout.addWidget(self.ResultList, 0, 0, 1, 2)
        self.Layout.addWidget(self.CopyButton, 1, 0)
        self.Layout.addWidget(self.DoneButton, 1, 1)
        self.setLayout(self.Layout)

        # Set Window Title and Icon
        self.setWindowTitle("Find Files and Images Not Linked in Pages")
        self.setWindowIcon(self.MainWindow.WindowIcon)

        # Populate Result List
        self.PopulateResultList()

        # Execute Dialog
        self.exec()

    def PopulateResultList(self):
        if not self.Notebook.SearchIndexUpToDate:
            self.Notebook.BuildSearchIndex()

        for Image in self.Notebook.Images.keys():
            SearchTerm = f"]({Image}"
            SearchResults = self.Notebook.GetSearchResults(SearchTerm, MatchCase=True)

            if len(SearchResults["ResultsList"]) < 1:
                self.Results.append({"FileName": Image, "FileType": "Image"})

        for File in self.Notebook.Files.keys():
            SearchTerm = f"]([file:{File}"
            SearchResults = self.Notebook.GetSearchResults(SearchTerm, MatchCase=True)

            if len(SearchResults["ResultsList"]) < 1:
                self.Results.append({"FileName": File, "FileType": "File"})

        for Result in self.Results:
            self.ResultList.addItem(ResultListItem(Result))

    def CopyResults(self):
        ResultsString = ""
        for Result in self.Results:
            ResultsString += f"{Result["FileType"]}:  {Result["FileName"]}\n"
        ResultsString = ResultsString.strip()
        QApplication.clipboard().setText(ResultsString)


class ResultListItem(QListWidgetItem):
    def __init__(self, Result):
        super().__init__()

        self.FileName = Result["FileName"]
        self.FileType = Result["FileType"]

        Text = f"{self.FileType}:  {self.FileName}"

        self.setText(Text)
