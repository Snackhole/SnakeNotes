from Core import Base64Converters

BackLocation = "Assets/SerpentNotes Back Icon.png"
ForwardLocation = "Assets/SerpentNotes Forward Icon.png"

BackString = Base64Converters.GetBase64StringFromFilePath(BackLocation)
ForwardString = Base64Converters.GetBase64StringFromFilePath(ForwardLocation)

with open("Assets/SerpentNotes Back Icon Base64.txt", "w") as WriteFile:
    WriteFile.write(BackString)

with open("Assets/SerpentNotes Forward Icon Base64.txt", "w") as WriteFile:
    WriteFile.write(ForwardString)
