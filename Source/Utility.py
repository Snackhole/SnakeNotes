def GetSafeFileNameFromPageTitle(PageTitle):
    SafeFileName = PageTitle.replace("/", " - ")
    SafeFileName = SafeFileName.replace("\\", " - ")
    SafeFileName = SafeFileName.replace(":", " - ")
    SafeFileName = SafeFileName.replace("|", " - ")
    SafeFileName = "".join([Character for Character in SafeFileName if Character.isalpha() or Character.isdigit() or Character in (" ", ".", "_", "-")])
    return SafeFileName
