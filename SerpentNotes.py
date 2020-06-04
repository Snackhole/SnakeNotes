import os
import sys

sys.path.append(os.getcwd())

from PyQt5.QtWidgets import QApplication

from Interface.MainWindow import MainWindow
from Build import VersionedAppName


def StartApp():
    AppInst = QApplication(sys.argv)

    # Main Window Interface
    ScriptName = VersionedAppName
    MainWindowInst = MainWindow(ScriptName)

    # Enter Main Loop
    sys.exit(AppInst.exec_())


if __name__ == "__main__":
    StartApp()
