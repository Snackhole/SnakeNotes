import os

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QCheckBox, QDialog, QFrame, QGridLayout, QLineEdit, QListWidget, QPushButton, QListWidgetItem, QLabel, QFileDialog, QMessageBox, QScrollArea, QSizePolicy, QSplitter, QInputDialog

from Core import Base64Converters


class ImageManagerDialog(QDialog):
    def __init__(self, Notebook, MainWindow):
        super().__init__(parent=MainWindow)

        # Store Parameters
        self.Notebook = Notebook
        self.MainWindow = MainWindow

        # Variables
        self.UnsavedChanges = False
        self.ExportFilters = {}
        self.ExportFilters[".jpeg"] = "JPEG (*.jpeg)"
        self.ExportFilters[".jpg"] = "JPG (*.jpg)"
        self.ExportFilters[".png"] = "PNG (*.png)"
        self.ExportFilters[".gif"] = "GIF (*.gif)"
        self.ExportFilters[".bmp"] = "BMP (*.bmp)"
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

        # Linking Pages Frame
        self.LinkingPagesFrame = QFrame()

        # Linking Pages Label
        self.LinkingPagesLabel = QLabel("Linking Pages")
        self.LinkingPagesLabel.setAlignment(Qt.AlignHCenter)

        # Linking Pages List
        self.LinkingPagesList = QListWidget()

        # Image Display
        self.ImageDisplay = QLabel()
        self.ImageDisplayScrollArea = QScrollArea()
        self.ImageDisplayScrollArea.setWidget(self.ImageDisplay)
        self.ImageDisplayScrollArea.setAlignment(Qt.AlignCenter)

        # Buttons
        self.AddImageButton = QPushButton("Add Image")
        self.AddImageButton.clicked.connect(self.AddImage)
        self.AddMultipleImagesButton = QPushButton("Add Multiple Images")
        self.AddMultipleImagesButton.clicked.connect(self.AddMultipleImages)
        self.RenameImageButton = QPushButton("Rename Image")
        self.RenameImageButton.clicked.connect(self.RenameImage)
        self.RenameImageButton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.ExportImageButton = QPushButton("Export Image")
        self.ExportImageButton.clicked.connect(self.ExportImage)
        self.ExportAllImagesButton = QPushButton("Export All Images")
        self.ExportAllImagesButton.clicked.connect(self.ExportAllImages)
        self.DeleteImageButton = QPushButton("Delete Image")
        self.DeleteImageButton.clicked.connect(self.DeleteImage)
        self.DeleteAllImagesButton = QPushButton("Delete All Images")
        self.DeleteAllImagesButton.clicked.connect(self.DeleteAllImages)
        self.DoneButton = QPushButton("Done")
        self.DoneButton.clicked.connect(self.Done)
        self.DoneButton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        # Create, Populate, and Set Layout
        self.Layout = QGridLayout()
        self.SearchLayout = QGridLayout()
        self.SearchLayout.addWidget(self.SearchLineEdit, 0, 0)
        self.SearchLayout.addWidget(self.MatchCaseCheckBox, 0, 1)
        self.Layout.addLayout(self.SearchLayout, 0, 0)
        self.Splitter = QSplitter()
        self.Splitter.addWidget(self.ImageList)
        self.Splitter.addWidget(self.ImageDisplayScrollArea)
        self.LinkingPagesLayout = QGridLayout()
        self.LinkingPagesLayout.addWidget(self.LinkingPagesLabel, 0, 0)
        self.LinkingPagesLayout.addWidget(self.LinkingPagesList, 1, 0)
        self.LinkingPagesFrame.setLayout(self.LinkingPagesLayout)
        self.Splitter.addWidget(self.LinkingPagesFrame)
        self.Splitter.setStretchFactor(1, 1)
        self.Layout.addWidget(self.Splitter, 1, 0)
        self.ButtonLayout = QGridLayout()
        self.ButtonLayout.addWidget(self.AddImageButton, 0, 0)
        self.ButtonLayout.addWidget(self.AddMultipleImagesButton, 1, 0)
        self.ButtonLayout.addWidget(self.ExportImageButton, 0, 1)
        self.ButtonLayout.addWidget(self.ExportAllImagesButton, 1, 1)
        self.ButtonLayout.addWidget(self.DeleteImageButton, 0, 2)
        self.ButtonLayout.addWidget(self.DeleteAllImagesButton, 1, 2)
        self.ButtonLayout.addWidget(self.RenameImageButton, 0, 3, 2, 1)
        self.ButtonLayout.addWidget(self.DoneButton, 0, 4, 2, 1)
        self.Layout.addLayout(self.ButtonLayout, 2, 0)
        self.setLayout(self.Layout)

        # Set Window Title and Icon
        self.setWindowTitle("Image Manager")
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
            CurrentFileName = SelectedItems[0].FileName
            SearchTerm = "](" + CurrentFileName
            SearchResults = self.Notebook.GetSearchResults(SearchTerm, MatchCase=True)
            self.LinkingPagesList.clear()
            for Result in SearchResults["ResultsList"]:
                LinkingPagesListItem = QListWidgetItem(Result[0])
                self.LinkingPagesList.addItem(LinkingPagesListItem)

    def PopulateImageList(self):
        SearchTerm = self.SearchLineEdit.text()
        MatchCase = self.MatchCaseCheckBox.isChecked()
        if not MatchCase:
            SearchTerm = SearchTerm.lower()
        self.ImageList.clear()
        self.ImageDisplay.clear()
        self.ImageDisplay.resize(QSize(0, 0))
        self.LinkingPagesList.clear()
        Images = sorted(self.Notebook.Images.items(), key=lambda Image: Image[0].lower())
        if SearchTerm != "":
            Images = [Image for Image in Images if SearchTerm in (Image[0].lower() if not MatchCase else Image[0])]
        for FileName, Base64String in Images:
            self.ImageList.addItem(ImageListItem(FileName, Base64String))
        self.ImageList.setCurrentRow(0)

    def AddImage(self):
        AttachNewFile = False
        ImageFilePath = QFileDialog.getOpenFileName(parent=self, caption="Attach Image File", filter="Images (*.jpg *.jpeg *.png *.gif *.bmp)")[0]
        if ImageFilePath != "":
            ImageFileName = os.path.basename(ImageFilePath)
            if self.Notebook.HasImage(ImageFileName):
                if self.MainWindow.DisplayMessageBox("A file named \"" + ImageFileName + "\" is already attached to the notebook.\n\nOverwrite existing file?", Icon=QMessageBox.Question, Buttons=(QMessageBox.Yes | QMessageBox.No), Parent=self) == QMessageBox.Yes:
                    AttachNewFile = True
            else:
                AttachNewFile = True
        if AttachNewFile:
            self.Notebook.AddImage(ImageFilePath)
            self.UnsavedChanges = True
            self.SearchLineEdit.clear()
            self.PopulateImageList()
            self.ImageList.setCurrentRow(self.GetImageIndexFromName(os.path.basename(ImageFilePath)))

    def AddMultipleImages(self):
        ImageFilePaths = QFileDialog.getOpenFileNames(parent=self, caption="Attach Image Files", filter="Images (*.jpg *.jpeg *.png *.gif *.bmp)")[0]
        ImageAdded = False
        for ImageFilePath in ImageFilePaths:
            AttachNewFile = False
            ImageFileName = os.path.basename(ImageFilePath)
            if self.Notebook.HasImage(ImageFileName):
                if self.MainWindow.DisplayMessageBox("A file named \"" + ImageFileName + "\" is already attached to the notebook.\n\nOverwrite existing file?", Icon=QMessageBox.Question, Buttons=(QMessageBox.Yes | QMessageBox.No), Parent=self) == QMessageBox.Yes:
                    AttachNewFile = True
            else:
                AttachNewFile = True
            if AttachNewFile:
                self.Notebook.AddImage(ImageFilePath)
                ImageAdded = True
        if ImageAdded:
            self.UnsavedChanges = True
            self.SearchLineEdit.clear()
            self.PopulateImageList()

    def RenameImage(self):
        SelectedItems = self.ImageList.selectedItems()
        if len(SelectedItems) > 0:
            CurrentFileNameParts = os.path.splitext(SelectedItems[0].FileName)
            CurrentFileName = CurrentFileNameParts[0]
            CurrentFileExtension = CurrentFileNameParts[1]
            NewName, OK = QInputDialog.getText(self, "Rename " + CurrentFileName, "Enter a name:", text=CurrentFileName)
            if OK:
                if NewName == "":
                    self.MainWindow.DisplayMessageBox("Image names cannot be blank.", Parent=self)
                elif NewName + CurrentFileExtension in self.Notebook.Images:
                    self.MainWindow.DisplayMessageBox("There is already an image by that name.", Parent=self)
                else:
                    ImageContent = self.Notebook.Images[CurrentFileName + CurrentFileExtension]
                    self.Notebook.Images[NewName + CurrentFileExtension] = ImageContent
                    del self.Notebook.Images[CurrentFileName + CurrentFileExtension]
                    self.MainWindow.SearchWidgetInst.ReplaceAllInNotebook(SearchText="](" + CurrentFileName + CurrentFileExtension, ReplaceText="](" + NewName + CurrentFileExtension, MatchCase=True)
                    self.UnsavedChanges = True
                    self.SearchLineEdit.clear()
                    self.PopulateImageList()
                    self.ImageList.setCurrentRow(self.GetImageIndexFromName(NewName + CurrentFileExtension))

    def ExportImage(self):
        SelectedItems = self.ImageList.selectedItems()
        if len(SelectedItems) > 0:
            CurrentFileName = SelectedItems[0].FileName
            CurrentFileExtension = os.path.splitext(CurrentFileName)[1]
            ExportImagePath = QFileDialog.getSaveFileName(parent=self, caption="Export Image File", filter=self.ExportFilters[CurrentFileExtension])[0]
            if ExportImagePath != "":
                if not ExportImagePath.endswith(CurrentFileExtension):
                    ExportImagePath += CurrentFileExtension
                Base64Converters.WriteFileFromBase64String(SelectedItems[0].Base64String, ExportImagePath)

    def ExportAllImages(self):
        ExportDirectory = QFileDialog.getExistingDirectory(parent=self, caption="Export All Image Files")
        ExportDirectoryContents = os.listdir(ExportDirectory)
        if len(ExportDirectoryContents) == 0:
            for Image in self.Notebook.Images.keys():
                ExportImagePath = os.path.join(ExportDirectory, Image)
                Base64Converters.WriteFileFromBase64String(self.Notebook.Images[Image], ExportImagePath)
        else:
            self.MainWindow.DisplayMessageBox("Choose an empty folder to export all image files.", Parent=self)

    def DeleteImage(self):
        SelectedItems = self.ImageList.selectedItems()
        if len(SelectedItems) > 0:
            CurrentFileName = SelectedItems[0].FileName
            CurrentImageRow = self.ImageList.currentRow()
            if self.MainWindow.DisplayMessageBox("Are you sure you want to delete " + CurrentFileName + " from the notebook?  This cannot be undone.", Icon=QMessageBox.Question, Buttons=(QMessageBox.Yes | QMessageBox.No), Parent=self) == QMessageBox.Yes:
                del self.Notebook.Images[CurrentFileName]
                self.UnsavedChanges = True
                self.PopulateImageList()
                if self.ImageList.count() == 0:
                    pass
                elif CurrentImageRow == self.ImageList.count():
                    self.ImageList.setCurrentRow(CurrentImageRow - 1)
                else:
                    self.ImageList.setCurrentRow(CurrentImageRow)

    def DeleteAllImages(self):
        if self.MainWindow.DisplayMessageBox("Are you sure you want to delete all images from the notebook?  This cannot be undone.", Icon=QMessageBox.Warning, Buttons=(QMessageBox.Yes | QMessageBox.No), Parent=self) == QMessageBox.Yes:
            self.Notebook.Images.clear()
            self.UnsavedChanges = True
            self.PopulateImageList()

    def GetImageIndexFromName(self, ImageName):
        ImageNames = sorted(self.Notebook.Images.keys(), key=lambda Image: Image.lower())
        return ImageNames.index(ImageName)

    def Done(self):
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
