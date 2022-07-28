from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QGridLayout, QPushButton, QScrollArea, QSizePolicy, QLabel


class NavigationBar(QFrame):
    def __init__(self, MainWindow):
        # Store Parameters
        self.MainWindow = MainWindow

        # Variables
        self.NavigationLabels = []

        # Initialize
        super().__init__(parent=self.MainWindow)

        # Scroll Area
        self.ScrollArea = QScrollArea()
        self.ScrollAreaFrame = QFrame()
        self.ScrollAreaLayout = QGridLayout()
        self.ScrollAreaFrame.setLayout(self.ScrollAreaLayout)
        self.ScrollArea.setWidget(self.ScrollAreaFrame)
        self.ScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ScrollArea.setWidgetResizable(True)
        self.ScrollArea.horizontalScrollBar().rangeChanged.connect(self.ScrollToEnd)

        # Scroll Buttons
        self.ScrollLeftButton = ScrollButton("\u2770", self.ScrollArea, -50)
        self.ScrollRightButton = ScrollButton("\u2771", self.ScrollArea, 50)

        # Create and Set Layout
        self.Layout = QGridLayout()
        self.Layout.addWidget(self.ScrollLeftButton, 0, 0)
        self.Layout.addWidget(self.ScrollArea, 0, 1)
        self.Layout.addWidget(self.ScrollRightButton, 0, 2)
        self.Layout.setColumnStretch(1, 1)
        self.setLayout(self.Layout)

        # Set Maximum Height
        self.setMaximumHeight(60)

    def UpdateFromIndexPath(self, IndexPath):
        for NavigationLabel in self.NavigationLabels:
            self.ScrollAreaLayout.removeWidget(NavigationLabel)
            del NavigationLabel
        for Column in range(self.ScrollAreaLayout.columnCount()):
            self.ScrollAreaLayout.setColumnStretch(Column, 0)
        self.NavigationLabels.clear()
        for SubPathEnd in range(1, len(IndexPath) + 1):
            SubPath = IndexPath[:SubPathEnd]
            Page = self.MainWindow.Notebook.GetPageFromIndexPath(SubPath)
            if len(SubPath) == len(IndexPath):
                self.NavigationLabels.append(QLabel(Page["Title"]))
            else:
                self.NavigationLabels.append(ParentPageLabel(Page, self.MainWindow))
                self.NavigationLabels.append(Separator(Page, self.MainWindow))
        for NavigationLabelIndex in range(len(self.NavigationLabels)):
            self.ScrollAreaLayout.addWidget(self.NavigationLabels[NavigationLabelIndex], 0, NavigationLabelIndex)
        self.ScrollAreaLayout.setColumnStretch(len(self.NavigationLabels), 1)

    def ScrollToEnd(self):
        self.ScrollArea.horizontalScrollBar().setValue(self.ScrollArea.horizontalScrollBar().maximum())


class ScrollButton(QPushButton):
    def __init__(self, Label, ScrollArea, Delta):
        # Store Parameters
        self.Label = Label
        self.ScrollArea = ScrollArea
        self.Delta = Delta

        # Initialize
        super().__init__(self.Label)

        # Configure
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.setMaximumWidth(30)
        self.setAutoRepeat(True)
        self.clicked.connect(self.Scroll)

    def Scroll(self):
        self.ScrollArea.horizontalScrollBar().setValue(self.ScrollArea.horizontalScrollBar().value() + self.Delta)


class Separator(QLabel):
    def __init__(self, Page, MainWindow):
        # Store Parameters
        self.Page = Page
        self.MainWindow = MainWindow

        # Initialize
        super().__init__("\u203a")

        # Configure
        self.setCursor(Qt.PointingHandCursor)


class ParentPageLabel(QLabel):
    def __init__(self, Page, MainWindow):
        # Store Parameters
        self.Page = Page
        self.MainWindow = MainWindow

        # Initialize
        super().__init__(self.Page["Title"])

        # Configure
        self.setCursor(Qt.PointingHandCursor)

    def mouseDoubleClickEvent(self, QMouseEvent):
        self.GoToPage()
        return super().mouseDoubleClickEvent(QMouseEvent)

    def GoToPage(self):
        self.MainWindow.NotebookDisplayWidgetInst.SelectTreeItemFromIndexPath(self.Page["IndexPath"])
