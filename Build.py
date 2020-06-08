import os
import platform
import shutil
import zipapp

# Build Variables
Version = "30"
AppName = "SerpentNotes"
VersionedAppName = AppName + " " + Version


def Build():
    # Additional Build Variables
    OS = platform.system()
    CodeFiles = ["Core", "Interface", "SaveAndLoad", "Build.py", "SerpentNotes.py"]
    AssetFiles = ["Assets"]
    if OS == "Linux":
        AssetFiles.append("CreateGNOMEDesktopFile.py")

    ExecutableZipName = AppName + ".pyzw"
    Interpreter = "python3"
    Main = AppName + ":StartApp"

    BuildFolder = "BUILD - " + VersionedAppName

    # Build Functions
    def CopyFilesToBuildFolder(CopiedFiles):
        IgnoredFiles = [File for File in os.listdir(".") if File not in CopiedFiles]
        shutil.copytree(".", BuildFolder, ignore=lambda Source, Contents: IgnoredFiles)

    def CleanUp():
        shutil.rmtree(BuildFolder)
        print("Build files cleaned up.")

    # Copy Code to Build Folder
    CopyFilesToBuildFolder(CodeFiles)
    print("Code files copied to build folder.")

    # Create Executable Archive
    zipapp.create_archive(BuildFolder, ExecutableZipName, Interpreter, Main)
    print("Executable archive created.")

    # Delete Build Folder
    shutil.rmtree(BuildFolder)
    print("Build folder deleted.")

    # Copy Assets to Build Folder and Move Executable Zip
    CopyFilesToBuildFolder(AssetFiles)
    print("Assets copied to build folder.")
    shutil.move(ExecutableZipName, BuildFolder)
    print("Executable archive moved to build folder.")

    # Prompt to Install Dependencies
    CurrentWorkingDirectory = os.getcwd()
    if OS == "Linux":
        CommandPrompt = "pip3 install -r \"" + CurrentWorkingDirectory + "/requirements.txt\" --target \"" + CurrentWorkingDirectory + "/" + BuildFolder + "\""
    elif OS == "Windows":
        CommandPrompt = "python -m pip install -r \"" + CurrentWorkingDirectory + "\\requirements.txt\" --target \"" + CurrentWorkingDirectory + "\\" + BuildFolder + "\""
    else:
        CommandPrompt = "OS unsupported; unknown command to install dependencies."
    ProceedPrompt = "\n---\nInstall dependencies to build folder (" + BuildFolder + ") using a command prompt:\n\n    " + CommandPrompt + "\n\nOnce all dependencies are installed, input \"PROCEED\" to continue with build or \"CANCEL\" to cancel and clean up build files:\n---\n"
    ProceedResponse = input(ProceedPrompt)
    if ProceedResponse == "PROCEED":
        pass
    elif ProceedResponse == "CANCEL":
        print("Build canceled.")
        CleanUp()
        return
    else:
        return

    # Zip Build
    shutil.make_archive(VersionedAppName + " - " + OS, "zip", BuildFolder)
    print("Build zipped.")

    # Clean Up
    CleanUp()


if __name__ == "__main__":
    Build()
