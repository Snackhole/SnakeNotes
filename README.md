# SerpentNotes
SerpentNotes is a searchable notes application with hierarchical pages and markdown formatting, written in Python 3.8 with PyQT5.

## Installation
Because SerpentNotes is written in 64-bit Python and packaged as an executable zip, a 64-bit Python 3 installation is required to run it.  It was written and tested in Python 3.8, though it may or may not run in other versions of Python 3.

### Windows
On Windows, Python 3.8 can be installed by downloading the installer from [python.org](https://www.python.org/).  Make sure to include the py launcher, associate files with Python, and add Python to the environment variables.  Make sure you're installing the 64-bit version.

At this point, you should be able to download the .zip file of the latest Windows release from this repository, unzip it wherever you like, and double-click on SerpentNotes.pyzw to run the app.

A shortcut to SerpentNotes can be created on Windows by right-clicking on SerpentNotes.pyzw and selecting "Create shortcut". It is recommended you change the icon of the shortcut to the included .ico file in the Assets folder, and place the shortcut in "\AppData\Roaming\Microsoft\Windows\Start Menu\Programs" for convenience.  This will cause the shortcut to appear in the Start menu with the correct icon and whatever name you gave to the shortcut.

### Linux
On Linux, SerpentNotes has only been built and tested for Ubuntu 20.04.  It probably runs just fine on many other distros, but you're on your own as far as resolving any problems or differences.

It is generally assumed that you already have 64-bit Python 3 installed as part of your distro.  If your distro has 3.8, you should be fine; otherwise, you may or may not need to install 3.8.

First, download the .zip file of the latest Linux release from this repository, and unzip it wherever you like (probably easiest somewhere in your Home).  To run the app, open a terminal in the app's directory and use the following command:

```
python3 SerpentNotes.pyzw
```

However, for convenience, consider running `python3 CreateGNOMEDesktopFile.py` (also in the app's directory; it will not work properly with any other working directory).  This will generate a .desktop file, which you should then copy to `usr/share/applications`  with `sudo cp SerpentNotes.desktop /usr/share/applications`.  Now SerpentNotes should show up along with your other apps in the GNOME desktop menus.

If SerpentNotes does not run at first, you probably need to resolve some dependencies.  First, try `sudo apt install libxcb-xinerama0`.  If that doesn't resolve the issue, try installing PyQT5 with `sudo apt install python3-pyqt5`; if this does resolve the issue, you might even be able to (partially) uninstall it with `sudo apt remove python3-pyqt5` and still run SerpentNotes, as long as you don't autoremove the additional packages that were installed with it.  If installing PyQT5 through APT doesn't work, try installing it through pip; if you don't have pip already, use `sudo apt install python3-pip`, then run `pip3 install pyqt5`.  Other issues have not yet been encountered and will require you to do some research and troubleshooting to resolve on your system.

## Keybindings
Note that, after the first startup, there will be a `Keybindings.cfg` file in the installation directory.  This file can be used to alter the keybindings for various actions in the app.  This is not intended as a feature for regular users, but rather as a workaround in case of conflicts with the user's operating system, so it is not documented thoroughly and there is no user interface provided.  If you want to alter your keybindings, you'll need to know how to format the shortcut string properly in the config file, which you can work out by looking at the existing shortcut strings.  If you format the shortcut improperly, the app will still run but the action will have no keybinding assigned.

## Updates
Updating SerpentNotes is as simple as deleting all files wherever you installed it *except* .cfg files, and then extracting the contents of the latest release to the same folder.  Any shortcuts in place should resolve without issue to the updated version.

The .cfg files should be left in place as they store settings and contexts between uses of the app.

## Uninstallation
Uninstalling SerpentNotes itself only requires deleting the directory you extracted it to, along with any shortcuts you created.

If you need to uninstall Python 3.8 or, on Linux, PyQT5, consult their documentation.