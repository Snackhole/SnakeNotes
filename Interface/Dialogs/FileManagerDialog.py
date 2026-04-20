import os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QLineEdit, QCheckBox, QListWidget, QListWidgetItem, QFrame, QLabel, QPushButton, QSizePolicy, QGridLayout, QSplitter, QFileDialog, QMessageBox, QInputDialog

from Core import Base64Converters


class FileManagerDialog(QDialog):
    def __init__(self, Notebook, MainWindow):
        super().__init__(parent=MainWindow)

        # Store Parameters
        self.Notebook = Notebook
        self.MainWindow = MainWindow

        # Variables
        self.UnsavedChanges = False
        self.ActivatedLinkingPageIndexPath = None
        self.Width = 560
        self.Height = 380

        # Search Line Edit
        self.SearchLineEdit = SearchLineEdit(self)
        self.SearchLineEdit.setPlaceholderText("Search")
        self.SearchLineEdit.textChanged.connect(self.PopulateFileList)
        self.SearchLineEdit.setFocus()

        # Match Case Check Box
        self.MatchCaseCheckBox = QCheckBox("Match Case")
        self.MatchCaseCheckBox.stateChanged.connect(self.PopulateFileList)

        # File List
        self.FileList = FileList(self)
        self.FileList.itemSelectionChanged.connect(self.ItemSelected)

        # Linking Pages Frame
        self.LinkingPagesFrame = QFrame()

        # Linking Pages Label
        self.LinkingPagesLabel = QLabel("Linking Pages")
        self.LinkingPagesLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Linking Pages List
        self.LinkingPagesList = QListWidget()
        self.LinkingPagesList.itemActivated.connect(self.LinkingPageActivated)

        # Buttons
        self.GoToLinkingPageButton = QPushButton("Go to Linking Page")
        self.GoToLinkingPageButton.clicked.connect(self.LinkingPageActivated)
        self.AddFileButton = QPushButton("Add File")
        self.AddFileButton.clicked.connect(self.AddFile)
        self.AddMultipleFilesButton = QPushButton("Add Multiple Files")
        self.AddMultipleFilesButton.clicked.connect(self.AddMultipleFiles)
        self.RenameFileButton = QPushButton("Rename File")
        self.RenameFileButton.clicked.connect(self.RenameFile)
        self.RenameFileButton.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.ExportFileButton = QPushButton("Export File")
        self.ExportFileButton.clicked.connect(self.ExportFile)
        self.ExportAllFilesButton = QPushButton("Export All Files")
        self.ExportAllFilesButton.clicked.connect(self.ExportAllFiles)
        self.DeleteFileButton = QPushButton("Delete File")
        self.DeleteFileButton.clicked.connect(self.DeleteFile)
        self.DeleteAllFilesButton = QPushButton("Delete All Files")
        self.DeleteAllFilesButton.clicked.connect(self.DeleteAllFiles)
        self.DoneButton = QPushButton("Done")
        self.DoneButton.clicked.connect(self.Done)
        self.DoneButton.setDefault(True)
        self.DoneButton.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        # Create, Populate, and Set Layout
        self.Layout = QGridLayout()
        self.SearchLayout = QGridLayout()
        self.SearchLayout.addWidget(self.SearchLineEdit, 0, 0)
        self.SearchLayout.addWidget(self.MatchCaseCheckBox, 0, 1)
        self.Layout.addLayout(self.SearchLayout, 0, 0)
        self.Splitter = QSplitter()
        self.Splitter.addWidget(self.FileList)
        self.LinkingPagesLayout = QGridLayout()
        self.LinkingPagesLayout.addWidget(self.LinkingPagesLabel, 0, 0)
        self.LinkingPagesLayout.addWidget(self.LinkingPagesList, 1, 0)
        self.LinkingPagesLayout.addWidget(self.GoToLinkingPageButton, 2, 0)
        self.LinkingPagesFrame.setLayout(self.LinkingPagesLayout)
        self.Splitter.addWidget(self.LinkingPagesFrame)
        self.Splitter.setStretchFactor(0, 1)
        self.Layout.addWidget(self.Splitter, 1, 0)
        self.ButtonLayout = QGridLayout()
        self.ButtonLayout.addWidget(self.AddFileButton, 0, 0)
        self.ButtonLayout.addWidget(self.AddMultipleFilesButton, 1, 0)
        self.ButtonLayout.addWidget(self.ExportFileButton, 0, 1)
        self.ButtonLayout.addWidget(self.ExportAllFilesButton, 1, 1)
        self.ButtonLayout.addWidget(self.DeleteFileButton, 0, 2)
        self.ButtonLayout.addWidget(self.DeleteAllFilesButton, 1, 2)
        self.ButtonLayout.addWidget(self.RenameFileButton, 0, 3, 2, 1)
        self.ButtonLayout.addWidget(self.DoneButton, 0, 4, 2, 1)
        self.Layout.addLayout(self.ButtonLayout, 2, 0)
        self.setLayout(self.Layout)

        # Set Window Title and Icon
        self.setWindowTitle("File Manager")
        self.setWindowIcon(self.MainWindow.WindowIcon)

        # Window Resize
        self.Resize()

        # Populate File List
        self.PopulateFileList()

        # Restrict Buttons if in Read Mode
        EditModeOnlyButtons = [self.AddFileButton, self.AddMultipleFilesButton, self.RenameFileButton, self.DeleteFileButton, self.DeleteAllFilesButton]
        if self.MainWindow.TextWidgetInst.ReadMode:
            for Button in EditModeOnlyButtons:
                Button.setDisabled(True)

        # Execute Dialog
        self.exec()

    def ItemSelected(self):
        SelectedItems = self.FileList.selectedItems()
        if len(SelectedItems) > 0:
            CurrentFileName = SelectedItems[0].FileName
            SearchTerm = f"]([file:{CurrentFileName}"
            SearchResults = self.Notebook.GetSearchResults(SearchTerm, MatchCase=True)
            self.LinkingPagesList.clear()
            for Result in SearchResults["ResultsList"]:
                LinkingPagesListItem = QListWidgetItem(Result[0])
                setattr(LinkingPagesListItem, "LinkingPageIndexPath", Result[1])
                self.LinkingPagesList.addItem(LinkingPagesListItem)

    def PopulateFileList(self):
        SearchTerm = self.SearchLineEdit.text()
        MatchCase = self.MatchCaseCheckBox.isChecked()
        if not MatchCase:
            SearchTerm = SearchTerm.lower()
        self.FileList.clear()
        self.LinkingPagesList.clear()
        Files = sorted(self.Notebook.Files.items(), key=lambda File: File[0].lower())
        if SearchTerm != "":
            Files = [File for File in Files if SearchTerm in (File[0].lower() if not MatchCase else File[0])]
        for FileName, Base64String in Files:
            self.FileList.addItem(FileListItem(FileName, Base64String))
        self.FileList.setCurrentRow(0)

    def AddFile(self):
        AttachNewFile = False
        FilePath = QFileDialog.getOpenFileName(parent=self, caption="Attach File")[0]
        if FilePath != "":
            FileName = os.path.basename(FilePath)
            if not os.path.isfile(FilePath):
                self.MainWindow.DisplayMessageBox(f"This filepath is not valid, and has not been attached:\n\n{FilePath}")
            elif "\"" in FileName:
                self.MainWindow.DisplayMessageBox("Attached file names cannot contain quotation marks (\").")
            elif self.Notebook.HasFile(FileName):
                if self.MainWindow.DisplayMessageBox(f"A file named \"{FileName}\" is already attached to the notebook.\n\nOverwrite existing file?", Icon=QMessageBox.Icon.Question, Buttons=(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No), Parent=self) == QMessageBox.StandardButton.Yes:
                    AttachNewFile = True
            else:
                AttachNewFile = True
        if AttachNewFile:
            self.Notebook.AddFile(FilePath)
            self.UnsavedChanges = True
            self.SearchLineEdit.clear()
            self.PopulateFileList()
            self.FileList.setCurrentRow(self.GetFileIndexFromName(os.path.basename(FilePath)))

    def AddMultipleFiles(self):
        FilePaths = QFileDialog.getOpenFileNames(parent=self, caption="Attach Files")[0]
        FileAdded = False
        for FilePath in FilePaths:
            AttachNewFile = False
            FileName = os.path.basename(FilePath)
            if not os.path.isfile(FilePath):
                self.MainWindow.DisplayMessageBox(f"This filepath is not valid, and has not been attached:\n\n{FilePath}")
            elif "\"" in FileName:
                self.MainWindow.DisplayMessageBox("Attached file names cannot contain quotation marks (\").")
            elif self.Notebook.HasFile(FileName):
                if self.MainWindow.DisplayMessageBox(f"A file named \"{FileName}\" is already attached to the notebook.\n\nOverwrite existing file?", Icon=QMessageBox.Icon.Question, Buttons=(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No), Parent=self) == QMessageBox.StandardButton.Yes:
                    AttachNewFile = True
            else:
                AttachNewFile = True
            if AttachNewFile:
                self.Notebook.AddFile(FilePath)
                FileAdded = True
        if FileAdded:
            self.UnsavedChanges = True
            self.SearchLineEdit.clear()
            self.PopulateFileList()

    def RenameFile(self):
        SelectedItems = self.FileList.selectedItems()
        if len(SelectedItems) > 0:
            CurrentFileNameParts = os.path.splitext(SelectedItems[0].FileName)
            CurrentFileName = CurrentFileNameParts[0]
            CurrentFileExtension = CurrentFileNameParts[1]
            NewName, OK = QInputDialog.getText(self, f"Rename \"{CurrentFileName}\"", "Enter a name:", text=CurrentFileName)
            if OK:
                ForbiddenCharacters = ["/", "\\", "\"", "?", "%", "*", ":", "|", "<", ">"]
                if NewName == "":
                    self.MainWindow.DisplayMessageBox("File names cannot be blank.", Parent=self)
                elif f"{NewName}{CurrentFileExtension}" in self.Notebook.Files:
                    self.MainWindow.DisplayMessageBox("There is already a file by that name.", Parent=self)
                elif any(Character in NewName for Character in ForbiddenCharacters):
                    self.MainWindow.DisplayMessageBox(f"File names cannot contain the following characters:  {" ".join(ForbiddenCharacters)}", Parent=self)
                else:
                    FileContent = self.Notebook.Files[f"{CurrentFileName}{CurrentFileExtension}"]
                    self.Notebook.Files[f"{NewName}{CurrentFileExtension}"] = FileContent
                    del self.Notebook.Files[f"{CurrentFileName}{CurrentFileExtension}"]
                    self.MainWindow.SearchWidgetInst.ReplaceAllInNotebook(SearchText=f"]([file:{CurrentFileName}{CurrentFileExtension}", ReplaceText=f"]([file:{NewName}{CurrentFileExtension}", MatchCase=True)
                    self.UnsavedChanges = True
                    self.SearchLineEdit.clear()
                    self.PopulateFileList()
                    self.FileList.setCurrentRow(self.GetFileIndexFromName(f"{NewName}{CurrentFileExtension}"))

    def ExportFile(self):
        SelectedItems = self.FileList.selectedItems()
        if len(SelectedItems) > 0:
            CurrentFileName = SelectedItems[0].FileName
            CurrentFileExtension = os.path.splitext(CurrentFileName)[1]
            ExportFilePath = QFileDialog.getSaveFileName(parent=self, caption="Export File", directory=CurrentFileName, filter=(f"{CurrentFileExtension[1:].upper()} (*{CurrentFileExtension})" if CurrentFileExtension != "" else None))[0]
            if ExportFilePath != "":
                if not ExportFilePath.endswith(CurrentFileExtension):
                    ExportFilePath += CurrentFileExtension
                Base64Converters.WriteFileFromBase64String(SelectedItems[0].Base64String, ExportFilePath)

    def ExportAllFiles(self):
        ExportDirectory = QFileDialog.getExistingDirectory(parent=self, caption="Export All Files")
        if ExportDirectory != "":
            ExportDirectoryContents = os.listdir(ExportDirectory)
            if len(ExportDirectoryContents) == 0:
                for File in self.Notebook.Files.keys():
                    ExportFilePath = os.path.join(ExportDirectory, File)
                    Base64Converters.WriteFileFromBase64String(self.Notebook.Files[File], ExportFilePath)
            else:
                self.MainWindow.DisplayMessageBox("Choose an empty folder to export all files.", Parent=self)

    def DeleteFile(self):
        SelectedItems = self.FileList.selectedItems()
        if len(SelectedItems) > 0:
            CurrentFileName = SelectedItems[0].FileName
            CurrentFileRow = self.FileList.currentRow()
            if self.MainWindow.DisplayMessageBox(f"Are you sure you want to delete \"{CurrentFileName}\" from the notebook?  This cannot be undone.", Icon=QMessageBox.Icon.Question, Buttons=(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No), Parent=self) == QMessageBox.StandardButton.Yes:
                del self.Notebook.Files[CurrentFileName]
                self.UnsavedChanges = True
                self.PopulateFileList()
                if self.FileList.count() == 0:
                    pass
                elif CurrentFileRow == self.FileList.count():
                    self.FileList.setCurrentRow(CurrentFileRow - 1)
                else:
                    self.FileList.setCurrentRow(CurrentFileRow)

    def DeleteAllFiles(self):
        if self.MainWindow.DisplayMessageBox("Are you sure you want to delete all files from the notebook?  This cannot be undone.", Icon=QMessageBox.Icon.Warning, Buttons=(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No), Parent=self) == QMessageBox.StandardButton.Yes:
            self.Notebook.Files.clear()
            self.UnsavedChanges = True
            self.PopulateFileList()

    def GetFileIndexFromName(self, FileName):
        FileNames = sorted(self.Notebook.Files.keys(), key=lambda File: File.lower())
        return FileNames.index(FileName)

    def LinkingPageActivated(self):
        SelectedItems = self.LinkingPagesList.selectedItems()
        if len(SelectedItems) > 0:
            self.ActivatedLinkingPageIndexPath = SelectedItems[0].LinkingPageIndexPath
            self.Done()
        else:
            self.MainWindow.DisplayMessageBox("No linking pages are selected.", Parent=self)

    def Done(self):
        self.close()

    def Resize(self):
        self.resize(self.Width, self.Height)


class FileListItem(QListWidgetItem):
    def __init__(self, FileName, Base64String):
        super().__init__()

        self.FileName = FileName
        self.Base64String = Base64String

        self.setText(self.FileName)


class SearchLineEdit(QLineEdit):
    def __init__(self, Dialog):
        # QLineEdit Init
        super().__init__()

        # Store Parameters
        self.Dialog = Dialog

    def keyPressEvent(self, QKeyEvent):
        KeyPressed = QKeyEvent.key()
        if KeyPressed == Qt.Key.Key_Down:
            self.Dialog.FileList.setFocus()
        else:
            super().keyPressEvent(QKeyEvent)


class FileList(QListWidget):
    def __init__(self, Dialog):
        # QListWidget Init
        super().__init__()

        # Store Parameters
        self.Dialog = Dialog

    def keyPressEvent(self, QKeyEvent):
        KeyPressed = QKeyEvent.key()
        Row = self.currentRow()
        if KeyPressed == Qt.Key.Key_Up and Row == 0:
            self.Dialog.SearchLineEdit.setFocus()
        else:
            super().keyPressEvent(QKeyEvent)
