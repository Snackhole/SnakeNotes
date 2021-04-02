import json
import os

from Core import Base64Converters
from SaveAndLoad.JSONSerializer import SerializableMixin


class Notebook(SerializableMixin):
    def __init__(self):
        # Variables
        self.DefaultHeader = "# {PAGETITLE}"
        self.DefaultFooter = "***\n\nSub Pages:\n\n{SUBPAGELINKS}\n\nSub Page Of:  {SUBPAGEOFLINK}\n\nLinking Pages:\n\n{LINKINGPAGES}"
        self.Header = self.DefaultHeader
        self.Footer = self.DefaultFooter
        self.RootPage = self.CreatePage("New Notebook")
        self.Images = {}
        self.PageTemplates = {}
        self.SearchIndexUpToDate = False
        self.SearchIndex = []

    # Page Methods
    def CreatePage(self, Title="New Page", Content="", IndexPath=None):
        if IndexPath is None:
            IndexPath = [0]
        Page = {}
        Page["Title"] = Title
        Page["Content"] = Content
        Page["IndexPath"] = IndexPath
        Page["SubPages"] = []
        return Page

    def AddSubPage(self, Title="New Page", Content="", SuperPageIndexPath=None, PageToAdd=None):
        if SuperPageIndexPath is None:
            SuperPageIndexPath = [0]
        if PageToAdd is None:
            PageToAdd = self.CreatePage(Title, Content)
        SuperPage = self.GetPageFromIndexPath(SuperPageIndexPath)
        if SuperPage is None:
            return
        SuperPage["SubPages"].append(PageToAdd)
        self.UpdateIndexPaths()

    def DeleteSubPage(self, IndexPath):
        SuperPage = self.GetSuperOfPageFromIndexPath(IndexPath)
        if SuperPage is None:
            return
        del SuperPage["SubPages"][IndexPath[-1]]
        self.UpdateIndexPaths()

    def MoveSubPage(self, IndexPath, Delta):
        SuperPage = self.GetSuperOfPageFromIndexPath(IndexPath)
        if SuperPage is None:
            return False
        PageToMoveIndex = IndexPath[-1]
        TargetPageIndex = PageToMoveIndex + Delta
        if TargetPageIndex < 0 or TargetPageIndex > len(SuperPage["SubPages"]) - 1:
            return False
        PageToMove = SuperPage["SubPages"][PageToMoveIndex]
        TargetPage = SuperPage["SubPages"][TargetPageIndex]
        SuperPage["SubPages"][PageToMoveIndex] = TargetPage
        SuperPage["SubPages"][TargetPageIndex] = PageToMove
        self.UpdateIndexPaths()
        return True

    def PromoteSubPage(self, IndexPath):
        SuperPage = self.GetSuperOfPageFromIndexPath(IndexPath)
        if SuperPage["IndexPath"] == [0] or IndexPath == [0]:
            return
        CurrentPage = self.GetPageFromIndexPath(IndexPath)
        self.DeleteSubPage(IndexPath)
        SuperOfSuperIndexPath = self.GetSuperOfPageFromIndexPath(self.GetSuperOfPageFromIndexPath(IndexPath)["IndexPath"])["IndexPath"]
        self.AddSubPage(SuperPageIndexPath=SuperOfSuperIndexPath, PageToAdd=CurrentPage)

    def DemoteSubPage(self, IndexPath, SiblingPageIndex):
        if IndexPath == [0]:
            return
        CurrentPage = self.GetPageFromIndexPath(IndexPath)
        TargetSiblingPage = self.GetPageFromIndexPath(IndexPath[:-1] + [SiblingPageIndex])
        self.DeleteSubPage(IndexPath)
        self.AddSubPage(SuperPageIndexPath=TargetSiblingPage["IndexPath"], PageToAdd=CurrentPage)

    def GetPageFromIndexPath(self, IndexPath):
        if len(IndexPath) < 1:
            return None
        DestinationPage = self.RootPage
        try:
            for Index in IndexPath[1:]:
                DestinationPage = DestinationPage["SubPages"][Index]
            return DestinationPage
        except IndexError:
            return None

    def GetSuperOfPageFromIndexPath(self, IndexPath):
        return self.GetPageFromIndexPath(IndexPath[:-1])

    def UpdateIndexPaths(self):
        self.RootPage["IndexPath"] = [0]
        self.UpdateSubPageIndexPaths(self.RootPage["IndexPath"], self.RootPage["SubPages"])

    def UpdateSubPageIndexPaths(self, CurrentIndexPath, SubPagesList):
        for Index in range(len(SubPagesList)):
            SubPagesList[Index]["IndexPath"] = CurrentIndexPath + [Index]
            self.UpdateSubPageIndexPaths(SubPagesList[Index]["IndexPath"], SubPagesList[Index]["SubPages"])

    def StringIsValidIndexPath(self, IndexPathString):
        try:
            IndexPath = json.loads(IndexPathString)
        except:
            return False
        if not isinstance(IndexPath, list):
            return False
        if len(IndexPath) < 1:
            return False
        if IndexPath[0] != 0:
            return False
        for Element in IndexPath:
            if not isinstance(Element, int):
                return False
            if Element < 0:
                return False
        try:
            DestinationPage = self.GetPageFromIndexPath(IndexPath)
        except IndexError:
            return False
        if DestinationPage is None:
            return False
        return True

    def AddTextToPageAndSubpages(self, Text, CurrentPage=None, Prepend=False):
        if CurrentPage is None:
            CurrentPage = self.RootPage
        if Prepend:
            NewContent = Text + CurrentPage["Content"]
        else:
            NewContent = CurrentPage["Content"] + Text
        CurrentPage["Content"] = NewContent
        for Page in CurrentPage["SubPages"]:
            self.AddTextToPageAndSubpages(Text, Page, Prepend=Prepend)

    # Image Methods
    def HasImage(self, FileName):
        return FileName in self.Images

    def AddImage(self, FilePath, FileName=None):
        if FileName is None:
            FileName = os.path.basename(FilePath)
        Base64String = Base64Converters.GetBase64StringFromFilePath(FilePath)
        self.Images[FileName] = Base64String

    def GetImage(self, FileName):
        if not self.HasImage(FileName):
            return None
        return self.Images[FileName]

    def GetImageNames(self):
        return sorted(self.Images.keys(), key=lambda ImageName: ImageName.lower())

    # Template Methods
    def HasTemplate(self, TemplateName):
        return TemplateName in self.PageTemplates

    def AddTemplate(self, TemplateName, TemplateContent):
        self.PageTemplates[TemplateName] = TemplateContent

    def GetTemplate(self, TemplateName):
        if not self.HasTemplate(TemplateName):
            return None
        return self.PageTemplates[TemplateName]

    def GetTemplateNames(self):
        return sorted(self.PageTemplates.keys(), key=lambda TemplateName: TemplateName.lower())

    # Search Methods
    def BuildSearchIndex(self):
        self.SearchIndex.clear()
        self.AddPageToSearchIndex(self.RootPage)
        self.SearchIndexUpToDate = True

    def AddPageToSearchIndex(self, Page):
        self.SearchIndex.append((Page["Title"], Page["Content"], Page["IndexPath"]))
        for SubPage in Page["SubPages"]:
            self.AddPageToSearchIndex(SubPage)

    def GetSearchResults(self, SearchTermString, MatchCase=False, ExactTitleOnly=False):
        if not MatchCase:
            SearchTermString = SearchTermString.casefold()
        if not self.SearchIndexUpToDate:
            self.BuildSearchIndex()
        ResultsList = []
        TotalHits = 0
        TotalPages = 0
        for PageData in self.SearchIndex:
            ExactTitle = (PageData[0].casefold() if not MatchCase else PageData[0]) == SearchTermString
            TitleHits = (PageData[0].casefold() if not MatchCase else PageData[0]).count(SearchTermString)
            ContentHits = (PageData[1].casefold() if not MatchCase else PageData[1]).count(SearchTermString)
            if (ExactTitleOnly and ExactTitle) or (not ExactTitleOnly and (TitleHits > 0 or ContentHits > 0)):
                ResultsList.append((PageData[0], PageData[2], ExactTitle, TitleHits, ContentHits))
                TotalHits += TitleHits + ContentHits
                TotalPages += 1
        ResultsList = sorted(ResultsList, key=lambda Result: (Result[2], Result[3], Result[4]), reverse=True)
        Results = {"ResultsList": ResultsList, "TotalHits": TotalHits, "TotalPages": TotalPages}
        return Results

    # Serialization Methods
    def SetState(self, NewState):
        self.Header = NewState["Header"]
        self.Footer = NewState["Footer"]
        self.RootPage = NewState["RootPage"]
        self.Images = NewState["Images"]
        self.PageTemplates = NewState["PageTemplates"]

    def GetState(self):
        State = {}
        State["Header"] = self.Header
        State["Footer"] = self.Footer
        State["RootPage"] = self.RootPage
        State["Images"] = self.Images
        State["PageTemplates"] = self.PageTemplates
        return State

    @classmethod
    def CreateFromState(cls, State):
        NewNotebook = cls()
        NewNotebook.SetState(State)
        return NewNotebook
