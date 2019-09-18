from PyQt5.QtWidgets import QDialog, QListWidget, QTextEdit, QListWidgetItem, QPushButton, QGridLayout, QMessageBox, QLabel, QLineEdit, QSplitter, QInputDialog


class TemplateManagerDialog(QDialog):
    def __init__(self, RootPage, ScriptName, Icon, DisplayMessageBox, Parent):
        # Store Parameters
        self.RootPage = RootPage
        self.ScriptName = ScriptName
        self.Icon = Icon
        self.DisplayMessageBox = DisplayMessageBox
        self.Parent = Parent

        # QDialog Init
        super().__init__(parent=self.Parent)

        # Variables
        self.UnsavedChanges = False
        self.Width = max(self.Parent.width() - 100, 100)
        self.Height = max(self.Parent.height() - 100, 100)

        # Template List
        self.TemplateList = QListWidget()
        self.TemplateList.itemSelectionChanged.connect(self.TemplateSelected)

        # Template Display
        self.TemplateDisplay = QTextEdit()
        self.TemplateDisplay.setReadOnly(True)
        self.TemplateDisplay.setStyleSheet("selection-background-color: rgb(0, 120, 215); selection-color: white")

        # Buttons
        self.AddTemplateButton = QPushButton("Add")
        self.AddTemplateButton.clicked.connect(self.AddTemplate)
        self.RenameTemplateButton = QPushButton("Rename")
        self.RenameTemplateButton.clicked.connect(self.RenameTemplate)
        self.DeleteTemplateButton = QPushButton("Delete")
        self.DeleteTemplateButton.clicked.connect(self.DeleteTemplate)
        self.DoneButton = QPushButton("Done")
        self.DoneButton.clicked.connect(self.Done)

        # Create, Populate, and Set Layout
        self.ButtonLayout = QGridLayout()
        self.ButtonLayout.addWidget(self.AddTemplateButton, 0, 0)
        self.ButtonLayout.addWidget(self.RenameTemplateButton, 0, 1)
        self.ButtonLayout.addWidget(self.DeleteTemplateButton, 0, 2)
        self.ButtonLayout.addWidget(self.DoneButton, 0, 3)

        self.Splitter = QSplitter()
        self.Splitter.addWidget(self.TemplateList)
        self.Splitter.addWidget(self.TemplateDisplay)
        self.Splitter.setStretchFactor(1, 1)

        self.Layout = QGridLayout()
        self.Layout.addWidget(self.Splitter, 0, 0)
        self.Layout.addLayout(self.ButtonLayout, 1, 0)
        self.setLayout(self.Layout)

        # Set Window Title and Icon
        self.setWindowTitle(self.ScriptName + " Template Manager")
        self.setWindowIcon(self.Icon)

        # Window Resize
        self.Resize()

        # Populate Image List
        self.PopulateTemplateList()

        # Execute Dialog
        self.exec_()

    def TemplateSelected(self):
        SelectedItems = self.TemplateList.selectedItems()
        if len(SelectedItems) > 0:
            SelectedItem = SelectedItems[0]
            self.TemplateDisplay.setPlainText(SelectedItem.TemplateContent)

    def PopulateTemplateList(self):
        self.TemplateList.clear()
        self.TemplateDisplay.clear()
        for TemplateName, TemplateContent in sorted(self.RootPage.PageTemplates.items()):
            self.TemplateList.addItem(TemplateListItem(TemplateName, TemplateContent))
        self.TemplateList.setCurrentRow(0)
        self.TemplateList.setFocus()

    def AddTemplate(self):
        AddTemplateDialogInst = AddTemplateDialog(self.RootPage, self.ScriptName, self.Icon, self.DisplayMessageBox, self)
        if AddTemplateDialogInst.TemplateAdded:
            self.RootPage.AddTemplate(AddTemplateDialogInst.TemplateNameString, AddTemplateDialogInst.TemplateString)
            self.UnsavedChanges = True
            self.PopulateTemplateList()

    def RenameTemplate(self):
        SelectedItems = self.TemplateList.selectedItems()
        if len(SelectedItems) > 0:
            CurrentTemplateName = SelectedItems[0].TemplateName
            NewName, OK = QInputDialog.getText(self, "Rename " + CurrentTemplateName, "Enter a name:", text=CurrentTemplateName)
            if OK:
                if NewName == "":
                    self.DisplayMessageBox("Template names cannot be blank.")
                elif NewName in self.RootPage.PageTemplates:
                    self.DisplayMessageBox("There is already a template by that name.")
                else:
                    TemplateContent = self.RootPage.PageTemplates[CurrentTemplateName]
                    self.RootPage.PageTemplates[NewName] = TemplateContent
                    del self.RootPage.PageTemplates[CurrentTemplateName]
                    self.UnsavedChanges = True
                    self.PopulateTemplateList()

    def DeleteTemplate(self):
        SelectedItems = self.TemplateList.selectedItems()
        if len(SelectedItems) > 0:
            CurrentTemplateName = SelectedItems[0].TemplateName
            if self.DisplayMessageBox("Are you sure you want to delete the template " + CurrentTemplateName + " from the notebook?  This cannot be undone.", Icon=QMessageBox.Question, Buttons=(QMessageBox.Yes | QMessageBox.No),
                                      Parent=self) == QMessageBox.Yes:
                del self.RootPage.PageTemplates[CurrentTemplateName]
                self.UnsavedChanges = True
                self.PopulateTemplateList()

    def Done(self):
        self.close()

    def Resize(self):
        self.resize(self.Width, self.Height)


class TemplateListItem(QListWidgetItem):
    def __init__(self, TemplateName, TemplateContent):
        super().__init__()

        # Store Parameters
        self.TemplateName = TemplateName
        self.TemplateContent = TemplateContent

        # Set Text
        self.setText(self.TemplateName)


class AddTemplateDialog(QDialog):
    def __init__(self, RootPage, ScriptName, Icon, DisplayMessageBox, Parent):
        super().__init__(parent=Parent)

        # Store Parameters
        self.RootPage = RootPage
        self.ScriptName = ScriptName
        self.Icon = Icon
        self.DisplayMessageBox = DisplayMessageBox

        # Variables
        self.TemplateAdded = False
        self.TemplateNameString = ""
        self.TemplateString = ""

        # Labels
        self.TemplateTitleLabel = QLabel("Template Title:")
        self.TemplateTextLabel = QLabel("Template Text:")

        # Template Title
        self.TemplateName = QLineEdit()

        # Template Text
        self.TemplateText = QTextEdit()
        self.TemplateText.setTabChangesFocus(True)
        self.TemplateText.setStyleSheet("selection-background-color: rgb(0, 120, 215); selection-color: white")

        # Buttons
        self.DoneButton = QPushButton("Done")
        self.DoneButton.clicked.connect(self.Done)
        self.CancelButton = QPushButton("Cancel")
        self.CancelButton.clicked.connect(self.Cancel)

        # Layout
        self.Layout = QGridLayout()
        self.Layout.addWidget(self.TemplateTitleLabel, 0, 0)
        self.Layout.addWidget(self.TemplateName, 0, 1)
        self.Layout.addWidget(self.TemplateTextLabel, 1, 0)
        self.Layout.addWidget(self.TemplateText, 1, 1)
        self.ButtonsLayout = QGridLayout()
        self.ButtonsLayout.addWidget(self.DoneButton, 0, 0)
        self.ButtonsLayout.addWidget(self.CancelButton, 0, 1)
        self.Layout.addLayout(self.ButtonsLayout, 2, 0, 1, 2)
        self.setLayout(self.Layout)

        # Set Window Title and Icon
        self.setWindowTitle(self.ScriptName)
        self.setWindowIcon(self.Icon)

        # Execute Dialog
        self.exec_()

    def Done(self):
        TemplateNameString = self.TemplateName.text()
        if TemplateNameString == "":
            self.DisplayMessageBox("Template names cannot be blank.", Parent=self)
            return
        if TemplateNameString in self.RootPage.PageTemplates:
            if self.DisplayMessageBox("A template by this name already exists in the notebook.\n\nOverwrite existing template?", Icon=QMessageBox.Question, Buttons=(QMessageBox.Yes | QMessageBox.No),
                                      Parent=self) == QMessageBox.No:
                return
        self.TemplateAdded = True
        self.TemplateNameString = TemplateNameString
        self.TemplateString = self.TemplateText.toPlainText()
        self.close()

    def Cancel(self):
        self.close()
