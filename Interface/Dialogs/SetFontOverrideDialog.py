from PyQt6.QtGui import QFontDatabase
from PyQt6.QtWidgets import QDialog, QLabel, QComboBox, QPushButton, QGridLayout


class SetFontOverrideDialog(QDialog):
    def __init__(self, MainWindow):
        super().__init__(parent=MainWindow)

        # Store Parameters
        self.MainWindow = MainWindow

        # Variables
        self.FontSelected = None
        self.FontChanged = False
        self.AvailableFonts = ["None"]
        self.AllowedFonts = [
            "Arial",
            "Bookman Old Style",
            "Calibri",
            "Consolas",
            "Courier",
            "Courier New",
            "Garamond",
            "Georgia",
            "Impact",
            "Liberation Mono",
            "Liberation Sans",
            "Liberation Serif",
            "Papyrus",
            "Segoe UI",
            "Terminal",
            "Times New Roman"
        ]

        # Populate Available Fonts
        self.PopulateAvailableFonts()

        # Prompt
        self.Prompt = QLabel("Select a font, or choose \"None\" to revert to the default:")

        # Font Combo Box
        self.FontComboBox = QComboBox()
        self.FontComboBox.setEditable(False)
        self.FontComboBox.addItems(self.AvailableFonts)

        # Buttons
        self.DoneButton = QPushButton("Done")
        self.DoneButton.clicked.connect(self.Done)
        self.CancelButton = QPushButton("Cancel")
        self.CancelButton.clicked.connect(self.close)

        # Layout
        self.Layout = QGridLayout()
        self.Layout.addWidget(self.Prompt, 0, 0, 1, 2)
        self.Layout.addWidget(self.FontComboBox, 1, 0, 1, 2)
        self.Layout.addWidget(self.DoneButton, 2, 0)
        self.Layout.addWidget(self.CancelButton, 2, 1)
        self.setLayout(self.Layout)

        # Set Window Title and Icon
        self.setWindowTitle("Set Font Override")
        self.setWindowIcon(self.MainWindow.WindowIcon)

        # Execute Menu
        self.exec()

    def PopulateAvailableFonts(self):
        SystemFontsAvailable = QFontDatabase.families()
        FontsToAdd = [Font for Font in self.AllowedFonts if Font in SystemFontsAvailable]
        self.AvailableFonts = self.AvailableFonts + FontsToAdd

    def Done(self):
        FontString = self.FontComboBox.currentText()
        self.FontSelected = None if FontString == "None" else FontString
        self.FontChanged = True
        self.close()
