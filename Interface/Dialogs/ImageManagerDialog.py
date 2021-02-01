import os
from PyQt5 import QtCore

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog, QFrame, QGridLayout, QListWidget, QPushButton, QListWidgetItem, QLabel, QFileDialog, QMessageBox, QScrollArea, QSplitter, QInputDialog

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

        # Image List
        self.ImageList = QListWidget()
        self.ImageList.itemSelectionChanged.connect(self.ItemSelected)

        # Linking Pages Frame
        self.LinkingPagesFrame = QFrame()

        # Linking Pages Label
        self.LinkingPagesLabel = QLabel("Linking Pages")
        self.LinkingPagesLabel.setAlignment(QtCore.Qt.AlignHCenter)

        # Linking Pages List
        self.LinkingPagesList = QListWidget()

        # Image Display
        self.ImageDisplay = QLabel()

        # Buttons
        self.AddImageButton = QPushButton("Add")
        self.AddImageButton.clicked.connect(self.AddImage)
        self.RenameImageButton = QPushButton("Rename")
        self.RenameImageButton.clicked.connect(self.RenameImage)
        self.ExportImageButton = QPushButton("Export")
        self.ExportImageButton.clicked.connect(self.ExportImage)
        self.DeleteImageButton = QPushButton("Delete")
        self.DeleteImageButton.clicked.connect(self.DeleteImage)
        self.DoneButton = QPushButton("Done")
        self.DoneButton.clicked.connect(self.Done)

        # Create, Populate, and Set Layout
        self.ImageDisplayScrollArea = QScrollArea()
        self.ImageDisplayScrollArea.setWidget(self.ImageDisplay)

        self.LinkingPagesLayout = QGridLayout()
        self.LinkingPagesLayout.addWidget(self.LinkingPagesLabel, 0, 0)
        self.LinkingPagesLayout.addWidget(self.LinkingPagesList, 1, 0)
        self.LinkingPagesFrame.setLayout(self.LinkingPagesLayout)

        self.Splitter = QSplitter()
        self.Splitter.addWidget(self.ImageList)
        self.Splitter.addWidget(self.ImageDisplayScrollArea)
        self.Splitter.addWidget(self.LinkingPagesFrame)
        self.Splitter.setStretchFactor(1, 1)

        self.ButtonLayout = QGridLayout()
        self.ButtonLayout.addWidget(self.AddImageButton, 0, 0)
        self.ButtonLayout.addWidget(self.RenameImageButton, 0, 1)
        self.ButtonLayout.addWidget(self.ExportImageButton, 0, 2)
        self.ButtonLayout.addWidget(self.DeleteImageButton, 0, 3)
        self.ButtonLayout.addWidget(self.DoneButton, 0, 4)

        self.Layout = QGridLayout()
        self.Layout.addWidget(self.Splitter, 0, 0)
        self.Layout.addLayout(self.ButtonLayout, 1, 0)
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
            SearchTerm = "](" + CurrentFileName + ")"
            SearchResults = self.Notebook.GetSearchResults(SearchTerm, MatchCase=True)
            self.LinkingPagesList.clear()
            for Result in SearchResults:
                LinkingPagesListItem = QListWidgetItem(Result[0])
                self.LinkingPagesList.addItem(LinkingPagesListItem)

    def PopulateImageList(self):
        self.ImageList.clear()
        self.ImageDisplay.clear()
        for FileName, Base64String in sorted(self.Notebook.Images.items(), key=lambda Image: Image[0].lower()):
            self.ImageList.addItem(ImageListItem(FileName, Base64String))
        self.ImageList.setCurrentRow(0)
        self.ImageList.setFocus()

    def AddImage(self):
        AttachNewFile = False
        ImageFilePath = QFileDialog.getOpenFileName(caption="Attach Image File", filter="Images (*.jpg *.jpeg *.png *.gif *.bmp)")[0]
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
            self.PopulateImageList()
            self.ImageList.setCurrentRow(self.GetImageIndexFromName(os.path.basename(ImageFilePath)))

    def RenameImage(self):
        SelectedItems = self.ImageList.selectedItems()
        if len(SelectedItems) > 0:
            CurrentFileNameParts = os.path.splitext(SelectedItems[0].FileName)
            CurrentFileName = CurrentFileNameParts[0]
            CurrentFileExtension = CurrentFileNameParts[1]
            NewName, OK = QInputDialog.getText(self, "Rename " + CurrentFileName, "Enter a name:", text=CurrentFileName)
            if OK:
                if NewName == "":
                    self.MainWindow.DisplayMessageBox("Image names cannot be blank.")
                elif NewName + CurrentFileExtension in self.Notebook.Images:
                    self.MainWindow.DisplayMessageBox("There is already an image by that name.")
                else:
                    ImageContent = self.Notebook.Images[CurrentFileName + CurrentFileExtension]
                    self.Notebook.Images[NewName + CurrentFileExtension] = ImageContent
                    del self.Notebook.Images[CurrentFileName + CurrentFileExtension]
                    self.MainWindow.SearchWidgetInst.ReplaceAllInNotebook(SearchText="](" + CurrentFileName + CurrentFileExtension + ")", ReplaceText="](" + NewName + CurrentFileExtension + ")", MatchCase=True)
                    self.UnsavedChanges = True
                    self.PopulateImageList()
                    self.ImageList.setCurrentRow(self.GetImageIndexFromName(NewName + CurrentFileExtension))

    def ExportImage(self):
        SelectedItems = self.ImageList.selectedItems()
        if len(SelectedItems) > 0:
            CurrentFileName = SelectedItems[0].FileName
            CurrentFileExtension = os.path.splitext(CurrentFileName)[1]
            ExportImagePath = QFileDialog.getSaveFileName(parent=self, caption="Export Image File", filter=self.ExportFilters[CurrentFileExtension])[0]
            if ExportImagePath != "":
                Base64Converters.WriteFileFromBase64String(SelectedItems[0].Base64String, ExportImagePath)

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
