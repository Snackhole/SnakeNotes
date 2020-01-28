import os
import shutil
import sys
from zipfile import ZipFile

import winshell
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QPushButton, QCheckBox, QApplication, QGridLayout, QTextEdit, QFileDialog, QMessageBox
from win32com.client import Dispatch


class InstallerWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Variables
        self.WindowIcon = QIcon(self.ResourcePath("Source/Assets/SerpentNotes Icon.png"))
        self.ScriptName = os.path.splitext(os.path.basename(__file__))[0]
        self.SerpentNotesScriptName = self.ScriptName[:-10]
        self.ProgramZip = self.ResourcePath("Executables/Final/" + self.SerpentNotesScriptName + ".zip")

        # Install Location
        self.InstallLocationTextEdit = QTextEdit()
        self.InstallLocationTextEdit.setDisabled(True)
        self.InstallLocationTextEdit.setFixedHeight(75)
        self.InstallLocationButton = QPushButton("Install Location")
        self.InstallLocationButton.clicked.connect(self.SetInstallLocation)

        # Desktop Shortcut
        self.DesktopShortcutCheckBox = QCheckBox("Create desktop shortcut?")

        # Install Button
        self.InstallButton = QPushButton("Install")
        self.InstallButton.clicked.connect(self.Install)

        # Configure Window
        self.setWindowTitle(self.ScriptName)
        self.setWindowIcon(self.WindowIcon)

        # Layout
        self.Layout = QGridLayout()
        self.Layout.addWidget(self.InstallLocationTextEdit, 0, 0, 3, 1)
        self.Layout.addWidget(self.InstallLocationButton, 0, 1)
        self.Layout.addWidget(self.DesktopShortcutCheckBox, 1, 1)
        self.Layout.addWidget(self.InstallButton, 2, 1)
        self.setLayout(self.Layout)

        # Show Window
        self.show()

    def SetInstallLocation(self):
        InstallPath = QFileDialog.getExistingDirectory(caption="Install Directory")
        if InstallPath != "":
            self.InstallLocationTextEdit.setPlainText(InstallPath)

    def Install(self):
        InstallLocation = self.InstallLocationTextEdit.toPlainText()

        if InstallLocation == "":
            self.DisplayMessageBox("Cannot install until a location has been chosen.")
            return

        if self.DisplayMessageBox("WARNING:  All files currently in the chosen location will be deleted and replaced with SerpentNotes' files.  Proceed?", Buttons=(QMessageBox.Yes | QMessageBox.No),
                                  Icon=QMessageBox.Warning) == QMessageBox.No:
            return

        try:
            for File in os.listdir(InstallLocation):
                FilePath = os.path.join(InstallLocation, File)
                if os.path.isfile(FilePath) and File != "Favorites.cfg" and File != "DisplaySettings.cfg" and File != "LastOpenedDirectory.cfg":
                    os.unlink(FilePath)
                elif os.path.isdir(FilePath):
                    shutil.rmtree(FilePath)
            with ZipFile(self.ProgramZip, mode="r") as Program:
                Program.extractall(InstallLocation)
            if self.DesktopShortcutCheckBox.isChecked():
                ShortcutTarget = os.path.join(InstallLocation, "SerpentNotes.exe")
                Shell = Dispatch("WScript.Shell")
                Shortcut = Shell.CreateShortCut(os.path.join(winshell.desktop(), "SerpentNotes.lnk"))
                Shortcut.Targetpath = ShortcutTarget
                Shortcut.WorkingDirectory = InstallLocation
                Shortcut.IconLocation = ShortcutTarget
                Shortcut.save()
        except Exception as Error:
            self.DisplayMessageBox("An error occurred during installation.\n\n" + str(Error), Icon=QMessageBox.Warning)
            return

        self.DisplayMessageBox("SerpentNotes has been installed to the chosen location.")
        self.close()

    def ResourcePath(self, RelativePath):
        BasePath = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(BasePath, RelativePath)

    def DisplayMessageBox(self, Message, Icon=QMessageBox.Information, Buttons=QMessageBox.Ok, Parent=None):
        MessageBox = QMessageBox(self if Parent is None else Parent)
        MessageBox.setWindowIcon(self.WindowIcon)
        MessageBox.setWindowTitle(self.ScriptName)
        MessageBox.setIcon(Icon)
        MessageBox.setText(Message)
        MessageBox.setStandardButtons(Buttons)
        return MessageBox.exec_()


if __name__ == "__main__":
    AppInst = QApplication(sys.argv)

    # Main Window Interface
    InstallerWindowInst = InstallerWindow()

    # Enter Main Loop
    sys.exit(AppInst.exec_())
