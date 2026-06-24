import re

from PyQt6.QtWidgets import QDialog, QListWidget, QGridLayout, QPushButton, QListWidgetItem, QApplication


class FindPagesWithMissingFilesAndImagesDialog(QDialog):
    def __init__(self, Notebook, MainWindow):
        super().__init__(parent=MainWindow)

        # Store Parameters
        self.Notebook = Notebook
        self.MainWindow = MainWindow

        # Variables
        self.Results = []
        self.GoToIndexPath = None

        # Result List
        self.ResultList = QListWidget()
        self.ResultList.itemActivated.connect(self.GoToResultPage)

        # Buttons
        self.GoToButton = QPushButton("Go To")
        self.GoToButton.clicked.connect(self.GoToResultPage)
        self.CopyButton = QPushButton("Copy Results")
        self.CopyButton.clicked.connect(self.CopyResults)
        self.DoneButton = QPushButton("Done")
        self.DoneButton.clicked.connect(self.close)

        # Create, Populate, and Set Layout
        self.Layout = QGridLayout()
        self.Layout.addWidget(self.ResultList, 0, 0, 1, 3)
        self.Layout.addWidget(self.GoToButton, 1, 0)
        self.Layout.addWidget(self.CopyButton, 1, 1)
        self.Layout.addWidget(self.DoneButton, 1, 2)
        self.setLayout(self.Layout)

        # Set Window Title and Icon
        self.setWindowTitle("Find Missing Files and Images")
        self.setWindowIcon(self.MainWindow.WindowIcon)

        # Populate Result List
        self.PopulateResultList()

        # Execute Dialog
        self.exec()

    def PopulateResultList(self):
        if not self.Notebook.SearchIndexUpToDate:
            self.Notebook.BuildSearchIndex()

        for Page in self.Notebook.SearchIndex:
            Title = Page[0]
            Content = Page[1]
            IndexPath = Page[2]

            MissingFilesOrImages = self.GetMissingFilesOrImages(Content)

            if len(MissingFilesOrImages) > 0:
                Result = {"Title": Title, "IndexPath": IndexPath, "MissingFilesOrImages": MissingFilesOrImages}
                self.Results.append(Result)

        for Result in self.Results:
            self.ResultList.addItem(ResultListItem(Result))

    def GoToResultPage(self):
        SelectedItems = self.ResultList.selectedItems()
        if len(SelectedItems) > 0:
            SelectedItem = SelectedItems[0]
            self.GoToIndexPath = SelectedItem.IndexPath
            self.close()

    def CopyResults(self):
        ResultsString = ""
        for Result in self.Results:
            ResultsString += f"Title:  {Result["Title"]} | Index Path:  {Result["IndexPath"]} | Missing:  {str(Result["MissingFilesOrImages"])}\n"
        ResultsString = ResultsString.strip()
        QApplication.clipboard().setText(ResultsString)

    def GetMissingFilesOrImages(self, Content):
        RegEx = r"(!?)\[([^\[\]\n]*?)\]\((.+?)( \".+?\")?\)"
        MatchIterator = re.finditer(RegEx, Content)
        MissingFilesOrImages = []
        for Match in MatchIterator:
            ImageIndicator = Match.group(1) == "!"
            FileIndicator = Match.group(2) != "" and Match.group(3).startswith("[file:") and Match.group(3).endswith("]")
            LinkedImageOrFile = Match.group(3)
            if ImageIndicator:
                if not self.Notebook.HasImage(LinkedImageOrFile):
                    MissingFilesOrImages.append(LinkedImageOrFile)
            elif FileIndicator:
                if not self.Notebook.HasFile(LinkedImageOrFile):
                    MissingFilesOrImages.append(LinkedImageOrFile)
        return MissingFilesOrImages


class ResultListItem(QListWidgetItem):
    def __init__(self, Result):
        super().__init__()

        self.Title = Result["Title"]
        self.IndexPath = Result["IndexPath"]
        self.MissingFilesOrImages = Result["MissingFilesOrImages"]

        Text = f"{self.Title}"
        for MissingFileOrImage in self.MissingFilesOrImages:
            Text += f"\n    {MissingFileOrImage}"

        self.setText(Text)
