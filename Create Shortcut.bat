@echo off

set APPNAME=SnakeNotes

set SHORTCUTNAME="%APPNAME%.lnk"
set INTERPRETERPATH="%cd%\Python Interpreter - Windows\pythonw.exe"
set SCRIPTPATH="""%cd%\%APPNAME%.pyzw"""
set ICONPATH="%cd%\Assets\%APPNAME% Icon.ico"

set SCRIPT="%TEMP%\%RANDOM%-%RANDOM%-%RANDOM%-%RANDOM%.vbs"

echo Set oWS = WScript.CreateObject("WScript.Shell") >> %SCRIPT%
echo sLinkFile = %SHORTCUTNAME% >> %SCRIPT%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%
echo oLink.TargetPath = %INTERPRETERPATH% >> %SCRIPT%
echo oLink.Arguments = %SCRIPTPATH% >> %SCRIPT%
echo oLink.IconLocation = %ICONPATH% >> %SCRIPT%
echo oLink.Save >> %SCRIPT%

cscript /nologo %SCRIPT%
del %SCRIPT%