import os
import platform
import shutil
import zipapp

# Build Variables
BuildVariables = {}
BuildVariables["Version"] = "31"
BuildVariables["AppName"] = "SerpentNotes"
BuildVariables["VersionedAppName"] = BuildVariables["AppName"] + " " + BuildVariables["Version"]


def Build():
    # Build Functions
    def CopyFilesToBuildFolder(CopiedFiles):
        if "BuildFolder" in BuildVariables:
            IgnoredFiles = [File for File in os.listdir(".") if File not in CopiedFiles]
            shutil.copytree(".", BuildVariables["BuildFolder"], ignore=lambda Source, Contents: IgnoredFiles)

    def CleanUp():
        if "BuildFolder" in BuildVariables:
            shutil.rmtree(BuildVariables["BuildFolder"])
            print("Build files cleaned up.")

    # Additional Build Variables
    BuildVariables["BuildFolder"] = "BUILD - " + BuildVariables["VersionedAppName"]
    BuildVariables["OS"] = platform.system()
    if BuildVariables["OS"] not in ["Windows", "Linux"]:
        print("OS unsupported; you'll have to write your own build function to package on this OS.")
        return

    BuildVariables["CodeFiles"] = ["Core", "Interface", "SaveAndLoad", "Build.py", "SerpentNotes.py"]
    BuildVariables["AssetFiles"] = ["Assets"]

    BuildVariables["ExecutableZipName"] = BuildVariables["AppName"] + ".pyzw"
    BuildVariables["Interpreter"] = "python3"
    BuildVariables["Main"] = BuildVariables["AppName"] + ":StartApp"

    BuildVariables["CurrentWorkingDirectory"] = os.getcwd()

    #  Windows-Specific Build Variables
    if BuildVariables["OS"] == "Windows":
        BuildVariables["CommandPrompt"] = "python -m pip install -r \"" + BuildVariables["CurrentWorkingDirectory"] + "\\requirements.txt\" --target \"" + BuildVariables["CurrentWorkingDirectory"] + "\\" + BuildVariables["BuildFolder"] + "\""

    # Linux-Specific Build Variables
    if BuildVariables["OS"] == "Linux":
        BuildVariables["CommandPrompt"] = "pip3 install -r \"" + BuildVariables["CurrentWorkingDirectory"] + "/requirements.txt\" --target \"" + BuildVariables["CurrentWorkingDirectory"] + "/" + BuildVariables["BuildFolder"] + "\""
        BuildVariables["AssetFiles"].append("CreateGNOMEDesktopFile.py")

    # Copy Code to Build Folder
    CopyFilesToBuildFolder(BuildVariables["CodeFiles"])
    print("Code files copied to build folder.")

    # Create Executable Archive
    zipapp.create_archive(BuildVariables["BuildFolder"], BuildVariables["ExecutableZipName"], BuildVariables["Interpreter"], BuildVariables["Main"])
    print("Executable archive created.")

    # Delete Build Folder
    shutil.rmtree(BuildVariables["BuildFolder"])
    print("Build folder deleted.")

    # Copy Assets to Build Folder and Move Executable Zip
    CopyFilesToBuildFolder(BuildVariables["AssetFiles"])
    print("Assets copied to build folder.")
    shutil.move(BuildVariables["ExecutableZipName"], BuildVariables["BuildFolder"])
    print("Executable archive moved to build folder.")

    # Prompt to Install Dependencies
    ProceedPrompt = "\n---\nInstall dependencies to build folder (" + BuildVariables["BuildFolder"] + ") using a command prompt:\n\n    " + BuildVariables["CommandPrompt"] + "\n\nOnce all dependencies are installed, input \"PROCEED\" to continue with build or \"CANCEL\" to cancel and clean up build files:\n---\n"
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
    shutil.make_archive(BuildVariables["VersionedAppName"] + " - " + BuildVariables["OS"], "zip", BuildVariables["BuildFolder"])
    print("Build zipped.")

    # Clean Up
    CleanUp()


if __name__ == "__main__":
    Build()
