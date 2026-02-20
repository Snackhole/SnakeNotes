from PyQt6.QtWidgets import QDialog, QLabel, QTextEdit, QPushButton, QGridLayout, QApplication


class ExportErrorDialog(QDialog):
    def __init__(self, ErrorString, MainWindow):
        super().__init__(parent=MainWindow)

        # Store Parameters
        self.MainWindow = MainWindow
        self.ErrorString = ErrorString

        # Label
        self.Label = QLabel("The following error was encountered while exporting this notebook:")

        # Text
        self.Text = QTextEdit()
        self.Text.setPlainText(self.ErrorString)
        self.Text.setReadOnly(True)

        # Buttons
        self.CopyButton = QPushButton("Copy to Clipboard")
        self.CopyButton.clicked.connect(self.Copy)
        self.DoneButton = QPushButton("Done")
        self.DoneButton.clicked.connect(self.Done)

        # Layout
        self.Layout = QGridLayout()
        self.Layout.addWidget(self.Label, 0, 0, 1, 2)
        self.Layout.addWidget(self.Text, 1, 0, 1, 2)
        self.Layout.addWidget(self.CopyButton, 2, 0)
        self.Layout.addWidget(self.DoneButton, 2, 1)
        self.setLayout(self.Layout)

        # Set Window Title and Icon
        self.setWindowTitle("Export Error")
        self.setWindowIcon(self.MainWindow.WindowIcon)

        # Execute Dialog
        self.exec()

    def Copy(self):
        QApplication.clipboard().setText(self.ErrorString)

    def Done(self):
        self.close()
