import base64


def GetBase64StringFromBinary(Binary):
    return base64.b64encode(Binary).decode("ascii")


def GetBinaryFromBase64String(Base64String):
    return base64.decodebytes(Base64String.encode("ascii"))


def GetBase64StringFromFilePath(FilePath):
    with open(FilePath, "rb") as File:
        FileBinary = File.read()
    Base64String = GetBase64StringFromBinary(FileBinary)
    return Base64String


def WriteFileFromBase64String(Base64String, FilePath):
    with open(FilePath, "wb") as File:
        File.write(GetBinaryFromBase64String(Base64String))
