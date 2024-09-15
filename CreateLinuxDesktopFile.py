import os
import shutil

AppName = "SnakeNotes"

ExecutableZip = f"{AppName}.pyzw"
CurrentWorkingDirectory = os.getcwd()
AbsolutePathToExecutableZip = os.path.join(CurrentWorkingDirectory, ExecutableZip)
AbsolutePathToIconPNG = os.path.join(CurrentWorkingDirectory, "Assets", f"{AppName} Icon.png")

DesktopFileContents = f"""[Desktop Entry]
Type=Application
Name={AppName}
Exec=python3 "{AbsolutePathToExecutableZip}"
Icon={AbsolutePathToIconPNG}
Categories=Application;"""

CreatedDesktopFilePath = f"{AppName}.desktop"
DesktopFileDestinationPath = os.path.expanduser(os.path.join("~", ".local", "share", "applications", CreatedDesktopFilePath))

with open(CreatedDesktopFilePath, "w") as DesktopFile:
    DesktopFile.write(DesktopFileContents)

if os.path.isfile(DesktopFileDestinationPath):
    os.remove(DesktopFileDestinationPath)

shutil.move(CreatedDesktopFilePath, DesktopFileDestinationPath)
