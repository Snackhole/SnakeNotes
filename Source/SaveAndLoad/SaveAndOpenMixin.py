import os

from PyQt5.QtWidgets import QFileDialog, QMessageBox

from SaveAndLoad.JSONSerializer import JSONSerializer


class SaveAndOpenMixin:
    def __init__(self):
        # Variables
        self.UnsavedChanges = False
        self.CurrentOpenFileName = ""

    def Save(self, ObjectToSave, SaveAs=False, AlternateFileDescription=None, AlternateFileExtension=None, SkipSerialization=False, ExportMode=False):
        from Interface.MainWindow import MainWindow
        assert isinstance(self, MainWindow)
        ActionString = "Save " if not ExportMode else "Export "
        ActionDoneString = "saved" if not ExportMode else "exported"
        Caption = ActionString + (self.FileDescription if AlternateFileDescription is None else AlternateFileDescription) + " File"
        Filter = (self.FileDescription if AlternateFileDescription is None else AlternateFileDescription) + " files (*" + (self.FileExtension if AlternateFileExtension is None else AlternateFileExtension) + ")"
        SaveFileName = self.CurrentOpenFileName if self.CurrentOpenFileName != "" and not SaveAs else QFileDialog.getSaveFileName(caption=Caption, filter=Filter)[0]
        if SaveFileName != "":
            SaveString = self.JSONSerializer.SerializeDataToJSONString(ObjectToSave) if not SkipSerialization else ObjectToSave
            with open(SaveFileName, "w") as SaveFile:
                SaveFile.write(SaveString)
            SaveFileNameShort = os.path.basename(SaveFileName)
            self.FlashStatusBar("File " + ActionDoneString + " as:  " + SaveFileNameShort)
            if not ExportMode:
                self.CurrentOpenFileName = SaveFileName
                self.UnsavedChanges = False
            return True
        else:
            self.FlashStatusBar("No file " + ActionDoneString + ".")
            return False

    def Open(self, ObjectToSave, FilePath=None, RespectUnsavedChanges=True, AlternateFileDescription=None, AlternateFileExtension=None, ImportMode=False):
        from Interface.MainWindow import MainWindow
        assert isinstance(self, MainWindow)
        ActionString = "Open " if not ImportMode else "Import "
        ActionInProgressString = "opening" if not ImportMode else "importing"
        ActionDoneString = "opened" if not ImportMode else "imported"
        ActionDoneStringCapitalized = "Opened" if not ImportMode else "Imported"
        if self.UnsavedChanges and RespectUnsavedChanges:
            SavePrompt = self.DisplayMessageBox("Save unsaved work before " + ActionInProgressString + "?", Icon=QMessageBox.Warning, Buttons=(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel))
            if SavePrompt == QMessageBox.Yes:
                if not self.Save(ObjectToSave):
                    return None
            elif SavePrompt == QMessageBox.No:
                pass
            elif SavePrompt == QMessageBox.Cancel:
                return None
        Caption = ActionString + (self.FileDescription if AlternateFileDescription is None else AlternateFileDescription) + " File"
        Filter = (self.FileDescription if AlternateFileDescription is None else AlternateFileDescription) + " files (*" + (self.FileExtension if AlternateFileExtension is None else AlternateFileExtension) + ")"
        OpenFileName = FilePath if FilePath is not None else QFileDialog.getOpenFileName(caption=Caption, filter=Filter)[0]
        if OpenFileName != "":
            with open(OpenFileName, "r") as LoadFile:
                JSONString = LoadFile.read()
            OpenFileNameShort = os.path.basename(OpenFileName)
            try:
                Data = self.JSONSerializer.DeserializeDataFromJSONString(JSONString)
            except KeyError:
                self.DisplayMessageBox("There was an error " + ActionInProgressString + " " + OpenFileNameShort + ".")
                return None
            self.FlashStatusBar(ActionDoneStringCapitalized + " file:  " + OpenFileNameShort)
            if not ImportMode:
                self.CurrentOpenFileName = OpenFileName
                self.UnsavedChanges = False
            return Data
        else:
            self.FlashStatusBar("No file " + ActionDoneString + ".")
            return None

    def New(self, ObjectToSave, RespectUnsavedChanges=True):
        from Interface.MainWindow import MainWindow
        assert isinstance(self, MainWindow)
        if self.UnsavedChanges and RespectUnsavedChanges:
            SavePrompt = self.DisplayMessageBox("Save unsaved work before starting a new file?", Icon=QMessageBox.Warning, Buttons=(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel))
            if SavePrompt == QMessageBox.Yes:
                if not self.Save(ObjectToSave):
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
