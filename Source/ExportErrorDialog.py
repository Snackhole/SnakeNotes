from PyQt5.QtWidgets import QDialog, QLabel, QTextEdit, QPushButton, QGridLayout, QApplication


class ExportErrorDialog(QDialog):
    def __init__(self, CombinedErrorString, Icon, Parent):
        super().__init__(parent=Parent)

        # Store Parameters
        self.CombinedErrorString = CombinedErrorString
        self.Icon = Icon

        # Label
        self.Label = QLabel("The following errors were encountered while exporting pages in this notebook:")

        # Text
        self.Text = QTextEdit()
        self.Text.setPlainText(self.CombinedErrorString)
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
        self.setWindowTitle("Export Errors")
        self.setWindowIcon(self.Icon)

        # Execute Dialog
        self.exec_()

    def Copy(self):
        QApplication.clipboard().setText(self.CombinedErrorString)

    def Done(self):
        self.close()
