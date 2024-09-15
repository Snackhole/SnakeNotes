import os

from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QGridLayout, QFileDialog, QMessageBox


class SetDefaultNotebookDialog(QDialog):
    def __init__(self, MainWindow):
        super().__init__(parent=MainWindow)

        # Store Parameters
        self.MainWindow = MainWindow
        self.GzipMode = self.MainWindow.GzipMode

        # Default Notebook Path Line Edit
        self.DefaultNotebookPathLineEdit = QLineEdit()
        self.DefaultNotebookPathLineEdit.setReadOnly(True)
        self.DefaultNotebookPathLineEdit.setPlaceholderText("No default notebook set.")

        # Buttons
        self.SetButton = QPushButton("Set")
        self.SetButton.clicked.connect(self.Set)
        self.ClearButton = QPushButton("Clear")
        self.ClearButton.clicked.connect(self.Clear)
        self.DoneButton = QPushButton("Done")
        self.DoneButton.clicked.connect(self.Done)

        # Layout
        self.Layout = QGridLayout()
        self.Layout.addWidget(self.DefaultNotebookPathLineEdit, 0, 0, 1, 3)
        self.Layout.addWidget(self.SetButton, 1, 0)
        self.Layout.addWidget(self.ClearButton, 1, 1)
        self.Layout.addWidget(self.DoneButton, 1, 2)
        self.setLayout(self.Layout)

        # Set Window Title and Icon
        self.setWindowTitle("Set Default Notebook")
        self.setWindowIcon(self.MainWindow.WindowIcon)

        # Update Default Notebook Path Line Edit with Current Default Notebook
        DefaultNotebookPath = (self.MainWindow.GzipDefaultNotebook if self.GzipMode else self.MainWindow.DefaultNotebook)
        if DefaultNotebookPath is not None:
            self.DefaultNotebookPathLineEdit.setText(DefaultNotebookPath)
            self.DefaultNotebookPathLineEdit.setCursorPosition(len(DefaultNotebookPath))
            if not os.path.isfile(DefaultNotebookPath):
                self.MainWindow.DisplayMessageBox("The current default notebook could not be found.  Clear the default notebook or select a new one.", Icon=QMessageBox.Warning, Buttons=QMessageBox.Ok, Parent=self)

        # Execute Dialog
        self.exec_()

    def Set(self):
        NewDefaultNotebookFilePath = QFileDialog.getOpenFileName(parent=self, caption="Set Default Notebook", filter=f"Notebook files (*.ntbk{".gz" if self.GzipMode else ""})")[0]
        if NewDefaultNotebookFilePath != "":
            if self.GzipMode:
                self.MainWindow.GzipDefaultNotebook = NewDefaultNotebookFilePath
            else:
                self.MainWindow.DefaultNotebook = NewDefaultNotebookFilePath
            self.DefaultNotebookPathLineEdit.setText(NewDefaultNotebookFilePath)
            self.DefaultNotebookPathLineEdit.setCursorPosition(len(NewDefaultNotebookFilePath))

    def Clear(self):
        if self.GzipMode:
            self.MainWindow.GzipDefaultNotebook = None
        else:
            self.MainWindow.DefaultNotebook = None
        self.DefaultNotebookPathLineEdit.clear()

    def Done(self):
        self.close()
