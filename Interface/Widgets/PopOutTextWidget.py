import json
import webbrowser

from PyQt5.QtCore import Qt
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
    def contextMenuEvent(self, QContextMenuEvent):
        ContextMenu = self.createStandardContextMenu()
        Anchor = self.anchorAt(QContextMenuEvent.pos())
        if Anchor != "":
            if self.Notebook.StringIsValidIndexPath(Anchor):
                ContextMenu.addSeparator()
                IndexPath = json.loads(Anchor)
                ContextMenu.addAction(self.MainWindow.PopOutPageIcon, "Pop Out Linked Page", lambda: self.MainWindow.PopOutPage(IndexPath))
        ContextMenu.exec_(self.mapToGlobal(QContextMenuEvent.pos()))

    def wheelEvent(self, QWheelEvent):
        if QWheelEvent.modifiers() == Qt.ControlModifier:
            QWheelEvent.accept()
        else:
            super().wheelEvent(QWheelEvent)

    def mouseDoubleClickEvent(self, QMouseEvent):
        Anchor = self.anchorAt(QMouseEvent.pos())
        if Anchor != "" and QMouseEvent.button() == Qt.LeftButton:
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

    def mouseReleaseEvent(self, QMouseEvent):
        Anchor = self.anchorAt(QMouseEvent.pos())
        if Anchor != "" and QMouseEvent.button() == Qt.MiddleButton:
            if self.Notebook.StringIsValidIndexPath(Anchor):
                IndexPath = json.loads(Anchor)
                self.MainWindow.PopOutPage(IndexPath)
                QMouseEvent.accept()
            else:
                if Anchor.startswith("[0,"):
                    self.MainWindow.DisplayMessageBox("Linked page not found.  Pop-out page may need to be refreshed.", Parent=self)
                else:
                    webbrowser.open(Anchor)
        else:
            super().mouseReleaseEvent(QMouseEvent)

    def mouseMoveEvent(self, QMouseEvent):
        Anchor = self.anchorAt(QMouseEvent.pos())
        if Anchor != "":
            self.viewport().setCursor(Qt.PointingHandCursor)
        else:
            self.viewport().setCursor(Qt.IBeamCursor)
        return super().mouseMoveEvent(QMouseEvent)
