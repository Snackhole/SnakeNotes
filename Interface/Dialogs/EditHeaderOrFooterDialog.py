from PyQt5.QtWidgets import QDialog, QGridLayout, QTextEdit, QPushButton


class EditHeaderOrFooterDialog(QDialog):
    def __init__(self, Mode, Notebook, MainWindow):
        super().__init__(parent=MainWindow)

        # Store Parameters
        self.Mode = Mode
        self.Notebook = Notebook
        self.MainWindow = MainWindow

        # Variables
        self.UnsavedChanges = False
        self.HeaderOrFooterString = None
        self.Width = max(self.MainWindow.width() - 100, 100)
        self.Height = max(self.MainWindow.height() - 100, 100)

        # Header or Footer Text
        self.HeaderOrFooterText = QTextEdit()
        self.HeaderOrFooterText.setTabChangesFocus(True)
        self.HeaderOrFooterText.setStyleSheet("selection-background-color: rgb(0, 120, 215); selection-color: white")
        self.HeaderOrFooterText.setPlainText(self.Notebook.Header if self.Mode == "Header" else (self.Notebook.Footer if self.Mode == "Footer" else ""))

        # Edit Buttons
        self.PageTitleButton = QPushButton("Page Title")
        self.PageTitleButton.clicked.connect(self.PageTitle)
        self.SubPagesButton = QPushButton("Sub Pages Links")
        self.SubPagesButton.clicked.connect(self.SubPages)
        self.SubPageOfButton = QPushButton("Sub Page Of Link")
        self.SubPageOfButton.clicked.connect(self.SubPageOf)
        self.LinkingPagesButton = QPushButton("Linking Pages Links")
        self.LinkingPagesButton.clicked.connect(self.LinkingPages)
        self.DefaultButton = QPushButton("Default")
        self.DefaultButton.clicked.connect(self.Default)

        # Buttons
        self.DoneButton = QPushButton("Done")
        self.DoneButton.clicked.connect(self.Done)
        self.CancelButton = QPushButton("Cancel")
        self.CancelButton.clicked.connect(self.Cancel)

        # Create, Populate, and Set Layout
        self.EditLayout = QGridLayout()
        self.EditLayout.addWidget(self.PageTitleButton, 0, 0)
        self.EditLayout.addWidget(self.SubPagesButton, 0, 1)
        self.EditLayout.addWidget(self.SubPageOfButton, 0, 2)
        self.EditLayout.addWidget(self.LinkingPagesButton, 0, 3)
        self.EditLayout.addWidget(self.DefaultButton, 0, 4)
        self.ButtonsLayout = QGridLayout()
        self.ButtonsLayout.addWidget(self.DoneButton, 0, 0)
        self.ButtonsLayout.addWidget(self.CancelButton, 0, 1)
        self.Layout = QGridLayout()
        self.Layout.addLayout(self.EditLayout, 0, 0)
        self.Layout.addWidget(self.HeaderOrFooterText, 1, 0)
        self.Layout.addLayout(self.ButtonsLayout, 2, 0)
        self.setLayout(self.Layout)

        # Set Window Title and Icon
        self.setWindowTitle(f"Edit {Mode}")
        self.setWindowIcon(self.MainWindow.WindowIcon)

        # Window Resize
        self.Resize()

        # Focus on Text
        self.HeaderOrFooterText.setFocus()

        # Execute Dialog
        self.exec_()

    def Done(self):
        self.HeaderOrFooterString = self.HeaderOrFooterText.toPlainText()
        self.UnsavedChanges = True
        self.close()

    def Cancel(self):
        self.close()

    def PageTitle(self):
        self.HeaderOrFooterText.insertPlainText("{PAGETITLE}")

    def SubPages(self):
        self.HeaderOrFooterText.insertPlainText("{SUBPAGELINKS}")

    def SubPageOf(self):
        self.HeaderOrFooterText.insertPlainText("{SUBPAGEOFLINK}")

    def LinkingPages(self):
        self.HeaderOrFooterText.insertPlainText("{LINKINGPAGES}")

    def Default(self):
        self.HeaderOrFooterText.setPlainText(self.Notebook.DefaultHeader if self.Mode == "Header" else (self.Notebook.DefaultFooter if self.Mode == "Footer" else ""))

    def Resize(self):
        self.resize(self.Width, self.Height)
