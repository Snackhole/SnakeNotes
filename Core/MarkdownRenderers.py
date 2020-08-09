import json
import os

import mistune


class Renderer(mistune.Renderer):
    def __init__(self, Notebook):
        super().__init__()
        self.Notebook = Notebook

    def link(self, Link, Title, Text):
        Link = mistune.escape_link(Link)
        if Link.startswith("[0,") and not self.Notebook.StringIsValidIndexPath(Link):
            return Text + " (LINKED PAGE NOT FOUND)"
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
    HTMLExportString += "</title><style media=\"screen\">html, body {height: 100%; width: 100%;padding: 0px; margin: 0px;}#PageListContainer {height: 100%;width: 20%;box-sizing: border-box;float: left;background-color: lightgray;}#PageListHeader {text-align: center;box-sizing: border-box;height: 32px;background-color: darkgray;}#PageList {height: calc(100% - 32px);box-sizing: border-box;overflow: auto;white-space: nowrap;}#PageList li {list-style: none;}#PageList span {cursor: pointer;-moz-user-select: none;-webkit-user-select: none;-khtml-user-select:none;-ms-user-select:none;}#PageList span.PageListCurrentPage {background-color: white;}img.ForwardBack {cursor: pointer;}img.ForwardBackDisabled {filter: grayscale(100%);cursor: default;}#PageDisplay {height: 100%;width: 60%;padding: 20px;box-sizing: border-box;float: left;overflow: auto;}#PageDisplay a:visited {color: blue;}#SearchInterfaceContainer {height: 100%;width: 20%;box-sizing: border-box;float: left;background-color: lightgray;}#SearchInterfaceHeader {text-align: center;box-sizing: border-box;height: 44px;background-color: darkgray}#SearchInterfaceHeader input[type=text] {width: 90%;}#SearchInterface {height: calc(100% - 44px);box-sizing: border-box;overflow: auto;white-space: nowrap;}#SearchResultsList {list-style: none;}#SearchResultsList span {cursor: pointer;-moz-user-select: none;-webkit-user-select: none;-khtml-user-select:none;-ms-user-select:none;}ul.PageListCollapsibleTree li.PageListCollapsibleItem input[type=checkbox] {display: none;}li.PageListCollapsibleItem {position: relative;}li.PageListCollapsibleItem label::before {content: \">\";cursor: pointer;position: absolute; left: -3ch;color: seagreen;}li.PageListCollapsibleItem input:checked ~ label::before {transform: rotate(90deg);}ul.PageListCollapsibleTree li.PageListCollapsibleItem ul {display: none;max-height: 0em;}ul.PageListCollapsibleTree li.PageListCollapsibleItem input:checked ~ ul {display: block;max-height: 1000000000em;}#JavaScriptBlocked {color: white;background-color: darkred;text-align: center;}</style></head><body><div id=\"JavaScriptBlocked\"><h1>JavaScript has been blocked!  This notebook will not function correctly.</h1></div><div id=\"PageListContainer\"><div id=\"PageListHeader\"><img id=\"BackButton\" class=\"ForwardBack ForwardBackDisabled\" onclick=\"Back();\" src=\"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAACXBIWXMAAAsTAAALEwEAmpwYAAALXGlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4gPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iQWRvYmUgWE1QIENvcmUgNS42LWMxNDUgNzkuMTYzNDk5LCAyMDE4LzA4LzEzLTE2OjQwOjIyICAgICAgICAiPiA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPiA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtbG5zOmRjPSJodHRwOi8vcHVybC5vcmcvZGMvZWxlbWVudHMvMS4xLyIgeG1sbnM6eG1wTU09Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iIHhtbG5zOnN0RXZ0PSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VFdmVudCMiIHhtbG5zOnN0UmVmPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VSZWYjIiB4bWxuczpwaG90b3Nob3A9Imh0dHA6Ly9ucy5hZG9iZS5jb20vcGhvdG9zaG9wLzEuMC8iIHhtbG5zOnRpZmY9Imh0dHA6Ly9ucy5hZG9iZS5jb20vdGlmZi8xLjAvIiB4bWxuczpleGlmPSJodHRwOi8vbnMuYWRvYmUuY29tL2V4aWYvMS4wLyIgeG1wOkNyZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgQ0MgMjAxOSAoV2luZG93cykiIHhtcDpDcmVhdGVEYXRlPSIyMDE4LTExLTI5VDExOjM3OjMzLTA2OjAwIiB4bXA6TWV0YWRhdGFEYXRlPSIyMDE5LTEwLTA0VDE2OjM4OjQyLTA1OjAwIiB4bXA6TW9kaWZ5RGF0ZT0iMjAxOS0xMC0wNFQxNjozODo0Mi0wNTowMCIgZGM6Zm9ybWF0PSJpbWFnZS9wbmciIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6NjYwNDM2ZmQtNjI0OS1jZTQ2LTk5MDItNzBhZjcwN2ViNzA4IiB4bXBNTTpEb2N1bWVudElEPSJhZG9iZTpkb2NpZDpwaG90b3Nob3A6MjMxYjQzNDAtNGVjZi0yYTRjLThkYzEtYTRkNjFkOWM4MGI0IiB4bXBNTTpPcmlnaW5hbERvY3VtZW50SUQ9InhtcC5kaWQ6NzM4ODFlNjMtMThlYy02NzQ0LWIyMDktMGFjZTExYWFkZmI1IiBwaG90b3Nob3A6Q29sb3JNb2RlPSIzIiB0aWZmOk9yaWVudGF0aW9uPSIxIiB0aWZmOlhSZXNvbHV0aW9uPSI3MjAwMDAvMTAwMDAiIHRpZmY6WVJlc29sdXRpb249IjcyMDAwMC8xMDAwMCIgdGlmZjpSZXNvbHV0aW9uVW5pdD0iMiIgZXhpZjpDb2xvclNwYWNlPSI2NTUzNSIgZXhpZjpQaXhlbFhEaW1lbnNpb249IjMyIiBleGlmOlBpeGVsWURpbWVuc2lvbj0iMzIiPiA8eG1wTU06SGlzdG9yeT4gPHJkZjpTZXE+IDxyZGY6bGkgc3RFdnQ6YWN0aW9uPSJjcmVhdGVkIiBzdEV2dDppbnN0YW5jZUlEPSJ4bXAuaWlkOjczODgxZTYzLTE4ZWMtNjc0NC1iMjA5LTBhY2UxMWFhZGZiNSIgc3RFdnQ6d2hlbj0iMjAxOC0xMS0yOVQxMTozNzozMy0wNjowMCIgc3RFdnQ6c29mdHdhcmVBZ2VudD0iQWRvYmUgUGhvdG9zaG9wIENDIDIwMTkgKFdpbmRvd3MpIi8+IDxyZGY6bGkgc3RFdnQ6YWN0aW9uPSJzYXZlZCIgc3RFdnQ6aW5zdGFuY2VJRD0ieG1wLmlpZDo2MTk3ZjRkZi1iMTdiLWM1NDYtOWI5ZS0yMTc0MjY5ZWZjZmYiIHN0RXZ0OndoZW49IjIwMTgtMTEtMjlUMTE6Mzk6NTEtMDY6MDAiIHN0RXZ0OnNvZnR3YXJlQWdlbnQ9IkFkb2JlIFBob3Rvc2hvcCBDQyAyMDE5IChXaW5kb3dzKSIgc3RFdnQ6Y2hhbmdlZD0iLyIvPiA8cmRmOmxpIHN0RXZ0OmFjdGlvbj0ic2F2ZWQiIHN0RXZ0Omluc3RhbmNlSUQ9InhtcC5paWQ6MTliYmVhZmQtNzRmZC1iYTRiLTlmMGMtNjUxZWU1NWQ3Y2IzIiBzdEV2dDp3aGVuPSIyMDE5LTEwLTA0VDE2OjM4OjQyLTA1OjAwIiBzdEV2dDpzb2Z0d2FyZUFnZW50PSJBZG9iZSBQaG90b3Nob3AgQ0MgMjAxOSAoV2luZG93cykiIHN0RXZ0OmNoYW5nZWQ9Ii8iLz4gPHJkZjpsaSBzdEV2dDphY3Rpb249ImNvbnZlcnRlZCIgc3RFdnQ6cGFyYW1ldGVycz0iZnJvbSBhcHBsaWNhdGlvbi92bmQuYWRvYmUucGhvdG9zaG9wIHRvIGltYWdlL3BuZyIvPiA8cmRmOmxpIHN0RXZ0OmFjdGlvbj0iZGVyaXZlZCIgc3RFdnQ6cGFyYW1ldGVycz0iY29udmVydGVkIGZyb20gYXBwbGljYXRpb24vdm5kLmFkb2JlLnBob3Rvc2hvcCB0byBpbWFnZS9wbmciLz4gPHJkZjpsaSBzdEV2dDphY3Rpb249InNhdmVkIiBzdEV2dDppbnN0YW5jZUlEPSJ4bXAuaWlkOjY2MDQzNmZkLTYyNDktY2U0Ni05OTAyLTcwYWY3MDdlYjcwOCIgc3RFdnQ6d2hlbj0iMjAxOS0xMC0wNFQxNjozODo0Mi0wNTowMCIgc3RFdnQ6c29mdHdhcmVBZ2VudD0iQWRvYmUgUGhvdG9zaG9wIENDIDIwMTkgKFdpbmRvd3MpIiBzdEV2dDpjaGFuZ2VkPSIvIi8+IDwvcmRmOlNlcT4gPC94bXBNTTpIaXN0b3J5PiA8eG1wTU06RGVyaXZlZEZyb20gc3RSZWY6aW5zdGFuY2VJRD0ieG1wLmlpZDoxOWJiZWFmZC03NGZkLWJhNGItOWYwYy02NTFlZTU1ZDdjYjMiIHN0UmVmOmRvY3VtZW50SUQ9ImFkb2JlOmRvY2lkOnBob3Rvc2hvcDphZWJmNGFhYy1jYTMyLWVmNGYtYjhmOC1jN2FhMzI3YzEzZDkiIHN0UmVmOm9yaWdpbmFsRG9jdW1lbnRJRD0ieG1wLmRpZDo3Mzg4MWU2My0xOGVjLTY3NDQtYjIwOS0wYWNlMTFhYWRmYjUiLz4gPHBob3Rvc2hvcDpEb2N1bWVudEFuY2VzdG9ycz4gPHJkZjpCYWc+IDxyZGY6bGk+YWRvYmU6ZG9jaWQ6cGhvdG9zaG9wOmFlYmY0YWFjLWNhMzItZWY0Zi1iOGY4LWM3YWEzMjdjMTNkOTwvcmRmOmxpPiA8cmRmOmxpPnhtcC5kaWQ6NzM4ODFlNjMtMThlYy02NzQ0LWIyMDktMGFjZTExYWFkZmI1PC9yZGY6bGk+IDwvcmRmOkJhZz4gPC9waG90b3Nob3A6RG9jdW1lbnRBbmNlc3RvcnM+IDwvcmRmOkRlc2NyaXB0aW9uPiA8L3JkZjpSREY+IDwveDp4bXBtZXRhPiA8P3hwYWNrZXQgZW5kPSJyIj8+rGxXigAAAMBJREFUWIXtl80NgzAMRp+rDFZ1IJgFBqnUBRCbuYdEpfymlZz4EktcyOG9KP5iEFXFs26u9CbQBICQWd9GRIoKSN8t5GHU73c6jNZs4OQIVvDHvQj4VKAmfCdQG74VqA6HpQl/hZsPDtE0jS7h02zNBWKyQhYOZY4kbcr9JmwCAWIzeDQhxBRALobTXHYWSN8JpIFzvVuxfj498IeEaa2a0ENilwJ5PatKHMawpoRkfkzqfpIdlDlwW+43YRNoAm+V6lRvEcgJkAAAAABJRU5ErkJggg==\" alt=\"Back\"><img id=\"ForwardButton\" class=\"ForwardBack ForwardBackDisabled\" onclick=\"Forward();\" src=\"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAACXBIWXMAAAsTAAALEwEAmpwYAAALXGlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4gPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iQWRvYmUgWE1QIENvcmUgNS42LWMxNDUgNzkuMTYzNDk5LCAyMDE4LzA4LzEzLTE2OjQwOjIyICAgICAgICAiPiA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPiA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtbG5zOmRjPSJodHRwOi8vcHVybC5vcmcvZGMvZWxlbWVudHMvMS4xLyIgeG1sbnM6eG1wTU09Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iIHhtbG5zOnN0RXZ0PSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VFdmVudCMiIHhtbG5zOnN0UmVmPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VSZWYjIiB4bWxuczpwaG90b3Nob3A9Imh0dHA6Ly9ucy5hZG9iZS5jb20vcGhvdG9zaG9wLzEuMC8iIHhtbG5zOnRpZmY9Imh0dHA6Ly9ucy5hZG9iZS5jb20vdGlmZi8xLjAvIiB4bWxuczpleGlmPSJodHRwOi8vbnMuYWRvYmUuY29tL2V4aWYvMS4wLyIgeG1wOkNyZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgQ0MgMjAxOSAoV2luZG93cykiIHhtcDpDcmVhdGVEYXRlPSIyMDE4LTExLTI5VDExOjM3OjMzLTA2OjAwIiB4bXA6TWV0YWRhdGFEYXRlPSIyMDE5LTEwLTA0VDE2OjM4OjU1LTA1OjAwIiB4bXA6TW9kaWZ5RGF0ZT0iMjAxOS0xMC0wNFQxNjozODo1NS0wNTowMCIgZGM6Zm9ybWF0PSJpbWFnZS9wbmciIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6NzNkYTlkYzEtODhkMS1iMTQwLThjYjUtZmE1NzkyNWNiNzljIiB4bXBNTTpEb2N1bWVudElEPSJhZG9iZTpkb2NpZDpwaG90b3Nob3A6ZjViMTNhZDYtOWNiMi00ZjQzLThiMjktNTQ5NTNiNTNiOGUzIiB4bXBNTTpPcmlnaW5hbERvY3VtZW50SUQ9InhtcC5kaWQ6NzM4ODFlNjMtMThlYy02NzQ0LWIyMDktMGFjZTExYWFkZmI1IiBwaG90b3Nob3A6Q29sb3JNb2RlPSIzIiB0aWZmOk9yaWVudGF0aW9uPSIxIiB0aWZmOlhSZXNvbHV0aW9uPSI3MjAwMDAvMTAwMDAiIHRpZmY6WVJlc29sdXRpb249IjcyMDAwMC8xMDAwMCIgdGlmZjpSZXNvbHV0aW9uVW5pdD0iMiIgZXhpZjpDb2xvclNwYWNlPSI2NTUzNSIgZXhpZjpQaXhlbFhEaW1lbnNpb249IjMyIiBleGlmOlBpeGVsWURpbWVuc2lvbj0iMzIiPiA8eG1wTU06SGlzdG9yeT4gPHJkZjpTZXE+IDxyZGY6bGkgc3RFdnQ6YWN0aW9uPSJjcmVhdGVkIiBzdEV2dDppbnN0YW5jZUlEPSJ4bXAuaWlkOjczODgxZTYzLTE4ZWMtNjc0NC1iMjA5LTBhY2UxMWFhZGZiNSIgc3RFdnQ6d2hlbj0iMjAxOC0xMS0yOVQxMTozNzozMy0wNjowMCIgc3RFdnQ6c29mdHdhcmVBZ2VudD0iQWRvYmUgUGhvdG9zaG9wIENDIDIwMTkgKFdpbmRvd3MpIi8+IDxyZGY6bGkgc3RFdnQ6YWN0aW9uPSJzYXZlZCIgc3RFdnQ6aW5zdGFuY2VJRD0ieG1wLmlpZDo2MTk3ZjRkZi1iMTdiLWM1NDYtOWI5ZS0yMTc0MjY5ZWZjZmYiIHN0RXZ0OndoZW49IjIwMTgtMTEtMjlUMTE6Mzk6NTEtMDY6MDAiIHN0RXZ0OnNvZnR3YXJlQWdlbnQ9IkFkb2JlIFBob3Rvc2hvcCBDQyAyMDE5IChXaW5kb3dzKSIgc3RFdnQ6Y2hhbmdlZD0iLyIvPiA8cmRmOmxpIHN0RXZ0OmFjdGlvbj0ic2F2ZWQiIHN0RXZ0Omluc3RhbmNlSUQ9InhtcC5paWQ6MzBmYzcyMWUtOWNmZS1lYjRjLThlYzYtZTZkNTAzZWRkM2I5IiBzdEV2dDp3aGVuPSIyMDE5LTEwLTA0VDE2OjM4OjU1LTA1OjAwIiBzdEV2dDpzb2Z0d2FyZUFnZW50PSJBZG9iZSBQaG90b3Nob3AgQ0MgMjAxOSAoV2luZG93cykiIHN0RXZ0OmNoYW5nZWQ9Ii8iLz4gPHJkZjpsaSBzdEV2dDphY3Rpb249ImNvbnZlcnRlZCIgc3RFdnQ6cGFyYW1ldGVycz0iZnJvbSBhcHBsaWNhdGlvbi92bmQuYWRvYmUucGhvdG9zaG9wIHRvIGltYWdlL3BuZyIvPiA8cmRmOmxpIHN0RXZ0OmFjdGlvbj0iZGVyaXZlZCIgc3RFdnQ6cGFyYW1ldGVycz0iY29udmVydGVkIGZyb20gYXBwbGljYXRpb24vdm5kLmFkb2JlLnBob3Rvc2hvcCB0byBpbWFnZS9wbmciLz4gPHJkZjpsaSBzdEV2dDphY3Rpb249InNhdmVkIiBzdEV2dDppbnN0YW5jZUlEPSJ4bXAuaWlkOjczZGE5ZGMxLTg4ZDEtYjE0MC04Y2I1LWZhNTc5MjVjYjc5YyIgc3RFdnQ6d2hlbj0iMjAxOS0xMC0wNFQxNjozODo1NS0wNTowMCIgc3RFdnQ6c29mdHdhcmVBZ2VudD0iQWRvYmUgUGhvdG9zaG9wIENDIDIwMTkgKFdpbmRvd3MpIiBzdEV2dDpjaGFuZ2VkPSIvIi8+IDwvcmRmOlNlcT4gPC94bXBNTTpIaXN0b3J5PiA8eG1wTU06RGVyaXZlZEZyb20gc3RSZWY6aW5zdGFuY2VJRD0ieG1wLmlpZDozMGZjNzIxZS05Y2ZlLWViNGMtOGVjNi1lNmQ1MDNlZGQzYjkiIHN0UmVmOmRvY3VtZW50SUQ9ImFkb2JlOmRvY2lkOnBob3Rvc2hvcDphZWJmNGFhYy1jYTMyLWVmNGYtYjhmOC1jN2FhMzI3YzEzZDkiIHN0UmVmOm9yaWdpbmFsRG9jdW1lbnRJRD0ieG1wLmRpZDo3Mzg4MWU2My0xOGVjLTY3NDQtYjIwOS0wYWNlMTFhYWRmYjUiLz4gPHBob3Rvc2hvcDpEb2N1bWVudEFuY2VzdG9ycz4gPHJkZjpCYWc+IDxyZGY6bGk+YWRvYmU6ZG9jaWQ6cGhvdG9zaG9wOmFlYmY0YWFjLWNhMzItZWY0Zi1iOGY4LWM3YWEzMjdjMTNkOTwvcmRmOmxpPiA8cmRmOmxpPnhtcC5kaWQ6NzM4ODFlNjMtMThlYy02NzQ0LWIyMDktMGFjZTExYWFkZmI1PC9yZGY6bGk+IDwvcmRmOkJhZz4gPC9waG90b3Nob3A6RG9jdW1lbnRBbmNlc3RvcnM+IDwvcmRmOkRlc2NyaXB0aW9uPiA8L3JkZjpSREY+IDwveDp4bXBtZXRhPiA8P3hwYWNrZXQgZW5kPSJyIj8+e0woHQAAAPdJREFUWIXtld0NgzAMhM8VgyEWqNRBkllgkEpdoGIz94HQksT5oQTykpOQkCC+L45jEzOjpm5V3RtAAwDQnRTXvVqUBUBa+ZHG6fttfc/RGsus4RBE9Aj2GIoa+u2mxIYTBDhsHoAgrbA+PsDQA0NfzlyA4HGyMuFlgO+PsuYJCOKThgFptWTU1XveZpiImVmq/iKSAByILvnzGTLHweNUvxM2gF8NvOfy0TOKsOo1JK2oQ2RSHZC8KcccuLIGBHPA1IDViEza3Ja8dxznmAORDNDr+Z/ZDvMoQBGIhDmw3II8U3uIpGQFJa0otNYDuFrVO2EDaAAfFxx8VebINYwAAAAASUVORK5CYII=\" alt=\"Forward\"></div><div id=\"PageList\"><ul class=\"PageListCollapsibleTree\">"
    HTMLExportString += GeneratePageListItemHTML(Notebook.RootPage, Root=True)
    HTMLExportString += "</ul></div></div><div id=\"PageDisplay\"></div><div id=\"SearchInterfaceContainer\"><div id=\"SearchInterfaceHeader\"><input type=\"text\" id=\"SearchTextInput\" name=\"Search\" placeholder=\"Search\" value=\"\"><br><button type=\"button\" name=\"button\" onclick=\"SearchNotebook();\">Search Notebook</button><input type=\"checkbox\" id=\"MatchCaseCheckbox\" value=\"\"><label for=\"MatchCaseCheckbox\">Match Case</label></div><div id=\"SearchInterface\"><ul id=\"SearchResultsList\"></ul></div></div></body><script type=\"text/javascript\">document.getElementById(\"JavaScriptBlocked\").remove();document.getElementById(\"SearchTextInput\").addEventListener(\"keypress\", function(event) {if (event.key === \"Enter\") {event.preventDefault();SearchNotebook();}});var Pages = "
    HTMLExportString += GeneratePageDictionaryJavaScript(Notebook)
    HTMLExportString += ";var CurrentPage = null;var BackList = [];var ForwardList = [];var BackNavigation = false;var BackMaximum = 50;SelectPage(\"[0]\", true);function SelectPage(IndexPath, SkipUpdatingBackAndForward=false) {if (IndexPath === CurrentPage) {return false;}UpdatePageListDisplay(IndexPath);if (!SkipUpdatingBackAndForward) {UpdateBackAndForward();}var PageDisplay = document.getElementById(\"PageDisplay\");PageDisplay.innerHTML = Pages[IndexPath][0];PageDisplay.scrollTop = 0;CurrentPage = IndexPath;return false;}function UpdatePageListDisplay(IndexPath) {var PageLinks = document.getElementsByClassName(\"PageLink\");for (var i = 0; i < PageLinks.length; i++) {var PageLinkClassList = PageLinks[i].classList;if (PageLinkClassList.contains(\"PageListCurrentPage\")) {PageLinkClassList.remove(\"PageListCurrentPage\");}}ExpandParentPages(IndexPath);var SelectedPage = document.getElementById(IndexPath + \"link\");SelectedPage.classList.add(\"PageListCurrentPage\");SelectedPage.scrollIntoView(true);var PageList = document.getElementById(\"PageList\");var ScrollAdjustment = (PageList.scrollHeight - PageList.scrollTop <= PageList.clientHeight) ? 0 : PageList.clientHeight / 2;PageList.scrollTop = PageList.scrollTop - ScrollAdjustment;}function TogglePageExpansion(IndexPath) {var CheckboxID = IndexPath + \"checkbox\";var Checkbox = document.getElementById(CheckboxID);if (Checkbox.checked === true) {Checkbox.checked = false;} else if (Checkbox.checked === false) {Checkbox.checked = true;}}function ExpandParentPages(IndexPath) {var IndexPathArray = eval(IndexPath);for (var i = IndexPathArray.length - 1; i > 0; i--) {var IndexPathArraySlice = IndexPathArray.slice(0, i);var CheckboxID = \"[\" + IndexPathArraySlice.toString() + \"]\";CheckboxID = CheckboxID.replace(new RegExp(\",\", \"g\"), \", \");CheckboxID = CheckboxID + \"checkbox\";var Checkbox = document.getElementById(CheckboxID);Checkbox.checked = true;}}function UpdateBackAndForward() {if (!BackNavigation) {var PreviousPageIndexPath = CurrentPage;var PreviousPageScrollPosition = document.getElementById(\"PageDisplay\").scrollTop;var PreviousPageData = [PreviousPageIndexPath, PreviousPageScrollPosition];if (BackList.length !== 0) {if (BackList[BackList.length - 1][0] !== PreviousPageIndexPath) {BackList.push(PreviousPageData);}} else {BackList.push(PreviousPageData);}if (BackList.length > BackMaximum) {BackList = BackList.slice(-BackMaximum);}ForwardList.length = 0;}var BackButton = document.getElementById(\"BackButton\");var BackButtonClassList = BackButton.classList;if (BackList.length > 0) {if (BackButtonClassList.contains(\"ForwardBackDisabled\")) {BackButtonClassList.remove(\"ForwardBackDisabled\");}} else {if (!BackButtonClassList.contains(\"ForwardBackDisabled\")) {BackButtonClassList.add(\"ForwardBackDisabled\");}}var ForwardButton = document.getElementById(\"ForwardButton\");var ForwardButtonClassList = ForwardButton.classList;if (ForwardList.length > 0) {if (ForwardButtonClassList.contains(\"ForwardBackDisabled\")) {ForwardButtonClassList.remove(\"ForwardBackDisabled\");}} else {if (!ForwardButtonClassList.contains(\"ForwardBackDisabled\")) {ForwardButtonClassList.add(\"ForwardBackDisabled\");}}}function Back() {if (BackList.length > 0) {BackNavigation = true;var TargetPageIndexPath = BackList[BackList.length - 1][0];var TargetPageScrollPosition = BackList[BackList.length - 1][1];BackList.length = BackList.length - 1;var PageDisplay = document.getElementById(\"PageDisplay\");var CurrentPageScrollPosition = PageDisplay.scrollTop;var CurrentPageData = [CurrentPage, CurrentPageScrollPosition];ForwardList.push(CurrentPageData);SelectPage(TargetPageIndexPath);PageDisplay.scrollTop = TargetPageScrollPosition;BackNavigation = false;}}function Forward() {if (ForwardList.length > 0) {BackNavigation = true;var TargetPageIndexPath = ForwardList[ForwardList.length - 1][0];var TargetPageScrollPosition = ForwardList[ForwardList.length - 1][1];ForwardList.length = ForwardList.length - 1;var PageDisplay = document.getElementById(\"PageDisplay\");var CurrentPageScrollPosition = PageDisplay.scrollTop;var CurrentPageData = [CurrentPage, CurrentPageScrollPosition];BackList.push(CurrentPageData);SelectPage(TargetPageIndexPath);PageDisplay.scrollTop = TargetPageScrollPosition;BackNavigation = false;}}function SearchNotebook() {var SearchText = document.getElementById(\"SearchTextInput\").value;var SearchResultsList = document.getElementById(\"SearchResultsList\");var SearchResultsHTMLString = \"\";if (SearchText === \"\") {SearchResultsList.innerHTML = SearchResultsHTMLString;} else {var MatchCase = document.getElementById(\"MatchCaseCheckbox\").checked;if (!MatchCase) {SearchText = SearchText.toLowerCase();}var SearchResultsArray = [];for (IndexPath in Pages) {var PageContent = Pages[IndexPath][1];var PageTitle = Pages[IndexPath][2];var ExactTitleMatch = (MatchCase ? PageTitle : PageTitle.toLowerCase()) === SearchText;var TitleHits = (MatchCase ? PageTitle : PageTitle.toLowerCase()).split(SearchText).length - 1;var ContentHits = (MatchCase ? PageContent : PageContent.toLowerCase()).split(SearchText).length - 1;if (ExactTitleMatch || TitleHits > 0 || ContentHits > 0) {SearchResultsArray.push({\"ExactTitleMatch\": ExactTitleMatch, \"TitleHits\": TitleHits, \"ContentHits\": ContentHits, \"IndexPath\": IndexPath, \"PageTitle\": PageTitle});}}SearchResultsArray.sort(function (a, b) {var Result = 0;var MatchCriteria = [\"ExactTitleMatch\", \"TitleHits\", \"ContentHits\"];for (MatchCriterion of MatchCriteria) {Result = a[MatchCriterion] < b[MatchCriterion] ? 1 : a[MatchCriterion] > b[MatchCriterion] ? -1 : 0;if (Result !== 0) {return Result;}}return Result;});for (Result of SearchResultsArray) {SearchResultsHTMLString += \"<li><span onclick=\\\"SelectPage(&quot;\" + Result[\"IndexPath\"] + \"&quot;);\\\">\" + Result[\"PageTitle\"] + \"</span></li>\";}SearchResultsList.innerHTML = SearchResultsHTMLString;}}</script></html>"
    return HTMLExportString


def GeneratePageListItemHTML(Page, Root=False):
    if len(Page["SubPages"]) > 0:
        ListItemString = "<li class=\"PageListCollapsibleItem\"><input type=\"checkbox\" id=\"" + str(Page["IndexPath"]) + "checkbox\"" + (" checked=\"checked\"" if Root else "") + "><label for=\"" + str(Page["IndexPath"]) + "checkbox\"></label><span id=\"" + str(Page["IndexPath"]) + "link\" class=\"PageLink\" onclick=\"SelectPage(&quot;" + str(Page["IndexPath"]) + "&quot;);\" ondblclick=\"TogglePageExpansion(&quot;" + str(Page["IndexPath"]) + "&quot;);\">" + Page["Title"] + "</span><ul>"
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
