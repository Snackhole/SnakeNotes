import json
import os

import mistune


class Renderer(mistune.Renderer):
    def __init__(self, Notebook):
        super().__init__()
        self.Notebook = Notebook

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
        if self.Notebook.StringIsValidIndexPath(Link):
            Link = mistune.escape_link(Link)
            if not Title:
                return "<a href=\"\" onclick=\"return SelectPage(&quot;" + Link + "&quot;);\">" + Text + "</a>"
            Title = mistune.escape(Title, quote=True)
            return "<a href=\"\" onclick=\"return SelectPage(&quot;" + Link + "&quot;);\" title=\"" + Title + "\">" + Text + "</a>"
        else:
            return super().link(Link, Title, Text)


def ConstructMarkdownStringFromPage(Page, Notebook):
    HeaderString = Notebook.Header + "\n\n"
    HeaderString = HeaderString.replace("{PAGETITLE}", Page["Title"])
    HeaderString = HeaderString.replace("{SUBPAGELINKS}", ConstructSubPageLinks(Page))
    HeaderString = HeaderString.replace("{SUBPAGEOFLINK}", ConstructSubPageOfLink(Page, Notebook))
    FooterString = "\n\n" + Notebook.Footer
    FooterString = FooterString.replace("{PAGETITLE}", Page["Title"])
    FooterString = FooterString.replace("{SUBPAGELINKS}", ConstructSubPageLinks(Page))
    FooterString = FooterString.replace("{SUBPAGEOFLINK}", ConstructSubPageOfLink(Page, Notebook))
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


def ConstructHTMLExportString(Notebook):
    HTMLExportString = "<!DOCTYPE html><html lang=\"en\" dir=\"ltr\"><head><meta charset=\"utf-8\"><title>"
    HTMLExportString += Notebook.RootPage["Title"]
    HTMLExportString += "</title><style media=\"screen\">html, body {height: 99%;}#PageList {height: 100%;width: 20%;box-sizing: border-box;float:left;overflow: auto;white-space: nowrap;background-color: lightgray;}#PageList li {list-style: none;}#PageList span {cursor: pointer;}#PageList span.PageListCurrentPage {background-color: white;}#PageDisplay {height: 100%;width: 60%;padding: 20px;box-sizing: border-box;float: left;overflow: auto;}#PageDisplay a:visited {color: blue;}#SearchInterface {height: 100%;width: 20%;padding: 20px;box-sizing: border-box;float: left;overflow: auto;white-space: nowrap;background-color: lightgray;}#SearchInterface input[type=text] {width: 100%;}#SearchResultsList {list-style: none;}#SearchResultsList span {cursor: pointer;}ul.PageListCollapsibleTree li.PageListCollapsibleItem input[type=checkbox] {display: none;}li.PageListCollapsibleItem label::before {content: \" +\";cursor: pointer;}li.PageListCollapsibleItem input:checked ~ label::before {content: \" -\";cursor: pointer;}ul.PageListCollapsibleTree li.PageListCollapsibleItem ul {display: none;max-height: 0px;}ul.PageListCollapsibleTree li.PageListCollapsibleItem input:checked ~ ul {display: block;max-height: 999px;}</style></head><body><div id=\"PageList\"><ul class=\"PageListCollapsibleTree\">"
    HTMLExportString += GeneratePageListItemHTML(Notebook.RootPage, Root=True)
    HTMLExportString += "</ul></div><div id=\"PageDisplay\"></div><div id=\"SearchInterface\"><input type=\"text\" id=\"SearchTextInput\" name=\"Search\" placeholder=\"Search\" value=\"\"><br><button type=\"button\" name=\"button\" onclick=\"SearchNotebook();\">Search Notebook</button><input type=\"checkbox\" id=\"MatchCaseCheckbox\" value=\"\"><label for=\"MatchCaseCheckbox\">Match Case</label><br><br><ul id=\"SearchResultsList\"></ul></div></body><script type=\"text/javascript\">document.getElementById(\"SearchTextInput\").addEventListener(\"keypress\", function(event) {if (event.key === \"Enter\") {event.preventDefault();SearchNotebook();}});var Pages = "
    HTMLExportString += GeneratePageDictionaryJavaScript(Notebook)
    HTMLExportString += ";SelectPage(\"[0]\");function SelectPage(IndexPath) {var PageLinks = document.getElementsByClassName(\"pagelink\");for (var i = 0; i < PageLinks.length; i++) {var PageLinkClassList = PageLinks[i].classList;if (PageLinkClassList.contains(\"PageListCurrentPage\")) {PageLinkClassList.remove(\"PageListCurrentPage\");}}ExpandParentPages(IndexPath);var SelectedPage = document.getElementById(IndexPath + \"link\");SelectedPage.classList.add(\"PageListCurrentPage\");document.getElementById(\"PageDisplay\").innerHTML = Pages[IndexPath][0];return false;}function ExpandParentPages(IndexPath) {var IndexPathArray = eval(IndexPath);for (var i = IndexPathArray.length - 1; i > 0; i--) {var IndexPathArraySlice = IndexPathArray.slice(0, i);var CheckboxID = \"[\" + IndexPathArraySlice.toString() + \"]\";CheckboxID = CheckboxID.replace(\",\", \", \");CheckboxID = CheckboxID + \"checkbox\";var Checkbox = document.getElementById(CheckboxID);Checkbox.checked = true;}}function SearchNotebook() {var SearchText = document.getElementById(\"SearchTextInput\").value;var SearchResultsList = document.getElementById(\"SearchResultsList\");var SearchResultsHTMLString = \"\";if (SearchText === \"\") {SearchResultsList.innerHTML = SearchResultsHTMLString;} else {var MatchCase = document.getElementById(\"MatchCaseCheckbox\").checked;if (!MatchCase) {SearchText = SearchText.toLowerCase();}var SearchResultsArray = [];for (IndexPath in Pages) {var PageContent = Pages[IndexPath][1];var PageTitle = Pages[IndexPath][2];var ExactTitleMatch = (MatchCase ? PageTitle : PageTitle.toLowerCase()) === SearchText;var TitleHits = (MatchCase ? PageTitle : PageTitle.toLowerCase()).split(SearchText).length - 1;var ContentHits = (MatchCase ? PageContent : PageContent.toLowerCase()).split(SearchText).length - 1;if (ExactTitleMatch || TitleHits > 0 || ContentHits > 0) {SearchResultsArray.push({\"ExactTitleMatch\": ExactTitleMatch, \"TitleHits\": TitleHits, \"ContentHits\": ContentHits, \"IndexPath\": IndexPath, \"PageTitle\": PageTitle})}}SearchResultsArray.sort(function (a, b) {var Result = 0;var MatchCriteria = [\"ExactTitleMatch\", \"TitleHits\", \"ContentHits\"];for (MatchCriterion of MatchCriteria) {Result = a[MatchCriterion] < b[MatchCriterion] ? 1 : a[MatchCriterion] > b[MatchCriterion] ? -1 : 0;if (Result !== 0) {return Result;}}return Result;});for (Result of SearchResultsArray) {SearchResultsHTMLString += \"<li><span onclick=\\\"SelectPage(&quot;\" + Result[\"IndexPath\"] + \"&quot;);\\\">\" + Result[\"PageTitle\"] + \"</span></li>\";}SearchResultsList.innerHTML = SearchResultsHTMLString;}}</script></html>"
    return HTMLExportString


def GeneratePageListItemHTML(Page, Root=False):
    if len(Page["SubPages"]) > 0:
        ListItemString = "<li class=\"PageListCollapsibleItem\"><span id=\"" + str(Page["IndexPath"]) + "link\" class=\"pagelink\" onclick=\"SelectPage(&quot;" + str(Page["IndexPath"]) + "&quot;);\">" + Page[
            "Title"] + "</span><input type=\"checkbox\" id=\"" + str(Page["IndexPath"]) + "checkbox\"" + (" checked=\"checked\"" if Root else "") + "><label for=\"" + str(Page["IndexPath"]) + "checkbox\"></label><ul>"
        for SubPage in Page["SubPages"]:
            ListItemString += GeneratePageListItemHTML(SubPage)
        ListItemString += "</ul></li>"
    else:
        ListItemString = "<li><span id=\"" + str(Page["IndexPath"]) + "link\" class=\"pagelink\" onclick=\"SelectPage(&quot;" + str(Page["IndexPath"]) + "&quot;);\">" + Page["Title"] + "</span></li>"
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
