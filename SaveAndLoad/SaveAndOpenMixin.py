import os
import gzip
import json

from PyQt5.QtWidgets import QFileDialog, QMessageBox

from SaveAndLoad.JSONSerializer import JSONSerializer


class SaveAndOpenMixin:
    def __init__(self):
        # Variables
        self.UnsavedChanges = False
        self.CurrentOpenFileName = ""
        self.LastOpenedDirectory = None
        self.GzipMode = False

        # Load from Config
        self.LoadLastOpenedDirectory()
        self.LoadGzipMode()

    def Save(self, ObjectToSave, SaveAs=False, AlternateFileDescription=None, AlternateFileExtension=None, SkipSerialization=False, ExportMode=False):
        from Interface.MainWindow import MainWindow
        assert isinstance(self, MainWindow)
        ActionString = "Save " if not ExportMode else "Export "
        ActionDoneString = "saved" if not ExportMode else "exported"
        Caption = ActionString + (self.FileDescription if AlternateFileDescription is None else AlternateFileDescription) + " File"
        ExtensionWithoutGzip = self.FileExtension if AlternateFileExtension is None else AlternateFileExtension
        GzipExtension = ".gz"
        Extension = ExtensionWithoutGzip + ("" if not self.GzipMode else GzipExtension)
        Filter = (self.FileDescription if AlternateFileDescription is None else AlternateFileDescription) + " files (*" + Extension + ")"
        SaveFileName = self.CurrentOpenFileName if self.CurrentOpenFileName != "" and not SaveAs else QFileDialog.getSaveFileName(caption=Caption, filter=Filter, directory=self.LastOpenedDirectory)[0]
        if SaveFileName != "":
            if not SaveFileName.endswith(Extension):
                if SaveFileName.endswith(ExtensionWithoutGzip):
                    SaveFileName += GzipExtension
                else:
                    SaveFileName += Extension
            SaveString = self.JSONSerializer.SerializeDataToJSONString(ObjectToSave) if not SkipSerialization else ObjectToSave
            if self.GzipMode:
                with gzip.open(SaveFileName, "wt") as SaveFile:
                    SaveFile.write(SaveString)
            else:
                with open(SaveFileName, "w") as SaveFile:
                    SaveFile.write(SaveString)
            SaveFileNameShort = os.path.basename(SaveFileName)
            self.LastOpenedDirectory = os.path.dirname(SaveFileName)
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
        Filter = (self.FileDescription if AlternateFileDescription is None else AlternateFileDescription) + " files (*" + (self.FileExtension if AlternateFileExtension is None else AlternateFileExtension) + ("" if not self.GzipMode else ".gz") + ")"
        OpenFileName = FilePath if FilePath is not None else QFileDialog.getOpenFileName(caption=Caption, filter=Filter, directory=self.LastOpenedDirectory)[0]
        if OpenFileName != "":
            if self.GzipMode:
                with gzip.open(OpenFileName, "rt") as LoadFile:
                    JSONString = LoadFile.read()
            else:
                with open(OpenFileName, "r") as LoadFile:
                    JSONString = LoadFile.read()
            OpenFileNameShort = os.path.basename(OpenFileName)
            try:
                Data = self.JSONSerializer.DeserializeDataFromJSONString(JSONString)
            except KeyError:
                self.DisplayMessageBox("There was an error " + ActionInProgressString + " " + OpenFileNameShort + ".")
                return None
            self.LastOpenedDirectory = os.path.dirname(OpenFileName)
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
                self.SaveLastOpenedDirectory()
                self.SaveGzipMode()
                event.accept()
            elif SavePrompt == QMessageBox.No:
                event.ignore()
        else:
            self.SaveLastOpenedDirectory()
            self.SaveGzipMode()
            event.accept()

    def SetUpSaveAndOpen(self, FileExtension, FileDescription, ObjectClasses):
        self.FileExtension = FileExtension
        self.FileDescription = FileDescription
        self.JSONSerializer = JSONSerializer(ObjectClasses)

    def LoadLastOpenedDirectory(self):
        from Interface.MainWindow import MainWindow
        assert isinstance(self, MainWindow)
        FileSavingConfig = self.GetResourcePath("LastOpenedDirectory.cfg")
        if os.path.isfile(FileSavingConfig):
            with open(FileSavingConfig, "r") as OpenedConfig:
                LastOpenedDirectory = OpenedConfig.read()
                if os.path.isdir(LastOpenedDirectory):
                    self.LastOpenedDirectory = LastOpenedDirectory

    def LoadGzipMode(self):
        from Interface.MainWindow import MainWindow
        assert isinstance(self, MainWindow)
        GzipModeConfig = self.GetResourcePath("GzipMode.cfg")
        if os.path.isfile(GzipModeConfig):
            with open(GzipModeConfig, "r") as OpenedConfig:
                self.GzipMode = json.loads(OpenedConfig.read())

    def SaveLastOpenedDirectory(self):
        from Interface.MainWindow import MainWindow
        assert isinstance(self, MainWindow)
        FileSavingConfig = self.GetResourcePath("LastOpenedDirectory.cfg")
        if type(self.LastOpenedDirectory) == str:
            if os.path.isdir(self.LastOpenedDirectory):
                with open(FileSavingConfig, "w") as OpenedConfig:
                    OpenedConfig.write(self.LastOpenedDirectory)

    def SaveGzipMode(self):
        from Interface.MainWindow import MainWindow
        assert isinstance(self, MainWindow)
        GzipModeConfig = self.GetResourcePath("GzipMode.cfg")
        with open(GzipModeConfig, "w") as OpenedConfig:
            OpenedConfig.write(json.dumps(self.GzipMode))
