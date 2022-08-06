import json

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel, QTreeWidget, QHeaderView, QPushButton, QTreeWidgetItem


class SearchForLinkedPagesDialog(QDialog):
    def __init__(self, MainWindow):
        super().__init__(parent=MainWindow)

        # Store Parameters
        self.MainWindow = MainWindow

        # Variables
        self.LinkingPage = self.MainWindow.TextWidgetInst.CurrentPage

        # Variables
        self.DestinationIndexPath = None

        # Prompt
        self.Prompt = QLabel("Pages linked by \"" + self.LinkingPage["Title"] + "\":")

        # Notebook Display
        self.NotebookDisplay = QTreeWidget()
        self.NotebookDisplay.setHeaderHidden(True)
        self.NotebookDisplay.header().setStretchLastSection(False)
        self.NotebookDisplay.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.NotebookDisplay.itemActivated.connect(self.GoTo)

        # Buttons
        self.GoToButton = QPushButton("Go To")
        self.GoToButton.clicked.connect(self.GoTo)
        self.DoneButton = QPushButton("Done")
        self.DoneButton.clicked.connect(self.Done)

        # Create, Populate, and Set Layout
        self.Layout = QGridLayout()
        self.Layout.addWidget(self.Prompt, 0, 0, 1, 2)
        self.Layout.addWidget(self.NotebookDisplay, 1, 0, 1, 2)
        self.Layout.addWidget(self.GoToButton, 2, 0)
        self.Layout.addWidget(self.DoneButton, 2, 1)
        self.setLayout(self.Layout)

        # Set Window Title and Icon
        self.setWindowTitle("Pages Linked by \"" + self.LinkingPage["Title"] + "\"")
        self.setWindowIcon(self.MainWindow.WindowIcon)

        # Populate Notebook Display
        self.PopulateNotebookDisplay()

        # Execute Dialog
        self.exec_()

    def PopulateNotebookDisplay(self):
        self.NotebookDisplay.setRootIsDecorated(True)
        self.FillNotebookWidgetItem(self.NotebookDisplay.invisibleRootItem(), self.MainWindow.Notebook.RootPage, IsRootPage=True)

    def FillNotebookWidgetItem(self, CurrentTreeItem, CurrentPage, IsRootPage=False):
        IsLinkedPage = "](" + json.dumps(CurrentPage["IndexPath"]) in self.LinkingPage["Content"]
        ChildTreeItem = NotebookDisplayItem(CurrentPage["Title"], CurrentPage["IndexPath"], IsLinkedPage)
        CurrentTreeItem.addChild(ChildTreeItem)

        for SubPage in CurrentPage["SubPages"]:
            self.FillNotebookWidgetItem(ChildTreeItem, SubPage)

        ChildTreeItem.setExpanded(True)

        if IsRootPage:
            self.NotebookDisplay.setCurrentIndex(self.NotebookDisplay.model().index(0, 0))

    def GoTo(self):
        SelectedItems = self.NotebookDisplay.selectedItems()
        if len(SelectedItems) < 1:
            return
        SelectedItem = SelectedItems[0]
        self.DestinationIndexPath = SelectedItem.IndexPath
        self.close()

    def Done(self):
        self.close()

    def keyPressEvent(self, QKeyEvent):
        KeyPressed = QKeyEvent.key()
        if KeyPressed == Qt.Key_Return and self.NotebookDisplay.hasFocus():
            return
        else:
            super().keyPressEvent(QKeyEvent)


class NotebookDisplayItem(QTreeWidgetItem):
    def __init__(self, Title, IndexPath, IsLinkedPage):
        super().__init__()

        # Store Parameters
        self.Title = Title
        self.IndexPath = IndexPath
        self.IsLinkedPage = IsLinkedPage

        # Set Text
        self.setText(0, Title)

        # Set Background
        if self.IsLinkedPage:
            self.setBackground(0, QColor("darkMagenta"))
            self.setForeground(0, QColor("white"))
