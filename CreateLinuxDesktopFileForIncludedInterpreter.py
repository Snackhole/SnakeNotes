import os
import shutil

AppName = "SnakeNotes"

ExecutableZip = f"{AppName}.pyzw"
CurrentWorkingDirectory = os.getcwd()
AbsolutePathToIncludedInterpreter = os.path.join(CurrentWorkingDirectory, "Python Interpreter - Linux", "bin", "python3")
AbsolutePathToExecutableZip = os.path.join(CurrentWorkingDirectory, ExecutableZip)
AbsolutePathToIconPNG = os.path.join(CurrentWorkingDirectory, "Assets", f"{AppName} Icon.png")

DesktopFileContents = f"""[Desktop Entry]
Type=Application
Name={AppName}
Exec="{AbsolutePathToIncludedInterpreter}" "{AbsolutePathToExecutableZip}"
Icon={AbsolutePathToIconPNG}
Categories=Application;"""

CreatedDesktopFilePath = f"{AppName}.desktop"
DesktopFileDestinationPath = os.path.expanduser(os.path.join("~", ".local", "share", "applications", CreatedDesktopFilePath))

with open(CreatedDesktopFilePath, "w") as DesktopFile:
    DesktopFile.write(DesktopFileContents)

if os.path.isfile(DesktopFileDestinationPath):
    os.remove(DesktopFileDestinationPath)

shutil.move(CreatedDesktopFilePath, DesktopFileDestinationPath)
