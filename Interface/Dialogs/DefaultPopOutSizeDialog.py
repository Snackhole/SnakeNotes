from PyQt6.QtWidgets import QDialog, QLabel, QSpinBox, QPushButton, QGridLayout


class DefaultPopOutSizeDialog(QDialog):
    def __init__(self, MainWindow):
        super().__init__(parent=MainWindow)

        # Store Parameters
        self.MainWindow = MainWindow

        # Variables
        self.SizeChanged = False
        self.Width = self.MainWindow.DefaultPopOutSize["Width"]
        self.Height = self.MainWindow.DefaultPopOutSize["Height"]

        # Labels
        self.Prompt = QLabel("Default size of pop-out pages:")
        self.WidthLabel = QLabel("Width:")
        self.HeightLabel = QLabel("Height:")

        # Spin Boxes
        self.WidthSpinBox = QSpinBox()
        self.WidthSpinBox.setMinimum(0)
        self.WidthSpinBox.setMaximum(3800)
        self.WidthSpinBox.setSingleStep(50)
        self.WidthSpinBox.setSuffix(" pixels")
        self.WidthSpinBox.setSpecialValueText("Adaptive")
        self.WidthSpinBox.setValue(self.Width)
        self.HeightSpinBox = QSpinBox()
        self.HeightSpinBox.setMinimum(0)
        self.HeightSpinBox.setMaximum(2100)
        self.HeightSpinBox.setSingleStep(50)
        self.HeightSpinBox.setSuffix(" pixels")
        self.HeightSpinBox.setSpecialValueText("Adaptive")
        self.HeightSpinBox.setValue(self.Height)

        # Buttons
        self.DoneButton = QPushButton("Done")
        self.DoneButton.clicked.connect(self.Done)
        self.CancelButton = QPushButton("Cancel")
        self.CancelButton.clicked.connect(self.Cancel)

        # Layout
        self.Layout = QGridLayout()
        self.Layout.addWidget(self.Prompt, 0, 0, 1, 2)
        self.Layout.addWidget(self.WidthLabel, 1, 0)
        self.Layout.addWidget(self.WidthSpinBox, 1, 1)
        self.Layout.addWidget(self.HeightLabel, 2, 0)
        self.Layout.addWidget(self.HeightSpinBox, 2, 1)
        self.ButtonsLayout = QGridLayout()
        self.ButtonsLayout.addWidget(self.DoneButton, 0, 0)
        self.ButtonsLayout.addWidget(self.CancelButton, 0, 1)
        self.Layout.addLayout(self.ButtonsLayout, 3, 0, 1, 2)
        self.setLayout(self.Layout)

        # Set Window Title and Icon
        self.setWindowTitle("Default Pop-Out Page Size")
        self.setWindowIcon(self.MainWindow.WindowIcon)

        # Execute Dialog
        self.exec()

    def Done(self):
        self.Width = self.WidthSpinBox.value()
        self.Height = self.HeightSpinBox.value()
        self.SizeChanged = True
        self.close()

    def Cancel(self):
        self.close()
