from PyQt6.QtWidgets import QDialog, QPushButton, QListWidget, QListWidgetItem, QGridLayout, QInputDialog, QMessageBox, QCheckBox


class HighlightTextDialog(QDialog):
    def __init__(self, MainWindow):
        super().__init__(parent=MainWindow)

        # Store Parameters
        self.MainWindow = MainWindow

        # Set Window Title and Icon
        self.setWindowTitle("Highlight Text")
        self.setWindowIcon(self.MainWindow.WindowIcon)

        # Text to Highlight List
        self.TextToHighlightListWidget = QListWidget()

        # Match Case Check Box
        self.MatchCaseCheckBox = QCheckBox("Match Case")
        self.MatchCaseCheckBox.setChecked(self.MainWindow.TextToHighlightMatchCase)
        self.MatchCaseCheckBox.stateChanged.connect(self.ToggleMatchCase)

        # Buttons
        self.AddButton = QPushButton("Add")
        self.AddButton.clicked.connect(self.Add)
        self.RemoveButton = QPushButton("Remove")
        self.RemoveButton.clicked.connect(self.Remove)
        self.ClearButton = QPushButton("Clear")
        self.ClearButton.clicked.connect(self.Clear)
        self.DoneButton = QPushButton("Done")
        self.DoneButton.clicked.connect(self.Done)

        # Create, Populate, and Set Layout
        self.Layout = QGridLayout()
        self.Layout.addWidget(self.TextToHighlightListWidget, 0, 0, 1, 5)
        self.Layout.addWidget(self.AddButton, 1, 0)
        self.Layout.addWidget(self.RemoveButton, 1, 1)
        self.Layout.addWidget(self.ClearButton, 1, 2)
        self.Layout.addWidget(self.MatchCaseCheckBox, 1, 3)
        self.Layout.addWidget(self.DoneButton, 1, 4)
        self.setLayout(self.Layout)

        # Populate List
        self.PopulateTextToHighlightList()

        # Execute Menu
        self.exec()

    def PopulateTextToHighlightList(self):
        self.TextToHighlightListWidget.clear()
        for Text in self.MainWindow.TextToHighlight:
            self.TextToHighlightListWidget.addItem(QListWidgetItem(Text))
        self.TextToHighlightListWidget.setCurrentRow(0)

    def Add(self):
        NewText, OK = QInputDialog.getText(self, "Add Text", "Add text to highlight:")
        if OK:
            if NewText == "":
                self.MainWindow.DisplayMessageBox("Cannot highlight blank text.", Parent=self)
            elif NewText in self.MainWindow.TextToHighlight:
                self.MainWindow.DisplayMessageBox("This text is already being highlighted.", Parent=self)
            else:
                self.MainWindow.TextToHighlight.append(NewText)
                self.PopulateTextToHighlightList()

    def Remove(self):
        SelectedItems = self.TextToHighlightListWidget.selectedItems()
        if len(SelectedItems) > 0:
            SelectedText = SelectedItems[0].text()
            self.MainWindow.TextToHighlight.remove(SelectedText)
            self.PopulateTextToHighlightList()

    def Clear(self):
        if self.MainWindow.DisplayMessageBox("Are you sure you want to clear the list of text to highlight?  This cannot be undone.", Icon=QMessageBox.Icon.Warning, Buttons=(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No), Parent=self) == QMessageBox.StandardButton.Yes:
            self.MainWindow.TextToHighlight.clear()
            self.MatchCaseCheckBox.setChecked(False)
            self.PopulateTextToHighlightList()

    def ToggleMatchCase(self):
        self.MainWindow.TextToHighlightMatchCase = not self.MainWindow.TextToHighlightMatchCase

    def Done(self):
        self.close()
