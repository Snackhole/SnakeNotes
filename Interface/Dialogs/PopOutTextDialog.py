from Interface.Widgets.PopOutTextWidget import PopOutTextWidget
from PyQt5.QtWidgets import QDialog, QGridLayout


class PopOutTextDialog(QDialog):
    def __init__(self, Page, Notebook, PopOutMarkdownParser, MainWindow):
        super().__init__(parent=MainWindow)

        # Store Parameters
        self.Page = Page
        self.Notebook = Notebook
        self.PopOutMarkdownParser = PopOutMarkdownParser
        self.MainWindow = MainWindow

        # Variables
        self.CurrentZoomLevel = 0
        self.Width = max(self.MainWindow.width() - 100, 100)
        self.Height = max(self.MainWindow.height() - 100, 100)

        # Pop-Out Text Widget
        self.PopOutTextWidget = PopOutTextWidget(self.Page, self.Notebook, self.PopOutMarkdownParser)

        # Create, Populate, and Set Layout
        self.Layout = QGridLayout()
        self.Layout.addWidget(self.PopOutTextWidget, 0, 0)
        self.setLayout(self.Layout)

        # Set Window Icon
        self.setWindowIcon(self.MainWindow.WindowIcon)

        # Refresh Page Display
        self.RefreshPageDisplay()

        # Window Resize
        self.Resize()

        # Show Window
        self.show()

    def RefreshPageDisplay(self):
        self.setWindowTitle(self.Page["Title"])
        self.UpdateZoomLevel()
        self.PopOutTextWidget.RefreshPageDisplay()

    def Resize(self):
        self.resize(self.Width, self.Height)

    def UpdateZoomLevel(self):
        if self.CurrentZoomLevel > 0:
            self.PopOutTextWidget.zoomOut(self.CurrentZoomLevel)
            self.CurrentZoomLevel = 0
        elif self.CurrentZoomLevel < 0:
            self.PopOutTextWidget.zoomIn(-self.CurrentZoomLevel)
            self.CurrentZoomLevel = 0
        if self.MainWindow.CurrentZoomLevel > 0:
            for ZoomLevel in range(self.MainWindow.CurrentZoomLevel):
                self.ZoomIn()
        elif self.MainWindow.CurrentZoomLevel < 0:
            for ZoomLevel in range(-self.MainWindow.CurrentZoomLevel):
                self.ZoomOut()

    def ZoomOut(self):
        self.PopOutTextWidget.zoomOut(1)
        self.CurrentZoomLevel -= 1

    def ZoomIn(self):
        self.PopOutTextWidget.zoomIn(1)
        self.CurrentZoomLevel += 1

    def closeEvent(self, event):
        PopOut = (self.Page, self)
        if PopOut in self.MainWindow.PopOutPages:
            del self.MainWindow.PopOutPages[self.MainWindow.PopOutPages.index(PopOut)]
        return super().closeEvent(event)
