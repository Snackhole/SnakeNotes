import os

AppName = "SnakeNotes"

ExecutableZip = AppName + ".pyzw"
CurrentWorkingDirectory = os.getcwd()
AbsolutePathToIncludedInterpreter = CurrentWorkingDirectory + "/Python Interpreter - Linux/bin/python3"
AbsolutePathToExecutableZip = CurrentWorkingDirectory + "/" + ExecutableZip
AbsolutePathToIconPNG = CurrentWorkingDirectory + "/Assets/" + AppName + " Icon.png"

DesktopFileContents = """[Desktop Entry]
Type=Application
Name={0}
Exec="{1}" "{2}"
Icon={3}
Categories=Application;"""
DesktopFileContents = DesktopFileContents.format(AppName, AbsolutePathToIncludedInterpreter, AbsolutePathToExecutableZip, AbsolutePathToIconPNG)

with open(AppName + ".desktop", "w") as DesktopFile:
    DesktopFile.write(DesktopFileContents)
