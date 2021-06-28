import os
import gzip
import json
from datetime import datetime

from PyQt5.QtWidgets import QFileDialog, QMessageBox

from SaveAndLoad.JSONSerializer import JSONSerializer


class SaveAndOpenMixin:
    def __init__(self):
        # Variables
        self.UnsavedChanges = False
        self.CurrentOpenFileName = ""
        self.LastOpenedDirectory = None
        self.FileLastModified = None
        self.GzipMode = False
        from Interface.MainWindow import MainWindow
        self.MainWindowClass = MainWindow

        # Load from Config
        self.LoadLastOpenedDirectory()
        self.LoadGzipMode()

    def Save(self, ObjectToSave, SaveAs=False, AlternateFileDescription=None, AlternateFileExtension=None, SkipSerialization=False, ExportMode=False):
        assert isinstance(self, self.MainWindowClass)
        GzipMode = self.GzipMode if not ExportMode else False
        ActionString = "Save " if not ExportMode else "Export "
        ActionDoneString = "saved" if not ExportMode else "exported"
        Caption = ActionString + (self.FileDescription if AlternateFileDescription is None else AlternateFileDescription) + " File"
        ExtensionWithoutGzip = self.FileExtension if AlternateFileExtension is None else AlternateFileExtension
        GzipExtension = ".gz"
        ModeAndExtensionMatch = (self.CurrentOpenFileName.endswith(ExtensionWithoutGzip) and not GzipMode) or (self.CurrentOpenFileName.endswith(ExtensionWithoutGzip + GzipExtension) and GzipMode)
        Extension = ExtensionWithoutGzip + ("" if not GzipMode else GzipExtension)
        Filter = (self.FileDescription if AlternateFileDescription is None else AlternateFileDescription) + " files (*" + Extension + ")"
        SaveFileName = self.CurrentOpenFileName if self.CurrentOpenFileName != "" and not SaveAs and ModeAndExtensionMatch else QFileDialog.getSaveFileName(caption=Caption, filter=Filter, directory=self.LastOpenedDirectory)[0]
        if SaveFileName == self.CurrentOpenFileName and os.path.isfile(SaveFileName) and self.FileLastModified is not None:
            SaveFileModified = datetime.fromtimestamp(os.path.getmtime(SaveFileName))
            if SaveFileModified != self.FileLastModified:
                if self.DisplayMessageBox("Warning!  The current open file has been modified since it was last saved or opened by this instance of SerpentNotes.  Saving could cause data loss!\n\nProceed?", Icon=QMessageBox.Warning, Buttons=(QMessageBox.Yes | QMessageBox.No)) == QMessageBox.No:
                    return False
        if SaveFileName != "":
            if not SaveFileName.endswith(Extension):
                if SaveFileName.endswith(ExtensionWithoutGzip):
                    SaveFileName += GzipExtension
                else:
                    SaveFileName += Extension
            SaveString = self.JSONSerializer.SerializeDataToJSONString(ObjectToSave) if not SkipSerialization else ObjectToSave
            if GzipMode:
                try:
                    with gzip.open(SaveFileName, "wt") as SaveFile:
                        SaveFile.write(SaveString)
                except FileNotFoundError as Error:
                    self.DisplayMessageBox("Failed to " + ActionString.lower() + " with the following error:\n\n" + str(Error) + "\n\nThis is most likely due to the excessive length of the file paths needed.  Try to " + ActionString.lower() + " to a different location.")
                    self.FlashStatusBar("No file " + ActionDoneString + ".")
                    return False
            else:
                try:
                    with open(SaveFileName, "w") as SaveFile:
                        SaveFile.write(SaveString)
                except FileNotFoundError as Error:
                    self.DisplayMessageBox("Failed to " + ActionString.lower() + " with the following error:\n\n" + str(Error) + "\n\nThis is most likely due to the excessive length of the file paths needed.  Try to " + ActionString.lower() + " to a different location.")
                    self.FlashStatusBar("No file " + ActionDoneString + ".")
                    return False
            SaveFileNameShort = os.path.basename(SaveFileName)
            self.LastOpenedDirectory = os.path.dirname(SaveFileName)
            self.FlashStatusBar("File " + ActionDoneString + " as:  " + SaveFileNameShort)
            if not ExportMode:
                self.CurrentOpenFileName = SaveFileName
                self.UnsavedChanges = False
                self.FileLastModified = datetime.fromtimestamp(os.path.getmtime(SaveFileName))
            return True
        else:
            self.FlashStatusBar("No file " + ActionDoneString + ".")
            return False

    def Open(self, ObjectToSave, FilePath=None, RespectUnsavedChanges=True, AlternateFileDescription=None, AlternateFileExtension=None, ImportMode=False):
        assert isinstance(self, self.MainWindowClass)
        GzipMode = self.GzipMode if not ImportMode else False
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
        Filter = (self.FileDescription if AlternateFileDescription is None else AlternateFileDescription) + " files (*" + (self.FileExtension if AlternateFileExtension is None else AlternateFileExtension) + ("" if not GzipMode else ".gz") + ")"
        OpenFileName = FilePath if FilePath is not None else QFileDialog.getOpenFileName(caption=Caption, filter=Filter, directory=self.LastOpenedDirectory)[0]
        if OpenFileName != "":
            if GzipMode:
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
                self.FileLastModified = datetime.fromtimestamp(os.path.getmtime(OpenFileName))
            return Data
        else:
            self.FlashStatusBar("No file " + ActionDoneString + ".")
            return None

    def New(self, ObjectToSave, RespectUnsavedChanges=True):
        assert isinstance(self, self.MainWindowClass)
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
        self.FileLastModified = None
        return True

    def closeEvent(self, event):
        assert isinstance(self, self.MainWindowClass)
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
        assert isinstance(self, self.MainWindowClass)
        FileSavingConfig = self.GetResourcePath("Configs/LastOpenedDirectory.cfg")
        if os.path.isfile(FileSavingConfig):
            with open(FileSavingConfig, "r") as OpenedConfig:
                LastOpenedDirectory = OpenedConfig.read()
                if os.path.isdir(LastOpenedDirectory):
                    self.LastOpenedDirectory = LastOpenedDirectory

    def LoadGzipMode(self):
        assert isinstance(self, self.MainWindowClass)
        GzipModeConfig = self.GetResourcePath("Configs/GzipMode.cfg")
        if os.path.isfile(GzipModeConfig):
            with open(GzipModeConfig, "r") as OpenedConfig:
                self.GzipMode = json.loads(OpenedConfig.read())

    def SaveLastOpenedDirectory(self):
        assert isinstance(self, self.MainWindowClass)
        FileSavingConfig = self.GetResourcePath("Configs/LastOpenedDirectory.cfg")
        if type(self.LastOpenedDirectory) == str:
            if os.path.isdir(self.LastOpenedDirectory):
                with open(FileSavingConfig, "w") as OpenedConfig:
                    OpenedConfig.write(self.LastOpenedDirectory)

    def SaveGzipMode(self):
        assert isinstance(self, self.MainWindowClass)
        GzipModeConfig = self.GetResourcePath("Configs/GzipMode.cfg")
        with open(GzipModeConfig, "w") as OpenedConfig:
            OpenedConfig.write(json.dumps(self.GzipMode))
