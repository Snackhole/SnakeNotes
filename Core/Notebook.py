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
        SuperPage = self.GetPageFromIndexPath(SuperPageIndexPath)
        if SuperPage is None:
            return
        if PageToAdd is None:
            PageToAdd = self.CreatePage(Title, Content)
        SuperPage["SubPages"].append(PageToAdd)
        self.UpdateIndexPaths()

    def AddSiblingPageBefore(self, IndexPath, Title="New Page", Content="", PageToAdd=None):
        SuperPage = self.GetSuperOfPageFromIndexPath(IndexPath)
        if SuperPage is None:
            return
        if PageToAdd is None:
            PageToAdd = self.CreatePage(Title, Content)
        SuperPage["SubPages"].insert(IndexPath[-1], PageToAdd)
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

    def PromoteAllSubPages(self, IndexPath):
        if IndexPath == [0]:
            return
        CurrentPage = self.GetPageFromIndexPath(IndexPath)
        if len(CurrentPage["SubPages"]) == 0:
            return
        SuperPage = self.GetSuperOfPageFromIndexPath(IndexPath)
        for SubPage in CurrentPage["SubPages"]:
            SuperPage["SubPages"].append(SubPage)
        CurrentPage["SubPages"].clear()
        self.UpdateIndexPaths()

    def DemoteAllSiblingPages(self, IndexPath):
        if IndexPath == [0]:
            return
        SuperPage = self.GetSuperOfPageFromIndexPath(IndexPath)
        if len(SuperPage["SubPages"]) < 2:
            return
        CurrentPage = self.GetPageFromIndexPath(IndexPath)
        SiblingPages = [Page for Page in SuperPage["SubPages"] if Page["IndexPath"] != IndexPath]
        SuperPage["SubPages"].clear()
        SuperPage["SubPages"].append(CurrentPage)
        for SiblingPage in SiblingPages:
            CurrentPage["SubPages"].append(SiblingPage)
        self.UpdateIndexPaths()

    def MoveSubPageTo(self, IndexPath, DestinationIndexPath):
        SuperPage = self.GetSuperOfPageFromIndexPath(IndexPath)
        if IndexPath == [0] or SuperPage["IndexPath"] == DestinationIndexPath or IndexPath == DestinationIndexPath[:len(IndexPath)]:
            return
        CurrentPage = self.GetPageFromIndexPath(IndexPath)
        DestinationPage = self.GetPageFromIndexPath(DestinationIndexPath)
        self.DeleteSubPage(IndexPath)
        self.AddSubPage(SuperPageIndexPath=DestinationPage["IndexPath"], PageToAdd=CurrentPage)

    def AlphabetizeSubPages(self, IndexPath):
        CurrentPage = self.GetPageFromIndexPath(IndexPath)
        if len(CurrentPage["SubPages"]) < 2:
            return
        CurrentPage["SubPages"].sort(key=lambda SubPage: SubPage["Title"].casefold())
        self.UpdateIndexPaths()

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
        return sorted(self.Images.keys(), key=lambda ImageName: ImageName.casefold())

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
        return sorted(self.PageTemplates.keys(), key=lambda TemplateName: TemplateName.casefold())

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

    def GetFilteredSearchResults(self, Results, Filters):
        # Create Filtered Results List and Counts
        FilteredResultsList = []
        TotalHits = 0
        TotalPages = 0

        # Filter Each Result
        for Result in Results["ResultsList"]:
            # Current Result Variables
            CurrentPage = self.GetPageFromIndexPath(Result[1])
            ValidResult = True

            # Page Filtering
            if ValidResult and "WithinPageIndexPath" in Filters:
                WithinPageIndexPath = Filters["WithinPageIndexPath"]
                if WithinPageIndexPath != CurrentPage["IndexPath"][:len(WithinPageIndexPath)]:
                    ValidResult = False

            # Title Filtering
            if ValidResult and "TitleContains" in Filters:
                CurrentTitle = CurrentPage["Title"]
                TitleContainsText = Filters["TitleContains"]["Text"]
                if not Filters["TitleContains"]["MatchCase"]:
                    TitleContainsText = TitleContainsText.casefold()
                    CurrentTitle = CurrentTitle.casefold()
                if not TitleContainsText in CurrentTitle:
                    ValidResult = False
            if ValidResult and "TitleDoesNotContain" in Filters:
                CurrentTitle = CurrentPage["Title"]
                TitleDoesNotContainText = Filters["TitleDoesNotContain"]["Text"]
                if not Filters["TitleDoesNotContain"]["MatchCase"]:
                    TitleDoesNotContainText = TitleDoesNotContainText.casefold()
                    CurrentTitle = CurrentTitle.casefold()
                if TitleDoesNotContainText in CurrentTitle:
                    ValidResult = False
            if ValidResult and "TitleStartsWith" in Filters:
                CurrentTitle = CurrentPage["Title"]
                TitleStartsWithText = Filters["TitleStartsWith"]["Text"]
                if not Filters["TitleStartsWith"]["MatchCase"]:
                    TitleStartsWithText = TitleStartsWithText.casefold()
                    CurrentTitle = CurrentTitle.casefold()
                if not CurrentTitle.startswith(TitleStartsWithText):
                    ValidResult = False
            if ValidResult and "TitleEndsWith" in Filters:
                CurrentTitle = CurrentPage["Title"]
                TitleEndsWithText = Filters["TitleEndsWith"]["Text"]
                if not Filters["TitleEndsWith"]["MatchCase"]:
                    TitleEndsWithText = TitleEndsWithText.casefold()
                    CurrentTitle = CurrentTitle.casefold()
                if not CurrentTitle.endswith(TitleEndsWithText):
                    ValidResult = False

            # Content Filtering
            if ValidResult and "ContentContains" in Filters:
                CurrentContent = CurrentPage["Content"]
                ContentContainsText = Filters["ContentContains"]["Text"]
                if not Filters["ContentContains"]["MatchCase"]:
                    ContentContainsText = ContentContainsText.casefold()
                    CurrentContent = CurrentContent.casefold()
                if not ContentContainsText in CurrentContent:
                    ValidResult = False
            if ValidResult and "ContentDoesNotContain" in Filters:
                CurrentContent = CurrentPage["Content"]
                ContentDoesNotContainText = Filters["ContentDoesNotContain"]["Text"]
                if not Filters["ContentDoesNotContain"]["MatchCase"]:
                    ContentDoesNotContainText = ContentDoesNotContainText.casefold()
                    CurrentContent = CurrentContent.casefold()
                if ContentDoesNotContainText in CurrentContent:
                    ValidResult = False
            if ValidResult and "ContentStartsWith" in Filters:
                CurrentContent = CurrentPage["Content"]
                ContentStartsWithText = Filters["ContentStartsWith"]["Text"]
                if not Filters["ContentStartsWith"]["MatchCase"]:
                    ContentStartsWithText = ContentStartsWithText.casefold()
                    CurrentContent = CurrentContent.casefold()
                if not CurrentContent.startswith(ContentStartsWithText):
                    ValidResult = False
            if ValidResult and "ContentEndsWith" in Filters:
                CurrentContent = CurrentPage["Content"]
                ContentEndsWithText = Filters["ContentEndsWith"]["Text"]
                if not Filters["ContentEndsWith"]["MatchCase"]:
                    ContentEndsWithText = ContentEndsWithText.casefold()
                    CurrentContent = CurrentContent.casefold()
                if not CurrentContent.endswith(ContentEndsWithText):
                    ValidResult = False

            # Append Valid Results and Update Counts
            if ValidResult:
                FilteredResultsList.append(Result)
                TotalHits += Result[3] + Result[4]
                TotalPages += 1

        # Create and Return Filtered Search Results Dictionary
        FilteredSearchResults = {"ResultsList": FilteredResultsList, "TotalHits": TotalHits, "TotalPages": TotalPages}
        return FilteredSearchResults

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
