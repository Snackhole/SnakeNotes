import json
import os

import mistune

from Core import Base64Converters


class Renderer(mistune.Renderer):
    def __init__(self, Notebook):
        super().__init__()
        self.Notebook = Notebook

    def link(self, Link, Title, Text):
        Link = mistune.escape_link(Link)
        if Link.startswith("[0,") and not self.Notebook.StringIsValidIndexPath(Link):
            return Text + " (LINKED PAGE NOT FOUND)"
        if Link == "[deleted]":
            return Text + " (LINKED PAGE DELETED)"
        if not Title:
            return "<a href=\"" + Link + "\">" + Text + "</a>"
        Title = mistune.escape(Title, quote=True)
        return "<a href=\"" + Link + "\" title=\"" + Title + "\">" + Text + "</a>"

    def strikethrough(self, Text):
        return "<s>" + Text + "</s>"

    def footnote_ref(self, Key, Index):
        Key = mistune.escape(Key)
        return "<sup class=\"footnote-ref\" id=\"fnref-" + Key + "\">" + Key + "</sup>"

    def footnote_item(self, Key, Text):
        Key = mistune.escape(Key)
        Text = "<p>" + Key + ". " + Text.rstrip()[3:]
        return "<li>" + Text + "</li>\n"

    def footnotes(self, Text):
        return "<div class=\"footnotes\">\n" + self.hrule() + "<ul style=\"list-style-type:none\">" + Text + "</ul>\n</div>\n"

    def table(self, Header, Body):
        return "<p><table border=\"1\" cellpadding=\"2\">\n<thead>" + Header + "</thead>\n<tbody>\n" + Body + "</tbody>\n</table>\n"

    def header(self, text, level, raw=None):
        return "<h" + str(level) + " style=\"color: seagreen\">" + text + "</h" + str(level) + ">\n"

    def image(self, Source, Title, AltText):
        if self.Notebook.HasImage(Source):
            Source = "data:image/" + os.path.splitext(Source)[1] + ";base64, " + self.Notebook.GetImage(Source)
            AltText = mistune.escape(AltText, quote=True)
            if Title is not None:
                Title = mistune.escape(Title, quote=True)
                HTML = "<img src=\"" + Source + "\" alt=\"" + AltText + "\" title=\"" + Title + "\""
            else:
                HTML = "<img src=\"" + Source + "\" alt=\"" + AltText + "\""
            if self.options.get("use_xhtml"):
                return HTML + " />"
            return HTML + ">"
        else:
            return "IMAGE NOT FOUND|" + Source + (("|" + AltText) if AltText != "" else "") + (("|" + Title) if Title is not None and Title != "" else "")


class HTMLExportRenderer(Renderer):
    def __init__(self, Notebook):
        super().__init__(Notebook)

    def link(self, Link, Title, Text):
        Link = mistune.escape_link(Link)
        ValidIndexPath = self.Notebook.StringIsValidIndexPath(Link)
        if Link.startswith("[0,") and not ValidIndexPath:
            return Text + " (LINKED PAGE NOT FOUND)"
        if Title:
            Title = mistune.escape(Title, quote=True)
        if ValidIndexPath:
            if not Title:
                return "<a href=\"\" onclick=\"return SelectPage(&quot;" + Link + "&quot;);\">" + Text + "</a>"
            return "<a href=\"\" onclick=\"return SelectPage(&quot;" + Link + "&quot;);\" title=\"" + Title + "\">" + Text + "</a>"
        else:
            if not Title:
                return "<a href=\"" + Link + "\" target=\"_blank\">" + Text + "</a>"
            return "<a href=\"" + Link + "\" title=\"" + Title + "\" target=\"_blank\">" + Text + "</a>"


class PDFExportRenderer(Renderer):
    def __init__(self, Notebook):
        super().__init__(Notebook)

    def link(self, Link, Title, Text):
        return Text


def ConstructMarkdownStringFromPage(Page, Notebook):
    HeaderString = Notebook.Header + "\n\n"
    HeaderString = HeaderString.replace("{PAGETITLE}", Page["Title"])
    HeaderString = HeaderString.replace("{SUBPAGELINKS}", ConstructSubPageLinks(Page))
    HeaderString = HeaderString.replace("{SUBPAGEOFLINK}", ConstructSubPageOfLink(Page, Notebook))
    HeaderString = HeaderString.replace("{LINKINGPAGES}", ConstructLinkingPagesLinks(Page, Notebook))
    FooterString = "\n\n" + Notebook.Footer
    FooterString = FooterString.replace("{PAGETITLE}", Page["Title"])
    FooterString = FooterString.replace("{SUBPAGELINKS}", ConstructSubPageLinks(Page))
    FooterString = FooterString.replace("{SUBPAGEOFLINK}", ConstructSubPageOfLink(Page, Notebook))
    FooterString = FooterString.replace("{LINKINGPAGES}", ConstructLinkingPagesLinks(Page, Notebook))
    MarkdownString = HeaderString + Page["Content"] + FooterString
    return MarkdownString


def ConstructSubPageLinks(Page):
    if len(Page["SubPages"]) < 1:
        LinksString = "No sub pages."
    else:
        LinksString = ""
        for SubPage in Page["SubPages"]:
            LinksString += "[" + SubPage["Title"] + "](" + json.dumps(SubPage["IndexPath"]) + ")  \n"
        LinksString = LinksString.rstrip()
    return LinksString


def ConstructSubPageOfLink(Page, Notebook):
    if Page is Notebook.RootPage:
        LinkString = "This is the root page."
    else:
        SuperPage = Notebook.GetSuperOfPageFromIndexPath(Page["IndexPath"])
        LinkString = "[" + SuperPage["Title"] + "](" + json.dumps(SuperPage["IndexPath"]) + ")"
    return LinkString


def ConstructLinkingPagesLinks(Page, Notebook):
    SearchResults = Notebook.GetSearchResults("](" + json.dumps(Page["IndexPath"]) + ")")
    if len(SearchResults["ResultsList"]) < 1:
        LinksString = "No linking pages."
    else:
        LinksString = ""
        for Result in SearchResults["ResultsList"]:
            LinksString += "[" + Result[0] + "](" + json.dumps(Result[1]) + ")  \n"
        LinksString = LinksString.rstrip()
    return LinksString


def ConstructHTMLExportString(Notebook, AssetPaths):
    with open(AssetPaths["TemplatePath"], "r") as TemplateFile:
        TemplateText = TemplateFile.read()
    TemplateTextSplit = TemplateText.split("[[SPLIT]]")
    HTMLExportString = TemplateTextSplit[0]
    HTMLExportString += Notebook.RootPage["Title"]
    HTMLExportString += TemplateTextSplit[1]
    HTMLExportString += Base64Converters.GetBase64StringFromFilePath(AssetPaths["BackButtonPath"])
    HTMLExportString += TemplateTextSplit[2]
    HTMLExportString += Base64Converters.GetBase64StringFromFilePath(AssetPaths["ForwardButtonPath"])
    HTMLExportString += TemplateTextSplit[3]
    HTMLExportString += Base64Converters.GetBase64StringFromFilePath(AssetPaths["ExpandButtonPath"])
    HTMLExportString += TemplateTextSplit[4]
    HTMLExportString += Base64Converters.GetBase64StringFromFilePath(AssetPaths["CollapseButtonPath"])
    HTMLExportString += TemplateTextSplit[5]
    HTMLExportString += GeneratePageListItemHTML(Notebook.RootPage, Root=True)
    HTMLExportString += TemplateTextSplit[6]
    HTMLExportString += GeneratePageDictionaryJavaScript(Notebook)
    HTMLExportString += TemplateTextSplit[7]
    return HTMLExportString


def GeneratePageListItemHTML(Page, Root=False):
    if len(Page["SubPages"]) > 0:
        ListItemString = "<li class=\"PageListCollapsibleItem\"><input type=\"checkbox\" id=\"" + str(Page["IndexPath"]) + "checkbox\"" + " class=\"PageListCollapsibleCheckbox\"" + (" checked=\"checked\"" if Root else "") + "><label for=\"" + str(Page["IndexPath"]) + "checkbox\"></label><span id=\"" + str(Page["IndexPath"]) + "link\" class=\"PageLink\" onclick=\"SelectPage(&quot;" + str(Page["IndexPath"]) + "&quot;);\" ondblclick=\"TogglePageExpansion(&quot;" + str(Page["IndexPath"]) + "&quot;);\">" + Page["Title"] + "</span><ul>"
        for SubPage in Page["SubPages"]:
            ListItemString += GeneratePageListItemHTML(SubPage)
        ListItemString += "</ul></li>"
    else:
        ListItemString = "<li><span id=\"" + str(Page["IndexPath"]) + "link\" class=\"PageLink\" onclick=\"SelectPage(&quot;" + str(Page["IndexPath"]) + "&quot;);\">" + Page["Title"] + "</span></li>"
    return ListItemString


def GeneratePageDictionaryJavaScript(Notebook):
    PageDictionaryJavaScript = {}
    HTMLExportParser = mistune.Markdown(renderer=HTMLExportRenderer(Notebook))
    GeneratePageDictionaryEntries(Notebook, Notebook.RootPage, PageDictionaryJavaScript, HTMLExportParser)
    PageDictionaryJavaScriptJSON = json.dumps(PageDictionaryJavaScript)
    return PageDictionaryJavaScriptJSON


def GeneratePageDictionaryEntries(Notebook, Page, PageDictionary, HTMLExportParser):
    MarkdownContent = Page["Content"]
    Title = Page["Title"]
    HTMLContent = HTMLExportParser(ConstructMarkdownStringFromPage(Page, Notebook))
    PageDictionary[str(Page["IndexPath"])] = [HTMLContent, MarkdownContent, Title]
    for SubPage in Page["SubPages"]:
        GeneratePageDictionaryEntries(Notebook, SubPage, PageDictionary, HTMLExportParser)


def ConstructPDFExportHTML(Page, Notebook):
    PDFExportParser = mistune.Markdown(renderer=PDFExportRenderer(Notebook))
    PDFExportHTML = PDFExportParser(ConstructMarkdownStringFromPage(Page, Notebook))
    return PDFExportHTML
