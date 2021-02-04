from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QScrollArea, QSplitter

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

        # Image List
        self.ImageList = QListWidget()
        self.ImageList.itemSelectionChanged.connect(self.ItemSelected)

        # Image Display
        self.ImageDisplay = QLabel()

        # Buttons
        self.InsertImageButton = QPushButton("Insert")
        self.InsertImageButton.clicked.connect(self.InsertImage)
        self.CancelButton = QPushButton("Cancel")
        self.CancelButton.clicked.connect(self.Cancel)

        # Create, Populate, and Set Layout
        self.ImageDisplayScrollArea = QScrollArea()
        self.ImageDisplayScrollArea.setWidget(self.ImageDisplay)

        self.Splitter = QSplitter()
        self.Splitter.addWidget(self.ImageList)
        self.Splitter.addWidget(self.ImageDisplayScrollArea)
        self.Splitter.setStretchFactor(1, 1)

        self.ButtonLayout = QGridLayout()
        self.ButtonLayout.addWidget(self.InsertImageButton, 0, 0)
        self.ButtonLayout.addWidget(self.CancelButton, 0, 1)

        self.Layout = QGridLayout()
        self.Layout.addWidget(self.Splitter, 0, 0)
        self.Layout.addLayout(self.ButtonLayout, 1, 0)
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
        self.ImageList.clear()
        self.ImageDisplay.clear()
        for FileName, Base64String in sorted(self.Notebook.Images.items(), key=lambda Image: Image[0].lower()):
            self.ImageList.addItem(ImageListItem(FileName, Base64String))
        self.ImageList.setCurrentRow(0)
        self.ImageList.setFocus()

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
