import os

from Core import Base64Converters
from SaveAndLoad.JSONSerializer import SerializableMixin


class Page(SerializableMixin):
    def __init__(self, PageIndex, Title, Content, Path=None, IsRootPage=False, SubPages=None, Images=None, PageTemplates=None, Header=None, Footer=None):
        # Store Parameters
        self.PageIndex = PageIndex
        self.Title = Title
        self.Content = Content
        self.SubPages = SubPages if SubPages is not None else []
        self.Path = Path if Path is not None else []
        self.IsRootPage = IsRootPage
        self.Images = Images if Images is not None else ({} if self.IsRootPage else None)
        self.PageTemplates = PageTemplates if PageTemplates is not None else ({} if self.IsRootPage else None)
        self.Header = Header if Header is not None else ("# {PAGETITLE}" if self.IsRootPage else None)
        self.Footer = Footer if Footer is not None else ("" if self.IsRootPage else None)

        # Initialize Serializable Mixin
        super().__init__()

    # Sub Page Methods
    def AddSubPage(self, Title, Content):
        PageIndex = len(self.SubPages)
        SubPagePath = self.GetFullIndexPath()
        self.SubPages.append(Page(PageIndex, str(Title), str(Content), SubPagePath))

    def AppendSubPage(self, PageToAppend):
        self.SubPages.append(PageToAppend)
        PageToAppend.UpdatePath(self.GetFullIndexPath(), len(self.SubPages) - 1)

    def DeleteSubPage(self, PageIndex):
        del self.SubPages[PageIndex]
        self.RefreshSubPageIndices()

    def MovePage(self, PageIndex, Delta):
        TargetPageIndex = PageIndex + Delta
        if TargetPageIndex < 0 or TargetPageIndex > len(self.SubPages) - 1:
            return False
        PageToMove = self.SubPages[PageIndex]
        TargetPage = self.SubPages[TargetPageIndex]
        self.SubPages[PageIndex] = TargetPage
        self.SubPages[TargetPageIndex] = PageToMove
        PageToMove.UpdatePageIndex(TargetPageIndex)
        TargetPage.UpdatePageIndex(PageIndex)
        return True

    def GetSubPageByIndexPath(self, IndexPath):
        DestinationPage = self
        for PathElement in IndexPath[1:]:
            DestinationPage = DestinationPage.SubPages[PathElement]
        return DestinationPage

    def GetSuperOfSubPageByIndexPath(self, IndexPath):
        SuperIndexPath = IndexPath[:-1]
        return self.GetSubPageByIndexPath(SuperIndexPath)

    def GetFullIndexPath(self):
        FullIndexPath = self.Path.copy()
        FullIndexPath.append(self.PageIndex)
        return FullIndexPath

    def UpdatePageIndex(self, NewIndex):
        self.PageIndex = NewIndex
        self.RefreshIndexPaths()

    def UpdatePath(self, NewPath, NewIndex):
        self.Path = NewPath
        self.UpdatePageIndex(NewIndex)

    def RefreshIndexPaths(self):
        NewPath = self.GetFullIndexPath()
        for SubPage in self.SubPages:
            SubPage.Path = NewPath
            SubPage.RefreshIndexPaths()

    def RefreshSubPageIndices(self):
        for Index in range(len(self.SubPages)):
            self.SubPages[Index].UpdatePageIndex(Index)

    # Image Methods
    def HasImage(self, FileName):
        if self.Images is None:
            return False
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
        if self.Images is None:
            return None
        return sorted(self.Images.keys())

    # Template Methods
    def HasTemplate(self, TemplateName):
        if self.PageTemplates is None:
            return False
        return TemplateName in self.PageTemplates

    def AddTemplate(self, TemplateName, TemplateContent):
        self.PageTemplates[TemplateName] = TemplateContent

    def GetTemplate(self, TemplateName):
        if not self.HasTemplate(TemplateName):
            return None
        return self.PageTemplates[TemplateName]

    def GetTemplateNames(self):
        if self.PageTemplates is None:
            return None
        return sorted(self.PageTemplates.keys())

    # Serialization Methods
    def SetState(self, NewState):
        self.PageIndex = NewState["PageIndex"]
        self.Title = NewState["Title"]
        self.Content = NewState["Content"]
        self.SubPages = NewState["SubPages"]
        self.Path = NewState["Path"]
        self.IsRootPage = NewState["IsRootPage"]
        self.Images = NewState["Images"]
        self.PageTemplates = NewState["PageTemplates"]
        self.Header = NewState["Header"]
        self.Footer = NewState["Footer"]

    def GetState(self):
        Data = {}
        Data["PageIndex"] = self.PageIndex
        Data["Title"] = self.Title
        Data["Content"] = self.Content
        Data["SubPages"] = self.SubPages
        Data["Path"] = self.Path
        Data["IsRootPage"] = self.IsRootPage
        Data["Images"] = self.Images
        Data["PageTemplates"] = self.PageTemplates
        Data["Header"] = self.Header
        Data["Footer"] = self.Footer
        return Data

    @classmethod
    def CreateFromState(cls, State):
        NewPage = cls(State["PageIndex"], State["Title"], State["Content"], State["Path"], State["IsRootPage"], State["SubPages"], State["Images"], State["PageTemplates"], State["Header"], State["Footer"])
        return NewPage
