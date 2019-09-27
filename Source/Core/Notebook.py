import os

from Core import Base64Converters
from SaveAndLoad.JSONSerializer import SerializableMixin


class Notebook(SerializableMixin):
    def __init__(self):
        # Variables
        self.Header = "# {PAGETITLE}"
        self.Footer = "***\n\nSub Pages:\n\n{SUBPAGELINKS}\n\nSub Page Of:  {SUBPAGEOFLINK}"
        self.RootPage = self.CreatePage("New Notebook")
        self.Images = {}
        self.PageTemplates = {}

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

    # TODO:  Promote and Demote methods

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
        return sorted(self.Images.keys())

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
        return sorted(self.PageTemplates.keys())

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
