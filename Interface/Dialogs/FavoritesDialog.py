import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QInputDialog, QListWidget, QPushButton, QGridLayout, QListWidgetItem, QMessageBox, QLineEdit, QCheckBox


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

        # Search Line Edit
        self.SearchLineEdit = SearchLineEdit(self)
        self.SearchLineEdit.setPlaceholderText("Search")
        self.SearchLineEdit.textChanged.connect(self.PopulateFavoritesList)
        self.SearchLineEdit.setFocus()

        # Match Case Check Box
        self.MatchCaseCheckBox = QCheckBox("Match Case")
        self.MatchCaseCheckBox.stateChanged.connect(self.PopulateFavoritesList)

        # Favorites List
        self.FavoritesList = FavoritesList(self)
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
        self.SearchLayout = QGridLayout()
        self.SearchLayout.addWidget(self.SearchLineEdit, 0, 0)
        self.SearchLayout.addWidget(self.MatchCaseCheckBox, 0, 1)
        self.Layout.addLayout(self.SearchLayout, 0, 0, 1, 3)
        self.Layout.addWidget(self.FavoritesList, 1, 0, 1, 3)
        self.Layout.addWidget(self.AddCurrentNotebookAsFavoriteButton, 2, 0, 1, 3)
        self.Layout.addWidget(self.OpenFavoriteButton, 3, 0)
        self.Layout.addWidget(self.DeleteFavoriteButton, 3, 1)
        self.Layout.addWidget(self.DoneButton, 3, 2)
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
                self.MainWindow.DisplayMessageBox(f"\"{SelectedItems[0].FavoriteName}\" is not a notebook file.\n\nCheck whether it has been moved, deleted, or renamed.", Parent=self)
                return
            self.OpenFilePath = SelectedItems[0].FavoritePath
            self.close()

    def AddCurrentNotebookAsFavorite(self):
        CurrentOpenFileName = self.MainWindow.CurrentOpenFileName
        if CurrentOpenFileName == "":
            self.MainWindow.DisplayMessageBox("Save or open a notebook first.", Parent=self)
            return
        CurrentModeExtension = ".ntbk" if not self.MainWindow.GzipMode else ".ntbk.gz"
        if not CurrentOpenFileName.endswith(CurrentModeExtension):
            self.MainWindow.DisplayMessageBox(f"The current file must be saved as a {CurrentModeExtension} file before it can be added to your favorites for the current mode.", Parent=self)
            return
        CurrentOpenFileNameShort = os.path.basename(CurrentOpenFileName)[:-len(CurrentModeExtension)]
        FavoriteName, OK = QInputDialog.getText(self, "Name Favorite", "Enter a name:", text=CurrentOpenFileNameShort)
        if OK:
            if FavoriteName == "":
                self.MainWindow.DisplayMessageBox("Favorite names cannot be blank.", Parent=self)
                return
            if FavoriteName in self.FavoritesData:
                if self.MainWindow.DisplayMessageBox(f"There is already a notebook called \"{FavoriteName}\" in your favorites.\n\nOverwrite?", Icon=QMessageBox.Question, Buttons=(QMessageBox.Yes | QMessageBox.No), Parent=self) == QMessageBox.No:
                    return
            self.FavoritesData[FavoriteName] = CurrentOpenFileName
            self.PopulateFavoritesList()

    def DeleteFavorite(self):
        SelectedItems = self.FavoritesList.selectedItems()
        if len(SelectedItems) > 0:
            if self.MainWindow.DisplayMessageBox(f"Delete \"{SelectedItems[0].FavoriteName}\" from your favorites?", Icon=QMessageBox.Question, Buttons=(QMessageBox.Yes | QMessageBox.No), Parent=self) == QMessageBox.Yes:
                del self.FavoritesData[SelectedItems[0].FavoriteName]
                self.PopulateFavoritesList()

    def Done(self):
        self.close()

    def Resize(self):
        self.resize(self.Width, self.Height)

    def PopulateFavoritesList(self):
        SearchTerm = self.SearchLineEdit.text()
        self.FavoritesList.clear()
        if SearchTerm == "":
            for FavoriteName, FavoritePath in sorted(self.FavoritesData.items()):
                self.FavoritesList.addItem(FavoritesItem(FavoriteName, FavoritePath))
        else:
            MatchCase = self.MatchCaseCheckBox.isChecked()
            SearchResults = {FavoriteName: FavoritePath for FavoriteName, FavoritePath in sorted(self.FavoritesData.items()) if SearchTerm in (FavoriteName.lower() if not MatchCase else FavoriteName)}
            for FavoriteName, FavoritePath in sorted(SearchResults.items()):
                self.FavoritesList.addItem(FavoritesItem(FavoriteName, FavoritePath))
        if self.FavoritesList.count() > 0:
            self.FavoritesList.setCurrentRow(0)


class SearchLineEdit(QLineEdit):
    def __init__(self, Dialog):
        # QLineEdit Init
        super().__init__()

        # Store Parameters
        self.Dialog = Dialog

    def keyPressEvent(self, QKeyEvent):
        KeyPressed = QKeyEvent.key()
        if KeyPressed == Qt.Key_Down:
            self.Dialog.FavoritesList.setFocus()
        else:
            super().keyPressEvent(QKeyEvent)


class FavoritesList(QListWidget):
    def __init__(self, Dialog):
        # QListWidget Init
        super().__init__()

        # Store Parameters
        self.Dialog = Dialog

    def keyPressEvent(self, QKeyEvent):
        KeyPressed = QKeyEvent.key()
        ItemBefore = self.currentItem()
        super().keyPressEvent(QKeyEvent)
        ItemAfter = self.currentItem()
        if ItemBefore == ItemAfter and KeyPressed == Qt.Key_Up:
            self.Dialog.SearchLineEdit.setFocus()


class FavoritesItem(QListWidgetItem):
    def __init__(self, FavoriteName, FavoritePath):
        super().__init__()

        # Store Parameters
        self.FavoriteName = FavoriteName
        self.FavoritePath = FavoritePath

        # Set Text
        self.setText(self.FavoriteName)
