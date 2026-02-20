from PyQt6.QtWidgets import QDialog, QGridLayout, QPushButton, QTextEdit


class AddToPageAndSubpagesDialog(QDialog):
    def __init__(self, Mode, Notebook, MainWindow):
        super().__init__(parent=MainWindow)

        # Store Parameters
        self.Mode = Mode
        self.Notebook = Notebook
        self.MainWindow = MainWindow

        # Variables
        self.TextToAdd = None
        self.Width = max(self.MainWindow.width() - 500, 100)
        self.Height = max(self.MainWindow.height() - 500, 100)

        # Text to Add
        self.TextToAddTextEdit = QTextEdit()
        self.TextToAddTextEdit.setTabChangesFocus(True)
        self.TextToAddTextEdit.setStyleSheet("selection-background-color: rgb(0, 120, 215); selection-color: white")

        # Buttons
        self.AddButton = QPushButton(self.Mode)
        self.AddButton.clicked.connect(self.Add)
        self.CancelButton = QPushButton("Cancel")
        self.CancelButton.clicked.connect(self.Cancel)

        # Create, Populate, and Set Layout
        self.Layout = QGridLayout()
        self.Layout.addWidget(self.TextToAddTextEdit, 0, 0, 1, 2)
        self.Layout.addWidget(self.AddButton, 1, 0)
        self.Layout.addWidget(self.CancelButton, 1, 1)
        self.setLayout(self.Layout)

        # Set Window Title and Icon
        self.setWindowTitle(f"{self.Mode} to Page and Sub Pages")
        self.setWindowIcon(self.MainWindow.WindowIcon)

        # Window Resize
        self.Resize()

        # Focus on Text
        self.TextToAddTextEdit.setFocus()

        # Execute Dialog
        self.exec()

    def Add(self):
        self.TextToAdd = self.TextToAddTextEdit.toPlainText()
        if self.TextToAdd == "":
            self.TextToAdd = None
        self.close()

    def Cancel(self):
        self.close()

    def Resize(self):
        self.resize(self.Width, self.Height)
