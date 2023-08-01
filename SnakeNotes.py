import os
import sys

AbsoluteDirectoryPath = os.path.dirname(__file__)
if AbsoluteDirectoryPath.endswith(".pyz") or AbsoluteDirectoryPath.endswith(".pyzw"):
    AbsoluteDirectoryPath = os.path.dirname(AbsoluteDirectoryPath)
if sys.path[0] != AbsoluteDirectoryPath:
    sys.path.insert(0, AbsoluteDirectoryPath)

from PyQt5.QtWidgets import QApplication

from Interface.MainWindow import MainWindow
from Build import BuildVariables


def StartApp():
    AppInst = QApplication(sys.argv)

    # Main Window Interface
    ScriptName = BuildVariables["VersionedAppName"]
    MainWindowInst = MainWindow(ScriptName, AbsoluteDirectoryPath, AppInst)

    # Enter Main Loop
    sys.exit(AppInst.exec_())


if __name__ == "__main__":
    StartApp()
