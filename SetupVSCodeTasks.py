import json
import os
import platform
import sys

import Build

# Establish Working Directory and OS
WorkingDir = os.getcwd()
OS = platform.system()

# Generate Task Commands
if OS == "Windows":
    PythonExecutable = os.path.join(WorkingDir, "venv", "Scripts", "python.exe")
elif OS == "Linux":
    PythonExecutable = f"source {os.path.join(WorkingDir, "venv", "bin", "activate")}; {os.path.join(WorkingDir, "venv", "bin", "python3")}"
else:
    print("Not on Windows or Linux.  Set up tasks manually.")
    sys.exit()

AppPath = os.path.join(WorkingDir, f"{Build.BuildVariables["AppName"]}.py")
BuildPath = os.path.join(WorkingDir, "Build.py")

AppCommand = f"{PythonExecutable} {AppPath}"
BuildCommand = f"{PythonExecutable} {BuildPath}"

# Create Tasks Dictionary
TasksDict = {}

TasksDict["version"] = "2.0.0"

TasksDict["tasks"] = []
TasksDict["tasks"].append({})
TasksDict["tasks"].append({})
AppTaskDict = TasksDict["tasks"][0]
BuildTaskDict = TasksDict["tasks"][1]

AppTaskDict["label"] = f"{Build.BuildVariables["AppName"]}.py"
AppTaskDict["type"] = "shell"
AppTaskDict["command"] = AppCommand
AppTaskDict["presentation"] = {"reveal": "silent", "showReuseMessage": False}

BuildTaskDict["label"] = "Build.py"
BuildTaskDict["type"] = "shell"
BuildTaskDict["command"] = BuildCommand
BuildTaskDict["presentation"] = {"showReuseMessage": False}

# Serialize Tasks Dictionary
TasksDictString = json.dumps(TasksDict, indent=4)

# Create .vscode Dir
CodeDir = os.path.join(WorkingDir, ".vscode")

if not os.path.isdir(CodeDir):
    os.mkdir(CodeDir)

# Write tasks.json File
TasksPath = os.path.join(CodeDir, "tasks.json")

with open(TasksPath, "w") as TasksFile:
    TasksFile.write(TasksDictString)
