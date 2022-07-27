import webbrowser

from PyQt5 import QtCore
from PyQt5.QtWidgets import QTextEdit

from Core import MarkdownRenderers


class PopOutTextWidget(QTextEdit):
    def __init__(self, Page, Notebook, PopOutMarkdownParser, MainWindow):
        super().__init__()

        # Store Parameters
        self.Page = Page
        self.Notebook = Notebook
        self.PopOutMarkdownParser = PopOutMarkdownParser
        self.MainWindow = MainWindow

        # Tab Behavior
        self.setTabChangesFocus(True)

        # Set Read Only
        self.setReadOnly(True)

        # Set Style Sheet
        self.setStyleSheet("selection-background-color: rgb(0, 120, 215); selection-color: white")

    def RefreshPageDisplay(self):
        DisplayText = MarkdownRenderers.ConstructMarkdownStringFromPage(self.Page, self.Notebook)
        HTMLText = self.PopOutMarkdownParser(DisplayText)
        self.setHtml(HTMLText)

    # Events
    def wheelEvent(self, QWheelEvent):
        if QWheelEvent.modifiers() == QtCore.Qt.ControlModifier:
            QWheelEvent.accept()
        else:
            super().wheelEvent(QWheelEvent)

    def mouseDoubleClickEvent(self, QMouseEvent):
        Anchor = self.anchorAt(QMouseEvent.pos())
        if Anchor != "":
            if self.Notebook.StringIsValidIndexPath(Anchor):
                self.MainWindow.NotebookDisplayWidgetInst.SelectTreeItemFromIndexPathString(Anchor)
                self.MainWindow.activateWindow()
                self.MainWindow.raise_()
                self.MainWindow.setFocus()
                QMouseEvent.accept()
            else:
                if Anchor.startswith("[0,"):
                    self.MainWindow.DisplayMessageBox("Linked page not found.  Pop-out page may need to be refreshed.", Parent=self)
                else:
                    webbrowser.open(Anchor)
        else:
            super().mouseDoubleClickEvent(QMouseEvent)

    def mouseMoveEvent(self, QMouseEvent):
        Anchor = self.anchorAt(QMouseEvent.pos())
        if Anchor != "":
            self.viewport().setCursor(QtCore.Qt.PointingHandCursor)
        else:
            self.viewport().setCursor(QtCore.Qt.IBeamCursor)
        return super().mouseMoveEvent(QMouseEvent)
