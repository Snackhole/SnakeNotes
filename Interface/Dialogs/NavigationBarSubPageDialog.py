from PyQt5.QtWidgets import QDialog, QListWidget, QListWidgetItem, QGridLayout, QPushButton, QLabel


class NavigationBarSubPageDialog(QDialog):
    def __init__(self, Page, SubPages, MainWindow):
        super().__init__(parent=MainWindow)

        # Store Parameters
        self.Page = Page
        self.SubPages = SubPages
        self.MainWindow = MainWindow

        # Variables
        self.SelectedSubPage = None
        self.Width = 250
        self.Height = 250

        # Prompt
        self.PromptLabel = QLabel("Go to sub page of " + self.Page["Title"] + "?")
        self.PromptLabel.setWordWrap(True)

        # Sub Page List
        self.SubPageList = QListWidget()
        self.SubPageList.itemActivated.connect(self.Go)

        # Buttons
        self.GoButton = QPushButton("Go")
        self.GoButton.clicked.connect(self.Go)
        self.CancelButton = QPushButton("Cancel")
        self.CancelButton.clicked.connect(self.Cancel)

        # Create, Populate, and Set Layout
        self.Layout = QGridLayout()
        self.Layout.addWidget(self.PromptLabel, 0, 0, 1, 2)
        self.Layout.addWidget(self.SubPageList, 1, 0, 1, 2)
        self.Layout.addWidget(self.GoButton, 2, 0)
        self.Layout.addWidget(self.CancelButton, 2, 1)
        self.setLayout(self.Layout)

        # Set Window Title and Icon
        self.setWindowTitle("Go to Sub Page")
        self.setWindowIcon(self.MainWindow.WindowIcon)

        # Window Resize
        self.Resize()

        # Populate Favorites List
        self.PopulateSubPageList()

        # Execute Menu
        self.exec_()

    def Go(self):
        SelectedItems = self.SubPageList.selectedItems()
        if len(SelectedItems) > 0:
            self.SelectedSubPage = SelectedItems[0].SubPage
            self.close()

    def Cancel(self):
        self.close()

    def Resize(self):
        self.resize(self.Width, self.Height)

    def PopulateSubPageList(self):
        for SubPage in self.SubPages:
            self.SubPageList.addItem(SubPageItem(SubPage))
        if self.SubPageList.count() > 0:
            self.SubPageList.setCurrentRow(0)
            self.SubPageList.setFocus()


class SubPageItem(QListWidgetItem):
    def __init__(self, SubPage):
        super().__init__()

        # Store Parameters
        self.SubPage = SubPage

        # Set Text
        self.setText(self.SubPage["Title"])
