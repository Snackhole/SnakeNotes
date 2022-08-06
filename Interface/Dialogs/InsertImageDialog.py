from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QCheckBox, QDialog, QGridLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QPushButton, QScrollArea, QSplitter

from Core import Base64Converters


class InsertImageDialog(QDialog):
    def __init__(self, Notebook, MainWindow):
        super().__init__(parent=MainWindow)

        # Store Parameters
        self.Notebook = Notebook
        self.MainWindow = MainWindow

        # Variables
        self.InsertAccepted = False
        self.ImageFileName = None
        self.Width = max(self.MainWindow.width() - 100, 100)
        self.Height = max(self.MainWindow.height() - 100, 100)

        # Search Line Edit
        self.SearchLineEdit = SearchLineEdit(self)
        self.SearchLineEdit.setPlaceholderText("Search")
        self.SearchLineEdit.textChanged.connect(self.PopulateImageList)
        self.SearchLineEdit.setFocus()

        # Match Case Check Box
        self.MatchCaseCheckBox = QCheckBox("Match Case")
        self.MatchCaseCheckBox.stateChanged.connect(self.PopulateImageList)

        # Image List
        self.ImageList = ImageList(self)
        self.ImageList.itemSelectionChanged.connect(self.ItemSelected)

        # Image Display
        self.ImageDisplay = QLabel()
        self.ImageDisplayScrollArea = QScrollArea()
        self.ImageDisplayScrollArea.setWidget(self.ImageDisplay)
        self.ImageDisplayScrollArea.setAlignment(Qt.AlignCenter)

        # Buttons
        self.InsertImageButton = QPushButton("Insert")
        self.InsertImageButton.clicked.connect(self.InsertImage)
        self.CancelButton = QPushButton("Cancel")
        self.CancelButton.clicked.connect(self.Cancel)

        # Create, Populate, and Set Layout
        self.Layout = QGridLayout()
        self.SearchLayout = QGridLayout()
        self.SearchLayout.addWidget(self.SearchLineEdit, 0, 0)
        self.SearchLayout.addWidget(self.MatchCaseCheckBox, 0, 1)
        self.Layout.addLayout(self.SearchLayout, 0, 0)
        self.Splitter = QSplitter()
        self.Splitter.addWidget(self.ImageList)
        self.Splitter.addWidget(self.ImageDisplayScrollArea)
        self.Splitter.setStretchFactor(1, 1)
        self.Layout.addWidget(self.Splitter, 1, 0)
        self.ButtonLayout = QGridLayout()
        self.ButtonLayout.addWidget(self.InsertImageButton, 0, 0)
        self.ButtonLayout.addWidget(self.CancelButton, 0, 1)
        self.Layout.addLayout(self.ButtonLayout, 2, 0)
        self.setLayout(self.Layout)

        # Set Window Title and Icon
        self.setWindowTitle("Insert Image")
        self.setWindowIcon(self.MainWindow.WindowIcon)

        # Window Resize
        self.Resize()

        # Populate Image List
        self.PopulateImageList()

        # Execute Dialog
        self.exec_()

    def ItemSelected(self):
        SelectedItems = self.ImageList.selectedItems()
        if len(SelectedItems) > 0:
            CurrentFileContent = SelectedItems[0].Base64String
            CurrentFileBinary = Base64Converters.GetBinaryFromBase64String(CurrentFileContent)
            ImagePixmap = QPixmap()
            ImagePixmap.loadFromData(CurrentFileBinary)
            self.ImageDisplay.setPixmap(ImagePixmap)
            self.ImageDisplay.resize(self.ImageDisplay.pixmap().size())

    def PopulateImageList(self):
        SearchTerm = self.SearchLineEdit.text()
        MatchCase = self.MatchCaseCheckBox.isChecked()
        if not MatchCase:
            SearchTerm = SearchTerm.lower()
        self.ImageList.clear()
        self.ImageDisplay.clear()
        self.ImageDisplay.resize(QSize(0, 0))
        Images = sorted(self.Notebook.Images.items(), key=lambda Image: Image[0].lower())
        if SearchTerm != "":
            Images = [Image for Image in Images if SearchTerm in (Image[0].lower() if not MatchCase else Image[0])]
        for FileName, Base64String in Images:
            self.ImageList.addItem(ImageListItem(FileName, Base64String))
        self.ImageList.setCurrentRow(0)

    def InsertImage(self):
        SelectedItems = self.ImageList.selectedItems()
        if len(SelectedItems) < 1:
            return
        self.ImageFileName = SelectedItems[0].FileName
        self.InsertAccepted = True
        self.close()

    def Cancel(self):
        self.close()

    def Resize(self):
        self.resize(self.Width, self.Height)


class ImageListItem(QListWidgetItem):
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
        if KeyPressed == Qt.Key_Down:
            self.Dialog.ImageList.setFocus()
        else:
            super().keyPressEvent(QKeyEvent)


class ImageList(QListWidget):
    def __init__(self, Dialog):
        # QListWidget Init
        super().__init__()

        # Store Parameters
        self.Dialog = Dialog

    def keyPressEvent(self, QKeyEvent):
        KeyPressed = QKeyEvent.key()
        Row = self.currentRow()
        if KeyPressed == Qt.Key_Up and Row == 0:
            self.Dialog.SearchLineEdit.setFocus()
        else:
            super().keyPressEvent(QKeyEvent)
