from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QGridLayout, QPushButton, QScrollArea, QSizePolicy, QLabel

from Interface.Dialogs.NavigationBarSubPageDialog import NavigationBarSubPageDialog


class NavigationBar(QFrame):
    def __init__(self, MainWindow):
        # Store Parameters
        self.MainWindow = MainWindow

        # Variables
        self.NavigationLabels = []

        # Initialize
        super().__init__(parent=self.MainWindow)

        # Scroll Area
        self.NavigationScrollArea = NavigationScrollArea()
        self.NavigationScrollArea.setFocusPolicy(Qt.NoFocus)

        # Scroll Buttons
        self.ScrollLeftButton = ScrollButton("Left", self.NavigationScrollArea)
        self.ScrollLeftButton.setFocusPolicy(Qt.NoFocus)
        self.ScrollRightButton = ScrollButton("Right", self.NavigationScrollArea)
        self.ScrollRightButton.setFocusPolicy(Qt.NoFocus)

        # Create and Set Layout
        self.Layout = QGridLayout()
        self.Layout.addWidget(self.ScrollLeftButton, 0, 0)
        self.Layout.addWidget(self.NavigationScrollArea, 0, 1)
        self.Layout.addWidget(self.ScrollRightButton, 0, 2)
        self.Layout.setColumnStretch(1, 1)
        self.setLayout(self.Layout)

        # Set Maximum Height
        self.setMaximumHeight(60)

    def UpdateFromIndexPath(self, IndexPath):
        for Column in range(self.NavigationScrollArea.Layout.columnCount()):
            self.NavigationScrollArea.Layout.setColumnStretch(Column, 0)
        for NavigationLabel in self.NavigationLabels:
            self.NavigationScrollArea.Layout.removeWidget(NavigationLabel)
            del NavigationLabel
        self.NavigationLabels.clear()
        for SubPathEnd in range(1, len(IndexPath) + 1):
            SubPath = IndexPath[:SubPathEnd]
            Page = self.MainWindow.Notebook.GetPageFromIndexPath(SubPath)
            self.NavigationLabels.append(NavigationPageLabel(Page, self.MainWindow))
            if len(Page["SubPages"]) > 0:
                self.NavigationLabels.append(Separator(Page, self.MainWindow))
        for NavigationLabelIndex in range(len(self.NavigationLabels)):
            self.NavigationScrollArea.Layout.addWidget(self.NavigationLabels[NavigationLabelIndex], 0, NavigationLabelIndex)
        self.NavigationScrollArea.Layout.setColumnStretch(len(self.NavigationLabels), 1)


class NavigationScrollArea(QScrollArea):
    def __init__(self):
        # Variables
        self.LeftDelta = -50
        self.RightDelta = 50

        # Initialize
        super().__init__()

        # Create and Set Frame and Layout
        self.Frame = QFrame()
        self.Layout = QGridLayout()
        self.Frame.setLayout(self.Layout)
        self.setWidget(self.Frame)

        # Configure
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        self.horizontalScrollBar().rangeChanged.connect(self.ScrollToEnd)

    def Scroll(self, Delta):
        self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + Delta)

    def ScrollLeft(self):
        self.Scroll(self.LeftDelta)

    def ScrollRight(self):
        self.Scroll(self.RightDelta)

    def ScrollToEnd(self):
        self.horizontalScrollBar().setValue(self.horizontalScrollBar().maximum())

    def wheelEvent(self, QWheelEvent):
        Delta = QWheelEvent.angleDelta()
        if Delta is not None:
            VerticalDelta = Delta.y()
            if VerticalDelta > 0:
                self.ScrollLeft()
            elif VerticalDelta < 0:
                self.ScrollRight()


class ScrollButton(QPushButton):
    def __init__(self, Direction, NavigationScrollArea):
        # Store Parameters
        self.Direction = Direction
        self.NavigationScrollArea = NavigationScrollArea

        # Variables
        if self.Direction == "Left":
            self.Label = "\u2770"
        elif self.Direction == "Right":
            self.Label = "\u2771"
        else:
            self.Label = "Undefined Direction"

        # Initialize
        super().__init__(self.Label)

        # Configure
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.setMaximumWidth(30)
        self.setAutoRepeat(True)
        self.clicked.connect(self.Scroll)

    def Scroll(self):
        if self.Direction == "Left":
            self.NavigationScrollArea.ScrollLeft()
        elif self.Direction == "Right":
            self.NavigationScrollArea.ScrollRight()
        else:
            return


class Separator(QLabel):
    def __init__(self, Page, MainWindow):
        # Store Parameters
        self.Page = Page
        self.MainWindow = MainWindow

        # Initialize
        super().__init__(" \u203a ")

        # Configure
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("QLabel::hover {background-color: darkCyan; color: white;}")

    def mouseDoubleClickEvent(self, QMouseEvent):
        self.GoToSubPage()

    def GoToSubPage(self):
        ValidSubPages = [SubPage for SubPage in self.Page["SubPages"] if self.MainWindow.NotebookDisplayWidgetInst.GetCurrentPageIndexPath() != SubPage["IndexPath"]]
        if len(ValidSubPages) > 0:
            NavigationBarSubPageDialogInst = NavigationBarSubPageDialog(self.Page, ValidSubPages, self.MainWindow)
            if NavigationBarSubPageDialogInst.SelectedSubPage is not None:
                self.MainWindow.NotebookDisplayWidgetInst.SelectTreeItemFromIndexPath(NavigationBarSubPageDialogInst.SelectedSubPage["IndexPath"])


class NavigationPageLabel(QLabel):
    def __init__(self, Page, MainWindow):
        # Store Parameters
        self.Page = Page
        self.MainWindow = MainWindow

        # Initialize
        super().__init__(" " + self.Page["Title"] + " ")

        # Configure
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("QLabel::hover {background-color: darkCyan; color: white;}")

    def mouseDoubleClickEvent(self, QMouseEvent):
        self.GoToPage()

    def GoToPage(self):
        if self.MainWindow.NotebookDisplayWidgetInst.GetCurrentPageIndexPath() != self.Page["IndexPath"]:
            self.MainWindow.NotebookDisplayWidgetInst.SelectTreeItemFromIndexPath(self.Page["IndexPath"])
