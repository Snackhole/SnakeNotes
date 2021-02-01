from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QGridLayout, QComboBox


class NewPageDialog(QDialog):
    def __init__(self, CurrentPageName, TemplateNames, MainWindow):
        super().__init__(parent=MainWindow)

        # Store Parameters
        self.CurrentPageName = CurrentPageName
        self.TemplateNames = TemplateNames
        self.MainWindow = MainWindow

        # Variables
        self.NewPageAdded = False
        self.NewPageName = ""
        self.TemplateName = ""

        # Labels
        self.PageNamePrompt = QLabel("Add sub page to " + self.CurrentPageName + "?")
        self.PageNameLabel = QLabel("Name:")
        self.TemplateLabel = QLabel("Template:")

        # Title Line Edit
        self.PageNameLineEdit = QLineEdit()

        # Template Combo Box
        self.TemplateComboBox = QComboBox()
        self.TemplateComboBox.setEditable(False)
        self.TemplateComboBox.addItem("None")
        self.TemplateComboBox.addItems(self.TemplateNames)

        # Buttons
        self.DoneButton = QPushButton("Done")
        self.DoneButton.clicked.connect(self.Done)
        self.CancelButton = QPushButton("Cancel")
        self.CancelButton.clicked.connect(self.Cancel)

        # Layout
        self.Layout = QGridLayout()
        self.Layout.addWidget(self.PageNamePrompt, 0, 0, 1, 2)
        self.Layout.addWidget(self.PageNameLabel, 1, 0)
        self.Layout.addWidget(self.PageNameLineEdit, 1, 1)
        self.Layout.addWidget(self.TemplateLabel, 2, 0)
        self.Layout.addWidget(self.TemplateComboBox, 2, 1)
        self.ButtonsLayout = QGridLayout()
        self.ButtonsLayout.addWidget(self.DoneButton, 0, 0)
        self.ButtonsLayout.addWidget(self.CancelButton, 0, 1)
        self.Layout.addLayout(self.ButtonsLayout, 3, 0, 1, 2)
        self.setLayout(self.Layout)

        # Set Window Title and Icon
        self.setWindowTitle("New Page")
        self.setWindowIcon(self.MainWindow.WindowIcon)

        # Execute Dialog
        self.exec_()

    def Done(self):
        NewPageName = self.PageNameLineEdit.text()
        if NewPageName == "":
            self.MainWindow.DisplayMessageBox("Page names cannot be blank.", Parent=self)
            return
        self.NewPageName = NewPageName
        self.TemplateName = self.TemplateComboBox.currentText()
        self.NewPageAdded = True
        self.close()

    def Cancel(self):
        self.close()
