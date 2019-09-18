def ConvertFromZimWikiSyntax(TextToConvert):
    TextToConvert = TextToConvert.replace("//", "*")
    TextToConvert = TextToConvert.replace("__", "")
    TextToConvert = TextToConvert.replace("'''", "```")
    TextToConvert = TextToConvert.replace("''", "`")
    TextToConvert = TextToConvert.replace("{{", "![](")
    TextToConvert = TextToConvert.replace("}}", ")")
    TextToConvert = TextToConvert.replace("[[", "")
    TextToConvert = TextToConvert.replace("]]", "")
    TextToConvert = TextToConvert.replace("====== ", "# ")
    TextToConvert = TextToConvert.replace("===== ", "## ")
    TextToConvert = TextToConvert.replace("==== ", "### ")
    TextToConvert = TextToConvert.replace("=== ", "#### ")
    TextToConvert = TextToConvert.replace("== ", "##### ")
    TextToConvert = TextToConvert.replace("= ", "###### ")
    TextToConvert = TextToConvert.replace(" ======", "")
    TextToConvert = TextToConvert.replace(" =====", "")
    TextToConvert = TextToConvert.replace(" ====", "")
    TextToConvert = TextToConvert.replace(" ===", "")
    TextToConvert = TextToConvert.replace(" ==", "")
    TextToConvert = TextToConvert.replace(" =", "")
    Lines = TextToConvert.splitlines()
    HorizontalRuleCharacterSet = set("-")
    SkipLines = False
    for Index in range(len(Lines)):
        if Lines[Index] == "```":
            SkipLines = not SkipLines
        if not SkipLines:
            LineCharacterSet = set(Lines[Index])
            if LineCharacterSet.issubset(HorizontalRuleCharacterSet) and len(Lines[Index]) > 4:
                Lines[Index] = "***"
    SkipLines = False
    for Index in range(len(Lines)):
        NextIndex = Index + 1
        if NextIndex < len(Lines):
            NextLine = Lines[NextIndex]
            if Lines[Index] == "```":
                SkipLines = not SkipLines
            if NextLine != "" and Lines[Index] != "" and Lines[Index] != "***" and not Lines[Index].startswith(("* ", "#", "```")) and not Lines[Index].split(".")[0].isnumeric() and not SkipLines:
                Lines[Index] += "  "
    TextToConvert = "\n".join(Lines).rstrip().lstrip()
    return TextToConvert


def ConvertFromZimWikiPage(TextToConvert):
    Lines = TextToConvert.splitlines()
    for Line in Lines[:5]:
        if Line.startswith(("Content-Type: ", "Wiki-Format: ", "Creation-Date: ", "====== ")) or Line == "":
            Lines.remove(Line)
    TextToConvert = "\n".join(Lines).rstrip().lstrip()
    TextToConvert = ConvertFromZimWikiSyntax(TextToConvert)
    return TextToConvert
