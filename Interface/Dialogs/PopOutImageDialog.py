from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QDialog, QLabel, QScrollArea, QPushButton, QGridLayout

from Core import Base64Converters


class PopOutImageDialog(QDialog):
    def __init__(self, ImageName, ImageBase64, MainWindow):
        super().__init__(parent=MainWindow)

        # Store Parameters
        self.ImageName = ImageName
        self.ImageBase64 = ImageBase64
        self.MainWindow = MainWindow

        # Variables
        self.Width = max(self.MainWindow.width() - 100, 100) if self.MainWindow.DefaultPopOutImageSize["Width"] == 0 else self.MainWindow.DefaultPopOutImageSize["Width"]
        self.Height = max(self.MainWindow.height() - 100, 100) if self.MainWindow.DefaultPopOutImageSize["Height"] == 0 else self.MainWindow.DefaultPopOutImageSize["Height"]

        # Image Display
        self.ImageDisplay = QLabel()
        self.ImageDisplayScrollArea = QScrollArea()
        self.ImageDisplayScrollArea.setWidget(self.ImageDisplay)
        self.ImageDisplayScrollArea.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Close Button
        self.CloseButton = QPushButton("Close")
        self.CloseButton.clicked.connect(self.close)

        # Create, Populate, and Set Layout
        self.Layout = QGridLayout()
        self.Layout.addWidget(self.ImageDisplayScrollArea, 0, 0)
        self.Layout.addWidget(self.CloseButton, 1, 0)
        self.setLayout(self.Layout)

        # Set Window Icon and Title
        self.setWindowIcon(self.MainWindow.WindowIcon)
        self.setWindowTitle(self.ImageName)

        # Refresh Image
        self.RefreshImage()

        # Window Resize
        self.Resize()

        # Show Window
        self.show()
    
    def RefreshImage(self):
        ImageBinary = Base64Converters.GetBinaryFromBase64String(self.ImageBase64)
        ImagePixmap = QPixmap()
        ImagePixmap.loadFromData(ImageBinary)
        self.ImageDisplay.setPixmap(ImagePixmap)
        self.ImageDisplay.resize(self.ImageDisplay.pixmap().size())

    def Resize(self):
        self.resize(self.Width, self.Height)

    def closeEvent(self, event):
        if self in self.MainWindow.PopOutImages:
            del self.MainWindow.PopOutImages[self.MainWindow.PopOutImages.index(self)]
        return super().closeEvent(event)

    def keyPressEvent(self, QKeyEvent):
        KeyPressed = QKeyEvent.key()
        if KeyPressed == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(QKeyEvent)
