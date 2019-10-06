import os

from PyQt5.QtWidgets import QFileDialog, QMessageBox

from SaveAndLoad.JSONSerializer import JSONSerializer


class SaveAndOpenMixin:
    def __init__(self):
        # Variables
        self.UnsavedChanges = False
        self.CurrentOpenFileName = ""

    def Save(self, ObjectToSerialize, SaveAs=False, AlternateFileDescription=None, AlternateFileExtension=None):
        from Interface.MainWindow import MainWindow
        assert isinstance(self, MainWindow)
        Caption = "Save " + (self.FileDescription if AlternateFileDescription is None else AlternateFileDescription) + " File"
        Filter = (self.FileDescription if AlternateFileDescription is None else AlternateFileDescription) + " files (*" + (self.FileExtension if AlternateFileExtension is None else AlternateFileExtension) + ")"
        SaveFileName = self.CurrentOpenFileName if self.CurrentOpenFileName != "" and not SaveAs else QFileDialog.getSaveFileName(caption=Caption, filter=Filter)[0]
        if SaveFileName != "":
            JSONString = self.JSONSerializer.SerializeDataToJSONString(ObjectToSerialize)
            with open(SaveFileName, "w") as SaveFile:
                SaveFile.write(JSONString)
            self.CurrentOpenFileName = SaveFileName
            SaveFileNameShort = os.path.basename(SaveFileName)
            self.FlashStatusBar("File saved as:  " + SaveFileNameShort)
            self.UnsavedChanges = False
            return True
        else:
            self.FlashStatusBar("No file saved.")
            return False

    def Open(self, ObjectToSerialize, FilePath=None, RespectUnsavedChanges=True, AlternateFileDescription=None, AlternateFileExtension=None):
        from Interface.MainWindow import MainWindow
        assert isinstance(self, MainWindow)
        if self.UnsavedChanges and RespectUnsavedChanges:
            SavePrompt = self.DisplayMessageBox("Save unsaved work before opening?", Icon=QMessageBox.Warning, Buttons=(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel))
            if SavePrompt == QMessageBox.Yes:
                if not self.Save(ObjectToSerialize):
                    return None
            elif SavePrompt == QMessageBox.No:
                pass
            elif SavePrompt == QMessageBox.Cancel:
                return None
        Caption = "Open " + (self.FileDescription if AlternateFileDescription is None else AlternateFileDescription) + " File"
        Filter = (self.FileDescription if AlternateFileDescription is None else AlternateFileDescription) + " files (*" + (self.FileExtension if AlternateFileExtension is None else AlternateFileExtension) + ")"
        OpenFileName = FilePath if FilePath is not None else QFileDialog.getOpenFileName(caption=Caption, filter=Filter)[0]
        if OpenFileName != "":
            with open(OpenFileName, "r") as LoadFile:
                JSONString = LoadFile.read()
            OpenFileNameShort = os.path.basename(OpenFileName)
            try:
                Data = self.JSONSerializer.DeserializeDataFromJSONString(JSONString)
            except KeyError:
                self.DisplayMessageBox("There was an error opening " + OpenFileNameShort + ".")
                return None
            self.CurrentOpenFileName = OpenFileName
            self.FlashStatusBar("Opened file:  " + OpenFileNameShort)
            self.UnsavedChanges = False
            return Data
        else:
            self.FlashStatusBar("No file opened.")
            return None

    def New(self, ObjectToSerialize, RespectUnsavedChanges=True):
        from Interface.MainWindow import MainWindow
        assert isinstance(self, MainWindow)
        if self.UnsavedChanges and RespectUnsavedChanges:
            SavePrompt = self.DisplayMessageBox("Save unsaved work before starting a new file?", Icon=QMessageBox.Warning, Buttons=(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel))
            if SavePrompt == QMessageBox.Yes:
                if not self.Save(ObjectToSerialize):
                    return False
            elif SavePrompt == QMessageBox.No:
                pass
            elif SavePrompt == QMessageBox.Cancel:
                return False
        self.CurrentOpenFileName = ""
        self.FlashStatusBar("New file opened.")
        self.UnsavedChanges = False
        return True

    def closeEvent(self, event):
        from Interface.MainWindow import MainWindow
        assert isinstance(self, MainWindow)
        if self.UnsavedChanges:
            SavePrompt = self.DisplayMessageBox("There are unsaved changes.  Close anyway?", Icon=QMessageBox.Warning, Buttons=(QMessageBox.Yes | QMessageBox.No))
            if SavePrompt == QMessageBox.Yes:
                event.accept()
            elif SavePrompt == QMessageBox.No:
                event.ignore()
        else:
            event.accept()

    def SetUpSaveAndOpen(self, FileExtension, FileDescription, ObjectClasses):
        self.FileExtension = FileExtension
        self.FileDescription = FileDescription
        self.JSONSerializer = JSONSerializer(ObjectClasses)
