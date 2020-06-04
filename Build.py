# import os
# import shutil
#
# from PyInstaller import __main__ as PyInstall
#
# # Built with Python 3.6.3 and dependencies in requirements.txt
#
# def Build():
#     # Version String
#     Version = "29"
#
#     # Build Variables
#     ExecutableScript = "Source/SerpentNotes " + Version + ".pyw"
#     ExecutableZip = "Executables/Final/" + ExecutableScript[7:-4] + ".zip"
#     InstallerScript = "SerpentNotes " + Version + " Installer.pyw"
#
#     # Build Executable
#     PyInstall.run(pyi_args=[ExecutableScript,
#                             "--clean",
#                             "--windowed",
#                             "--name=SerpentNotes",
#                             "--icon=Source/Assets/.SerpentNotes Icon.ico",
#                             "--add-data=Source/Assets/.SerpentNotes Icon.ico;./Assets/",
#                             "--add-data=Source/Assets/SerpentNotes Bold Icon.png;./Assets/",
#                             "--add-data=Source/Assets/SerpentNotes Back Icon.png;./Assets/",
#                             "--add-data=Source/Assets/SerpentNotes Forward Icon.png;./Assets/",
#                             "--add-data=Source/Assets/SerpentNotes Bullet List Icon.png;./Assets/",
#                             "--add-data=Source/Assets/SerpentNotes Delete Page Icon.png;./Assets/",
#                             "--add-data=Source/Assets/SerpentNotes Demote Page Icon.png;./Assets/",
#                             "--add-data=Source/Assets/SerpentNotes Icon.png;./Assets/",
#                             "--add-data=Source/Assets/SerpentNotes Insert External Link Icon.png;./Assets/",
#                             "--add-data=Source/Assets/SerpentNotes Insert Link(s) Icon.png;./Assets/",
#                             "--add-data=Source/Assets/SerpentNotes Insert Table Icon.png;./Assets/",
#                             "--add-data=Source/Assets/SerpentNotes Insert Image Icon.png;./Assets/",
#                             "--add-data=Source/Assets/SerpentNotes Italics Icon.png;./Assets/",
#                             "--add-data=Source/Assets/SerpentNotes Move Page Down Icon.png;./Assets/",
#                             "--add-data=Source/Assets/SerpentNotes Move Page Up Icon.png;./Assets/",
#                             "--add-data=Source/Assets/SerpentNotes New Page Icon.png;./Assets/",
#                             "--add-data=Source/Assets/SerpentNotes Number List Icon.png;./Assets/",
#                             "--add-data=Source/Assets/SerpentNotes Promote Page Icon.png;./Assets/",
#                             "--add-data=Source/Assets/SerpentNotes Quote Icon.png;./Assets/",
#                             "--add-data=Source/Assets/SerpentNotes Rename Page Icon.png;./Assets/",
#                             "--add-data=Source/Assets/SerpentNotes Strikethrough Icon.png;./Assets/",
#                             "--add-data=Source/Assets/SerpentNotes Toggle Read Mode Icon.png;./Assets/",
#                             "--add-data=Source/Assets/SerpentNotes Zoom In Icon.png;./Assets/",
#                             "--add-data=Source/Assets/SerpentNotes Zoom Out Icon.png;./Assets/",
#                             "--add-data=Source/Assets/SerpentNotes Favorites Icon.png;./Assets/",
#                             "--add-data=Source/Assets/SerpentNotes Search Icon.png;./Assets/",
#                             "--add-data=Source/Assets/SerpentNotes Toggle Search Icon.png;./Assets/",
#                             "--workpath=./Executables/Build",
#                             "--distpath=./Executables/Final"])
#
#     # Zip Executable
#     shutil.make_archive(ExecutableZip[:-4], "zip", "Executables/Final/SerpentNotes")
#
#     # Build Installer
#     PyInstall.run(pyi_args=[InstallerScript,
#                             "--clean",
#                             "--windowed",
#                             "--onefile",
#                             "--name=SerpentNotes " + Version + " Installer",
#                             "--icon=Source/Assets/.SerpentNotes Icon.ico",
#                             "--add-data=Source/Assets/SerpentNotes Icon.png;./Source/Assets/",
#                             "--add-binary=./" + ExecutableZip + ";./Executables/Final",
#                             "--workpath=./Installer/Build",
#                             "--distpath=./Installer/Final"])
#
#     # Move Files to Versions Folder
#     VersionsSubFolder = os.path.dirname("Versions/SerpentNotes " + Version + "/")
#     if not os.path.exists(VersionsSubFolder):
#         os.makedirs(VersionsSubFolder)
#     shutil.copy(ExecutableZip, VersionsSubFolder)
#     shutil.copy("Installer/Final/SerpentNotes " + Version + " Installer.exe", VersionsSubFolder)
#
#     # Delete Build Files
#     for Folder in ["Executables/", "Installer/"]:
#         shutil.rmtree(Folder, True)
#     for File in os.listdir("."):
#         if File.endswith(".spec"):
#             os.unlink(File)
#
#     # Mark Source Files as Built
#     os.rename(ExecutableScript, "Source/BUILT SerpentNotes " + Version + ".pyw")
#     os.rename(InstallerScript, "BUILT " + InstallerScript)
#
#
# if __name__ == "__main__":
#     Build()
