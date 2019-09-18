from PyQt5.QtWidgets import QDialog, QTreeWidget, QHeaderView, QTreeWidgetItem, QGridLayout, QPushButton, QCheckBox, QLabel, QComboBox

from Page import Page


class InsertLinksDialog(QDialog):
    def __init__(self, RootPage, ScriptName, Icon, Parent):
        # Store Parameters
        self.RootPage = RootPage
        self.ScriptName = ScriptName
        self.Icon = Icon
        self.Parent = Parent

        # QDialog Init
        super().__init__(parent=self.Parent)

        # Variables
        self.InsertAccepted = False
        self.InsertSubPageLinks = False
        self.SubPageLinksSeparator = None
        self.InsertIndexPath = None
        self.InsertIndexPaths = None
        self.Separators = {}
        self.Separators["Paragraph"] = "\n\n"
        self.Separators["New Line"] = "  \n"
        self.Width = max(self.Parent.width() - 100, 100)
        self.Height = max(self.Parent.height() - 100, 100)

        # Notebook Display
        self.NotebookDisplay = QTreeWidget()
        self.NotebookDisplay.setHeaderHidden(True)
        self.NotebookDisplay.header().setStretchLastSection(False)
        self.NotebookDisplay.header().setSectionResizeMode(QHeaderView.ResizeToContents)

        # Insert Sub Page Links Check Box
        self.InsertSubPageLinksCheckBox = QCheckBox("Insert Sub Page Links")

        # Sub Page Links Separator
        self.SubPageLinksSeparatorLabel = QLabel("Sub Page Links Separator:  ")
        self.SubPageLinksSeparatorComboBox = QComboBox()
        self.SubPageLinksSeparatorComboBox.addItems(["Paragraph", "New Line"])
        self.SubPageLinksSeparatorComboBox.setEditable(False)

        # Buttons
        self.InsertButton = QPushButton("Insert")
        self.InsertButton.clicked.connect(self.Insert)
        self.CancelButton = QPushButton("Cancel")
        self.CancelButton.clicked.connect(self.Cancel)

        # Create, Populate, and Set Layout
        self.Layout = QGridLayout()
        self.Layout.addWidget(self.NotebookDisplay, 0, 0, 1, 3)
        self.Layout.addWidget(self.InsertSubPageLinksCheckBox, 1, 0)
        self.Layout.addWidget(self.SubPageLinksSeparatorLabel, 1, 1)
        self.Layout.addWidget(self.SubPageLinksSeparatorComboBox, 1, 2)
        self.ButtonsLayout = QGridLayout()
        self.ButtonsLayout.addWidget(self.InsertButton, 0, 0)
        self.ButtonsLayout.addWidget(self.CancelButton, 0, 1)
        self.Layout.addLayout(self.ButtonsLayout, 2, 0, 1, 3)
        self.setLayout(self.Layout)

        # Set Window Title and Icon
        self.setWindowTitle(self.ScriptName)
        self.setWindowIcon(self.Icon)

        # Window Resize
        self.Resize()

        # Populate Notebook Display
        self.PopulateNotebookDisplay()

        # Execute Dialog
        self.exec_()

    def Insert(self):
        SelectedItems = self.NotebookDisplay.selectedItems()
        if len(SelectedItems) < 1:
            return
        self.InsertSubPageLinks = self.InsertSubPageLinksCheckBox.isChecked()
        if self.InsertSubPageLinks:
            self.InsertIndexPaths = SelectedItems[0].SubPageIndexPaths
            self.SubPageLinksSeparator = self.Separators[self.SubPageLinksSeparatorComboBox.currentText()]
        else:
            self.InsertIndexPath = SelectedItems[0].IndexPath
        self.InsertAccepted = True
        self.close()

    def Cancel(self):
        self.close()

    def PopulateNotebookDisplay(self):
        self.NotebookDisplay.clear()
        self.FillNotebookWidgetItem(self.NotebookDisplay.invisibleRootItem(), self.RootPage, IsRootPage=True)
        self.NotebookDisplay.setFocus()

    def FillNotebookWidgetItem(self, CurrentTreeItem, CurrentPage, IsRootPage=False):
        assert isinstance(CurrentPage, Page)

        SubPageIndexPaths = []
        for SubPage in CurrentPage.SubPages:
            SubPageIndexPaths.append((SubPage.Title, SubPage.GetFullIndexPath()))

        ChildTreeItem = NotebookDisplayItem(CurrentPage.Title, CurrentPage.GetFullIndexPath(), SubPageIndexPaths)
        CurrentTreeItem.addChild(ChildTreeItem)

        for SubPage in CurrentPage.SubPages:
            self.FillNotebookWidgetItem(ChildTreeItem, SubPage)

        if IsRootPage:
            ChildTreeItem.setExpanded(True)
            self.NotebookDisplay.setCurrentIndex(self.NotebookDisplay.model().index(0, 0))

    def Resize(self):
        self.resize(self.Width, self.Height)


class NotebookDisplayItem(QTreeWidgetItem):
    def __init__(self, Title, IndexPath, SubPageIndexPaths):
        super().__init__()
        self.setText(0, Title)
        self.IndexPath = IndexPath
        self.SubPageIndexPaths = SubPageIndexPaths
