import json

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QTreeWidgetItemIterator, QHeaderView, QMenu


class NotebookDisplayWidget(QTreeWidget):
    def __init__(self, Notebook, MainWindow):
        super().__init__()

        # Store Parameters
        self.Notebook = Notebook
        self.MainWindow = MainWindow

        # Header Setup
        self.setHeaderHidden(True)
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(QHeaderView.ResizeToContents)

        # Fill From Root Page
        self.FillFromRootPage()

    def FillFromRootPage(self):
        self.clear()
        self.FillNotebookWidgetItem(self.invisibleRootItem(), self.Notebook.RootPage, IsRootPage=True)
        self.setFocus()

    def FillNotebookWidgetItem(self, CurrentTreeItem, CurrentPage, IsRootPage=False):
        ChildTreeItem = NotebookDisplayWidgetItem(CurrentPage["Title"], CurrentPage["IndexPath"])
        CurrentTreeItem.addChild(ChildTreeItem)

        for SubPage in CurrentPage["SubPages"]:
            self.FillNotebookWidgetItem(ChildTreeItem, SubPage)

        if IsRootPage:
            ChildTreeItem.setExpanded(True)
            self.setCurrentIndex(self.model().index(0, 0))

    def GetCurrentPageIndexPath(self):
        SelectedItems = self.selectedItems()
        if len(SelectedItems) < 1:
            return None
        SelectedItem = SelectedItems[0]
        return SelectedItem.IndexPath

    def HighlightPages(self, HighlightedPageIndexPaths):
        Iterator = QTreeWidgetItemIterator(self)
        while Iterator.value():
            Page = Iterator.value()
            if Page.IndexPath in HighlightedPageIndexPaths:
                Page.setForeground(0, QColor("white"))
                Page.setBackground(0, QColor("darkMagenta"))
            Iterator += 1

    def ClearPageHighlighting(self):
        Iterator = QTreeWidgetItemIterator(self)
        while Iterator.value():
            Page = Iterator.value()
            Page.setData(0, Qt.ForegroundRole, None)
            Page.setData(0, Qt.BackgroundRole, None)
            Iterator += 1

    def SelectTreeItemFromIndexPath(self, IndexPath, SelectParent=False, ScrollToLastChild=False, SelectDelta=0):
        if SelectParent:
            IndexPath = IndexPath[:-1]
        IndexPath[-1] += SelectDelta
        DestinationIndex = self.model().index(0, 0)
        for Element in IndexPath[1:]:
            DestinationIndex = DestinationIndex.child(Element, 0)
        self.setCurrentIndex(DestinationIndex)
        self.currentItem().setExpanded(True)
        self.scrollToItem(self.currentItem() if not ScrollToLastChild else self.currentItem().child(self.currentItem().childCount() - 1), self.PositionAtCenter)

    def SelectTreeItemFromIndexPathString(self, IndexPathString, SelectParent=False, ScrollToLastChild=False, SelectDelta=0):
        IndexPath = json.loads(IndexPathString)
        self.SelectTreeItemFromIndexPath(IndexPath, SelectParent=SelectParent, ScrollToLastChild=ScrollToLastChild, SelectDelta=SelectDelta)

    def contextMenuEvent(self, event):
        ContextMenu = QMenu(self)
        ContextMenu.addAction(self.MainWindow.NewPageAction)
        ContextMenu.addAction(self.MainWindow.DeletePageAction)
        ContextMenu.addAction(self.MainWindow.RenamePageAction)
        ContextMenu.addSeparator()
        ContextMenu.addAction(self.MainWindow.MovePageUpAction)
        ContextMenu.addAction(self.MainWindow.MovePageDownAction)
        ContextMenu.addAction(self.MainWindow.PromotePageAction)
        ContextMenu.addAction(self.MainWindow.DemotePageAction)
        ContextMenu.addAction(self.MainWindow.PromoteAllSubPagesAction)
        ContextMenu.addAction(self.MainWindow.DemoteAllSiblingPagesAction)
        ContextMenu.addAction(self.MainWindow.MovePageToAction)
        ContextMenu.addAction(self.MainWindow.AlphabetizeSubPagesAction)
        ContextMenu.addSeparator()
        ContextMenu.addAction(self.MainWindow.ExpandAllAction)
        ContextMenu.addAction(self.MainWindow.ExpandRecursivelyAction)
        ContextMenu.addAction(self.MainWindow.CollapseAllAction)
        ContextMenu.exec_(self.mapToGlobal(event.pos()))

    def ExpandRecursively(self):
        SelectedIndexes = self.selectedIndexes()
        if len(SelectedIndexes) == 1:
            self.expandRecursively(SelectedIndexes[0])

    def collapseAll(self):
        super().collapseAll()
        self.itemAt(0, 0).setExpanded(True)
        self.setCurrentIndex(self.model().index(0, 0))


class NotebookDisplayWidgetItem(QTreeWidgetItem):
    def __init__(self, Title, IndexPath):
        super().__init__()
        self.setText(0, Title)
        self.IndexPath = IndexPath
