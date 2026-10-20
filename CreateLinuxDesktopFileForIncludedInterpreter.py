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

ApplicationsFolder = os.path.expanduser(os.path.join("~", ".local", "share", "applications"))

if not os.path.isdir(ApplicationsFolder):
    os.mkdir(ApplicationsFolder)

CreatedDesktopFilePath = f"{AppName}.desktop"
DesktopFileDestinationPath = os.path.join(ApplicationsFolder, CreatedDesktopFilePath)

with open(CreatedDesktopFilePath, "w") as DesktopFile:
    DesktopFile.write(DesktopFileContents)

if os.path.isfile(DesktopFileDestinationPath):
    os.remove(DesktopFileDestinationPath)

shutil.move(CreatedDesktopFilePath, DesktopFileDestinationPath)
