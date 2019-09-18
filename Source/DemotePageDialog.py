from PyQt5.QtWidgets import QDialog, QLabel, QComboBox, QPushButton, QGridLayout


class DemotePageDialog(QDialog):
    def __init__(self, CurrentPageName, CurrentPageIndex, ScriptName, Icon, SiblingPageTitles, Parent):
        super().__init__(parent=Parent)

        # Store Parameters
        self.CurrentPageName = CurrentPageName
        self.CurrentPageIndex = CurrentPageIndex
        self.ScriptName = ScriptName
        self.Icon = Icon
        self.SiblingPageTitles = SiblingPageTitles

        # Variables
        self.SiblingPageIndex = None

        # Label
        self.DemotePrompt = QLabel("Demote " + self.CurrentPageName + " to which of its siblings?")

        # Sibling Page Titles Combo Box
        self.SiblingPageTitlesComboBox = QComboBox()
        self.SiblingPageTitlesComboBox.setEditable(False)
        self.SiblingPageTitlesComboBox.addItems(self.SiblingPageTitles)

        # Buttons
        self.DoneButton = QPushButton("Done")
        self.DoneButton.clicked.connect(self.Done)
        self.CancelButton = QPushButton("Cancel")
        self.CancelButton.clicked.connect(self.Cancel)

        # Layout
        self.Layout = QGridLayout()
        self.Layout.addWidget(self.DemotePrompt, 0, 0, 1, 2)
        self.Layout.addWidget(self.SiblingPageTitlesComboBox, 1, 0, 1, 2)
        self.Layout.addWidget(self.DoneButton, 2, 0)
        self.Layout.addWidget(self.CancelButton, 2, 1)
        self.setLayout(self.Layout)

        # Set Window Title and Icon
        self.setWindowTitle(self.ScriptName)
        self.setWindowIcon(self.Icon)

        # Execute Dialog
        self.exec_()

    def Done(self):
        SiblingPageIndex = self.SiblingPageTitlesComboBox.currentIndex()
        if SiblingPageIndex >= self.CurrentPageIndex:
            SiblingPageIndex += 1
        self.SiblingPageIndex = SiblingPageIndex
        self.close()

    def Cancel(self):
        self.close()
