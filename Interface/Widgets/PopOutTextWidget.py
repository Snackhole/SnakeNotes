import json
import webbrowser

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextFormat
from PyQt6.QtWidgets import QTextEdit

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
        ContextMenu.exec(self.mapToGlobal(QContextMenuEvent.pos()))

    def wheelEvent(self, QWheelEvent):
        if QWheelEvent.modifiers() == Qt.KeyboardModifier.ControlModifier:
            QWheelEvent.accept()
        else:
            super().wheelEvent(QWheelEvent)

    def mouseDoubleClickEvent(self, QMouseEvent):
        Anchor = self.anchorAt(QMouseEvent.pos())
        CharFormat = self.cursorForPosition(QMouseEvent.pos()).charFormat()
        if Anchor != "" and QMouseEvent.button() == Qt.MouseButton.LeftButton:
            self.NavigateToLink(Anchor, QMouseEvent) if not self.MainWindow.SwapLeftAndMiddleClickForLinks else self.OpenLinkAsPopup(Anchor, QMouseEvent)
        elif CharFormat.isImageFormat():
            ImageFormat = CharFormat.toImageFormat()
            ImageAltText = ImageFormat.property(QTextFormat.Property.ImageAltText)
            self.MainWindow.ImageManager(ImageAltText)
        else:
            super().mouseDoubleClickEvent(QMouseEvent)

    def mouseReleaseEvent(self, QMouseEvent):
        Anchor = self.anchorAt(QMouseEvent.pos())
        if Anchor != "" and QMouseEvent.button() == Qt.MouseButton.MiddleButton:
            self.OpenLinkAsPopup(Anchor, QMouseEvent) if not self.MainWindow.SwapLeftAndMiddleClickForLinks else self.NavigateToLink(Anchor, QMouseEvent)
        else:
            super().mouseReleaseEvent(QMouseEvent)

    def mouseMoveEvent(self, QMouseEvent):
        Anchor = self.anchorAt(QMouseEvent.pos())
        CharFormat = self.cursorForPosition(QMouseEvent.pos()).charFormat()
        if Anchor != "" or CharFormat.isImageFormat():
            self.viewport().setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.viewport().setCursor(Qt.CursorShape.IBeamCursor)
        return super().mouseMoveEvent(QMouseEvent)

    # Link Methods
    def NavigateToLink(self, Anchor, QMouseEvent):
        if self.Notebook.StringIsValidIndexPath(Anchor):
            self.MainWindow.NotebookDisplayWidgetInst.SelectTreeItemFromIndexPathString(Anchor)
            self.MainWindow.activateWindow()
            self.MainWindow.raise_()
            self.MainWindow.setFocus()
            QMouseEvent.accept()
        else:
            if Anchor.startswith("[0,"):
                self.MainWindow.DisplayMessageBox("Linked page not found.  Pop-out page may need to be refreshed.", Parent=self)
                QMouseEvent.accept()
            else:
                webbrowser.open(Anchor)
                QMouseEvent.accept()

    def OpenLinkAsPopup(self, Anchor, QMouseEvent):
        if self.Notebook.StringIsValidIndexPath(Anchor):
            IndexPath = json.loads(Anchor)
            self.MainWindow.PopOutPage(IndexPath)
            QMouseEvent.accept()
        else:
            if Anchor.startswith("[0,"):
                self.MainWindow.DisplayMessageBox("Linked page not found.  Pop-out page may need to be refreshed.", Parent=self)
                QMouseEvent.accept()
            else:
                webbrowser.open(Anchor)
                QMouseEvent.accept()
