import webbrowser

from PyQt6.QtWidgets import QDialog, QLabel, QPushButton, QGridLayout

from Build import BuildVariables


class UpdateDialog(QDialog):
    def __init__(self, LatestVersion, MainWindow):
        super().__init__(parent=MainWindow)

        # Store Parameters
        self.LatestVersion = LatestVersion
        self.MainWindow = MainWindow

        # Label
        self.Label = QLabel(f"You are not using the latest version!  Please visit the releases page to download version {self.LatestVersion}.")

        # Buttons
        self.ReleasesButton = QPushButton("Visit Releases Page")
        self.ReleasesButton.clicked.connect(self.Releases)
        self.CloseButton = QPushButton("Close")
        self.CloseButton.clicked.connect(self.close)

        # Layout
        self.Layout = QGridLayout()
        self.Layout.addWidget(self.Label, 0, 0, 1, 2)
        self.Layout.addWidget(self.ReleasesButton, 1, 0)
        self.Layout.addWidget(self.CloseButton, 1, 1)
        self.setLayout(self.Layout)

        # Set Window Title and Icon
        self.setWindowTitle("Update Check")
        self.setWindowIcon(self.MainWindow.WindowIcon)

        # Execute Dialog
        self.exec()

    def Releases(self):
        webbrowser.open(f"https://github.com/Snackhole/{BuildVariables["AppName"]}/releases")
