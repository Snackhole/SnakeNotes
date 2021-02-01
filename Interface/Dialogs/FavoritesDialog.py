import os

from PyQt5.QtWidgets import QDialog, QInputDialog, QListWidget, QPushButton, QGridLayout, QListWidgetItem, QMessageBox


class FavoritesDialog(QDialog):
    def __init__(self, FavoritesData, MainWindow):
        super().__init__(parent=MainWindow)

        # Store Parameters
        self.FavoritesData = FavoritesData
        self.MainWindow = MainWindow

        # Variables
        self.OpenFilePath = None
        self.Width = 250
        self.Height = 250

        # Favorites List
        self.FavoritesList = QListWidget()
        self.FavoritesList.itemDoubleClicked.connect(self.OpenFavorite)

        # Buttons
        self.AddCurrentNotebookAsFavoriteButton = QPushButton("Add Current Notebook as Favorite")
        self.AddCurrentNotebookAsFavoriteButton.clicked.connect(self.AddCurrentNotebookAsFavorite)
        self.OpenFavoriteButton = QPushButton("Open Favorite")
        self.OpenFavoriteButton.clicked.connect(self.OpenFavorite)
        self.OpenFavoriteButton.setDefault(True)
        self.DeleteFavoriteButton = QPushButton("Delete Favorite")
        self.DeleteFavoriteButton.clicked.connect(self.DeleteFavorite)
        self.DoneButton = QPushButton("Done")
        self.DoneButton.clicked.connect(self.Done)

        # Create, Populate, and Set Layout
        self.Layout = QGridLayout()
        self.Layout.addWidget(self.FavoritesList, 0, 0, 1, 3)
        self.Layout.addWidget(self.AddCurrentNotebookAsFavoriteButton, 1, 0, 1, 3)
        self.Layout.addWidget(self.OpenFavoriteButton, 2, 0)
        self.Layout.addWidget(self.DeleteFavoriteButton, 2, 1)
        self.Layout.addWidget(self.DoneButton, 2, 2)
        self.setLayout(self.Layout)

        # Set Window Title and Icon
        self.setWindowTitle("Favorites")
        self.setWindowIcon(self.MainWindow.WindowIcon)

        # Window Resize
        self.Resize()

        # Populate Favorites List
        self.PopulateFavoritesList()

        # Execute Menu
        self.exec_()

    def OpenFavorite(self):
        SelectedItems = self.FavoritesList.selectedItems()
        if len(SelectedItems) > 0:
            if not os.path.isfile(SelectedItems[0].FavoritePath):
                self.MainWindow.DisplayMessageBox(SelectedItems[0].FavoriteName + " is not a notebook file.\n\nCheck whether it has been moved, deleted, or renamed.")
                return
            self.OpenFilePath = SelectedItems[0].FavoritePath
            self.close()

    def AddCurrentNotebookAsFavorite(self):
        CurrentOpenFileName = self.MainWindow.CurrentOpenFileName
        if CurrentOpenFileName == "":
            self.MainWindow.DisplayMessageBox("Save or open a notebook first.")
            return
        CurrentModeExtension = ".ntbk" if not self.MainWindow.GzipMode else ".ntbk.gz"
        if not CurrentOpenFileName.endswith(CurrentModeExtension):
            self.MainWindow.DisplayMessageBox("The current file must be saved as a " + CurrentModeExtension + " file before it can be added to your favorites for the current mode.")
            return
        CurrentOpenFileNameShort = os.path.basename(CurrentOpenFileName)[:-len(CurrentModeExtension)]
        FavoriteName, OK = QInputDialog.getText(self, "Name Favorite", "Enter a name:", text=CurrentOpenFileNameShort)
        if OK:
            if FavoriteName == "":
                self.MainWindow.DisplayMessageBox("Favorite names cannot be blank.")
                return
            if FavoriteName in self.FavoritesData:
                if self.MainWindow.DisplayMessageBox("There is already a notebook called " + FavoriteName + " in your favorites.\n\nOverwrite?", Icon=QMessageBox.Question, Buttons=(QMessageBox.Yes | QMessageBox.No)) == QMessageBox.No:
                    return
            self.FavoritesData[FavoriteName] = CurrentOpenFileName
            self.PopulateFavoritesList()

    def DeleteFavorite(self):
        SelectedItems = self.FavoritesList.selectedItems()
        if len(SelectedItems) > 0:
            if self.MainWindow.DisplayMessageBox("Delete " + SelectedItems[0].FavoriteName + " from your favorites?", Icon=QMessageBox.Question, Buttons=(QMessageBox.Yes | QMessageBox.No)) == QMessageBox.Yes:
                del self.FavoritesData[SelectedItems[0].FavoriteName]
                self.PopulateFavoritesList()

    def Done(self):
        self.close()

    def Resize(self):
        self.resize(self.Width, self.Height)

    def PopulateFavoritesList(self):
        self.FavoritesList.clear()
        for FavoriteName, FavoritePath in sorted(self.FavoritesData.items()):
            self.FavoritesList.addItem(FavoritesItem(FavoriteName, FavoritePath))
        if self.FavoritesList.count() > 0:
            self.FavoritesList.setCurrentRow(0)
            self.FavoritesList.setFocus()


class FavoritesItem(QListWidgetItem):
    def __init__(self, FavoriteName, FavoritePath):
        super().__init__()

        # Store Parameters
        self.FavoriteName = FavoriteName
        self.FavoritePath = FavoritePath

        # Set Text
        self.setText(self.FavoriteName)
