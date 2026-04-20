from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QLineEdit, QCheckBox, QListWidget, QListWidgetItem, QPushButton, QGridLayout


class LinkFileDialog(QDialog):
    def __init__(self, Notebook, MainWindow):
        super().__init__(parent=MainWindow)

        # Store Parameters
        self.Notebook = Notebook
        self.MainWindow = MainWindow

        # Variables
        self.InsertAccepted = False
        self.FileName = None
        self.Width = 280
        self.Height = 280

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

        # Buttons
        self.InsertFileButton = QPushButton("Insert")
        self.InsertFileButton.clicked.connect(self.InsertFile)
        self.CancelButton = QPushButton("Cancel")
        self.CancelButton.clicked.connect(self.Cancel)

        # Create, Populate, and Set Layout
        self.Layout = QGridLayout()
        self.SearchLayout = QGridLayout()
        self.SearchLayout.addWidget(self.SearchLineEdit, 0, 0)
        self.SearchLayout.addWidget(self.MatchCaseCheckBox, 0, 1)
        self.Layout.addLayout(self.SearchLayout, 0, 0)
        self.Layout.addWidget(self.FileList, 1, 0)
        self.ButtonLayout = QGridLayout()
        self.ButtonLayout.addWidget(self.InsertFileButton, 0, 0)
        self.ButtonLayout.addWidget(self.CancelButton, 0, 1)
        self.Layout.addLayout(self.ButtonLayout, 2, 0)
        self.setLayout(self.Layout)

        # Set Window Title and Icon
        self.setWindowTitle("Link File")
        self.setWindowIcon(self.MainWindow.WindowIcon)

        # Window Resize
        self.Resize()

        # Populate File List
        self.PopulateFileList()

        # Execute Dialog
        self.exec()

    def PopulateFileList(self):
        SearchTerm = self.SearchLineEdit.text()
        MatchCase = self.MatchCaseCheckBox.isChecked()
        if not MatchCase:
            SearchTerm = SearchTerm.lower()
        self.FileList.clear()
        Files = sorted(self.Notebook.Files.keys(), key=lambda File: File[0].lower())
        if SearchTerm != "":
            Files = [File for File in Files if SearchTerm in (File.lower() if not MatchCase else File)]
        for FileName in Files:
            self.FileList.addItem(FileListItem(FileName))
        self.FileList.setCurrentRow(0)

    def InsertFile(self):
        SelectedItems = self.FileList.selectedItems()
        if len(SelectedItems) < 1:
            return
        self.FileName = SelectedItems[0].FileName
        self.InsertAccepted = True
        self.close()

    def Cancel(self):
        self.close()

    def Resize(self):
        self.resize(self.Width, self.Height)


class FileListItem(QListWidgetItem):
    def __init__(self, FileName):
        super().__init__()

        self.FileName = FileName

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
