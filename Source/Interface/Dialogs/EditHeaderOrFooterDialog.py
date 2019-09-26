from PyQt5.QtWidgets import QDialog, QGridLayout, QTextEdit, QPushButton


class EditHeaderOrFooterDialog(QDialog):
    def __init__(self, Mode, RootPage, Icon, Parent):
        super().__init__(parent=Parent)

        # Store Parameters
        self.Mode = Mode
        self.RootPage = RootPage
        self.Icon = Icon
        self.Parent = Parent

        # Variables
        self.UnsavedChanges = False
        self.HeaderOrFooterString = None
        self.Width = max(self.Parent.width() - 100, 100)
        self.Height = max(self.Parent.height() - 100, 100)

        # Header or Footer Text
        self.HeaderOrFooterText = QTextEdit()
        self.HeaderOrFooterText.setTabChangesFocus(True)
        self.HeaderOrFooterText.setStyleSheet("selection-background-color: rgb(0, 120, 215); selection-color: white")
        self.HeaderOrFooterText.setPlainText(self.RootPage.Header if self.Mode == "Header" else (self.RootPage.Footer if self.Mode == "Footer" else ""))

        # Edit Buttons
        self.PageTitleButton = QPushButton("Page Title")
        self.PageTitleButton.clicked.connect(self.PageTitle)
        self.SubPagesButton = QPushButton("Sub Pages Links")
        self.SubPagesButton.clicked.connect(self.SubPages)
        self.SubPageOfButton = QPushButton("Sub Page Of Link")
        self.SubPageOfButton.clicked.connect(self.SubPageOf)

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
        self.ButtonsLayout = QGridLayout()
        self.ButtonsLayout.addWidget(self.DoneButton, 0, 0)
        self.ButtonsLayout.addWidget(self.CancelButton, 0, 1)
        self.Layout = QGridLayout()
        self.Layout.addLayout(self.EditLayout, 0, 0)
        self.Layout.addWidget(self.HeaderOrFooterText, 1, 0)
        self.Layout.addLayout(self.ButtonsLayout, 2, 0)
        self.setLayout(self.Layout)

        # Set Window Title and Icon
        self.setWindowTitle("Edit " + Mode)
        self.setWindowIcon(self.Icon)

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

    def Resize(self):
        self.resize(self.Width, self.Height)
