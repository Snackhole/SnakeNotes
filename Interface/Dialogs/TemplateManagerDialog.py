from PyQt5.QtWidgets import QDialog, QListWidget, QTextEdit, QListWidgetItem, QPushButton, QGridLayout, QMessageBox, QLabel, QLineEdit, QSplitter, QInputDialog


class TemplateManagerDialog(QDialog):
    def __init__(self, Notebook, MainWindow):
        super().__init__(parent=MainWindow)

        # Store Parameters
        self.Notebook = Notebook
        self.MainWindow = MainWindow

        # Variables
        self.UnsavedChanges = False
        self.Width = max(self.MainWindow.width() - 100, 100)
        self.Height = max(self.MainWindow.height() - 100, 100)

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
        self.EditTemplateButton = QPushButton("Edit")
        self.EditTemplateButton.clicked.connect(self.EditTemplate)
        self.RenameTemplateButton = QPushButton("Rename")
        self.RenameTemplateButton.clicked.connect(self.RenameTemplate)
        self.DeleteTemplateButton = QPushButton("Delete")
        self.DeleteTemplateButton.clicked.connect(self.DeleteTemplate)
        self.DoneButton = QPushButton("Done")
        self.DoneButton.clicked.connect(self.Done)

        # Create, Populate, and Set Layout
        self.ButtonLayout = QGridLayout()
        self.ButtonLayout.addWidget(self.AddTemplateButton, 0, 0)
        self.ButtonLayout.addWidget(self.EditTemplateButton, 0, 1)
        self.ButtonLayout.addWidget(self.RenameTemplateButton, 0, 2)
        self.ButtonLayout.addWidget(self.DeleteTemplateButton, 0, 3)
        self.ButtonLayout.addWidget(self.DoneButton, 0, 4)

        self.Splitter = QSplitter()
        self.Splitter.addWidget(self.TemplateList)
        self.Splitter.addWidget(self.TemplateDisplay)
        self.Splitter.setStretchFactor(1, 1)

        self.Layout = QGridLayout()
        self.Layout.addWidget(self.Splitter, 0, 0)
        self.Layout.addLayout(self.ButtonLayout, 1, 0)
        self.setLayout(self.Layout)

        # Set Window Title and Icon
        self.setWindowTitle("Template Manager")
        self.setWindowIcon(self.MainWindow.WindowIcon)

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
        for TemplateName, TemplateContent in sorted(self.Notebook.PageTemplates.items(), key=lambda Template: Template[0].lower()):
            self.TemplateList.addItem(TemplateListItem(TemplateName, TemplateContent))
        self.TemplateList.setCurrentRow(0)
        self.TemplateList.setFocus()

    def AddTemplate(self):
        AddTemplateDialogInst = AddTemplateDialog(self.Notebook, self.MainWindow, self)
        if AddTemplateDialogInst.TemplateAdded:
            self.Notebook.AddTemplate(AddTemplateDialogInst.TemplateNameString, AddTemplateDialogInst.TemplateString)
            self.UnsavedChanges = True
            self.PopulateTemplateList()
            self.TemplateList.setCurrentRow(self.GetTemplateIndexFromName(AddTemplateDialogInst.TemplateNameString))

    def EditTemplate(self):
        SelectedItems = self.TemplateList.selectedItems()
        if len(SelectedItems) > 0:
            CurrentTemplateName = SelectedItems[0].TemplateName
            CurrentTemplateContent = SelectedItems[0].TemplateContent
            EditTemplateDialogInst = AddTemplateDialog(self.Notebook, self.MainWindow, self, EditMode=True, TemplateTitle=CurrentTemplateName, TemplateContent=CurrentTemplateContent)
            if EditTemplateDialogInst.TemplateAdded:
                self.Notebook.PageTemplates[CurrentTemplateName] = EditTemplateDialogInst.TemplateString
                self.UnsavedChanges = True
                self.PopulateTemplateList()
                self.TemplateList.setCurrentRow(self.GetTemplateIndexFromName(CurrentTemplateName))

    def RenameTemplate(self):
        SelectedItems = self.TemplateList.selectedItems()
        if len(SelectedItems) > 0:
            CurrentTemplateName = SelectedItems[0].TemplateName
            NewName, OK = QInputDialog.getText(self, "Rename " + CurrentTemplateName, "Enter a name:", text=CurrentTemplateName)
            if OK:
                if NewName == "":
                    self.MainWindow.DisplayMessageBox("Template names cannot be blank.")
                elif NewName in self.Notebook.PageTemplates:
                    self.MainWindow.DisplayMessageBox("There is already a template by that name.")
                else:
                    TemplateContent = self.Notebook.PageTemplates[CurrentTemplateName]
                    self.Notebook.PageTemplates[NewName] = TemplateContent
                    del self.Notebook.PageTemplates[CurrentTemplateName]
                    self.UnsavedChanges = True
                    self.PopulateTemplateList()
                    self.TemplateList.setCurrentRow(self.GetTemplateIndexFromName(NewName))

    def DeleteTemplate(self):
        SelectedItems = self.TemplateList.selectedItems()
        if len(SelectedItems) > 0:
            CurrentTemplateName = SelectedItems[0].TemplateName
            CurrentTemplateRow = self.TemplateList.currentRow()
            if self.MainWindow.DisplayMessageBox("Are you sure you want to delete the template " + CurrentTemplateName + " from the notebook?  This cannot be undone.", Icon=QMessageBox.Question, Buttons=(QMessageBox.Yes | QMessageBox.No), Parent=self) == QMessageBox.Yes:
                del self.Notebook.PageTemplates[CurrentTemplateName]
                self.UnsavedChanges = True
                self.PopulateTemplateList()
                if self.TemplateList.count() == 0:
                    pass
                elif CurrentTemplateRow == self.TemplateList.count():
                    self.TemplateList.setCurrentRow(CurrentTemplateRow - 1)
                else:
                    self.TemplateList.setCurrentRow(CurrentTemplateRow)

    def GetTemplateIndexFromName(self, TemplateName):
        TemplateNames = sorted(self.Notebook.PageTemplates.keys(), key=lambda Template: Template.lower())
        return TemplateNames.index(TemplateName)

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
    def __init__(self, Notebook, MainWindow, Parent, EditMode=False, TemplateTitle="", TemplateContent=""):
        super().__init__(parent=Parent)

        # Store Parameters
        self.Notebook = Notebook
        self.MainWindow = MainWindow
        self.EditMode = EditMode
        self.TemplateTitle = TemplateTitle
        self.TemplateContent = TemplateContent

        # Variables
        self.TemplateAdded = False
        self.TemplateNameString = ""
        self.TemplateString = ""

        # Labels
        self.TemplateTitleLabel = QLabel("Template Title:")
        self.TemplateTextLabel = QLabel("Template Text:")

        # Template Title
        self.TemplateName = QLineEdit()
        self.TemplateName.setText(self.TemplateTitle)
        if self.EditMode:
            self.TemplateName.setEnabled(False)

        # Template Text
        self.TemplateText = QTextEdit()
        self.TemplateText.setPlainText(self.TemplateContent)
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
        self.setWindowTitle("Add Template" if not self.EditMode else "Edit Template")
        self.setWindowIcon(self.MainWindow.WindowIcon)

        # Execute Dialog
        self.exec_()

    def Done(self):
        TemplateNameString = self.TemplateName.text()
        if TemplateNameString == "":
            self.MainWindow.DisplayMessageBox("Template names cannot be blank.", Parent=self)
            return
        if TemplateNameString in self.Notebook.PageTemplates and not self.EditMode:
            if self.MainWindow.DisplayMessageBox("A template by this name already exists in the notebook.\n\nOverwrite existing template?", Icon=QMessageBox.Question, Buttons=(QMessageBox.Yes | QMessageBox.No), Parent=self) == QMessageBox.No:
                return
        self.TemplateAdded = True
        self.TemplateNameString = TemplateNameString
        self.TemplateString = self.TemplateText.toPlainText()
        self.close()

    def Cancel(self):
        self.close()
