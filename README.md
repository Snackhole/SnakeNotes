# SerpentNotes
SerpentNotes is a searchable notes application with hierarchical pages and markdown formatting, written in Python 3.8 with PyQT5.

## Installation
Because SerpentNotes is written in Python and packaged as an executable zip, a Python 3 installation is required to run it.  It was written and tested in Python 3.8, though it may or may not run in other versions of Python 3.

### Windows
On Windows, Python 3.8 can be installed by downloading the installer from [python.org](https://www.python.org/).  Make sure to include the py launcher, associate files with Python, and add Python to the environment variables.

At this point, you should be able to download the .zip file of the latest Windows release from this repository, unzip it wherever you like, and double-click on SerpentNotes.pyzw to run the app.

A shortcut to SerpentNotes can be created on Windows by right-clicking on SerpentNotes.pyzw and selecting "Create shortcut". It is recommended you change the icon of the shortcut to the included .ico file in the Assets folder, and place the shortcut in "\AppData\Roaming\Microsoft\Windows\Start Menu\Programs" for convenience.  This will cause the shortcut to appear in the Start menu with the correct icon and whatever name you gave to the shortcut.

### Linux
On Linux, SerpentNotes has only been built and tested for Ubuntu 20.04.  It probably runs just fine on many other distros, but you're on your own as far as resolving any problems or differences.

It is generally assumed that you already have Python 3 installed as part of your distro.  If your distro has 3.8, you should be fine; otherwise, you may or may not need to install 3.8.  Either way, you will likely still need to resolve some dependencies before running the app.

First, install pip if you don't already have it:

    sudo apt install python3-pip

Then, install PyQT5 in both pip and APT:

    pip3 install pyqt5
    sudo apt install python3-pyqt5

Now, download the .zip file of the latest Linux release from this repository, and unzip it wherever you like.  To run the app, open a terminal in the app's directory and use the following command:

    python3 SerpentNotes.pyzw

However, for convenience, consider running `python3 CreateGNOMEDesktopFile.py`.  This will generate a .desktop file, which you should then copy to `usr/share/applications`  with `sudo cp SerpentNotes.desktop /usr/share/applications`.  Now SerpentNotes should show up along with your other apps in the GNOME desktop menus.

## Updates
Updating SerpentNotes is as simple as deleting all files wherever you installed it *except* .cfg files, and then extracting the contents of the latest release to the same folder.  Any shortcuts in place should resolve without issue to the updated version.

The .cfg files should be left as they store settings and contexts between uses of the app.

## Uninstallation
Uninstalling SerpentNotes is as simple as deleting the directory you extracted it to, along with any shortcuts you created.

If you need to uninstall Python 3.8 or, on Linux, PyQT5, consult their documentation.