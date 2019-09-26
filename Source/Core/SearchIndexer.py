class SearchIndexer:
    def __init__(self, RootPage):
        # Store Parameters
        self.RootPage = RootPage

        # Variables
        self.IndexUpToDate = False

        # Create Index
        self.Index = []

    def BuildIndex(self):
        self.Index.clear()
        self.IndexPage(self.RootPage)
        self.IndexUpToDate = True

    def IndexPage(self, Page):
        self.Index.append((Page.Title, Page.Content, Page.GetFullIndexPath()))
        for SubPage in Page.SubPages:
            self.IndexPage(SubPage)

    def GetSearchResults(self, SearchTermString, MatchCase=False, ExactTitleOnly=False):
        if not MatchCase:
            SearchTermString = SearchTermString.casefold()
        if not self.IndexUpToDate:
            self.BuildIndex()
        Results = []
        for PageData in self.Index:
            ExactTitle = (PageData[0].casefold() if not MatchCase else PageData[0]) == SearchTermString
            TitleHits = (PageData[0].casefold() if not MatchCase else PageData[0]).count(SearchTermString)
            ContentHits = (PageData[1].casefold() if not MatchCase else PageData[1]).count(SearchTermString)
            if (ExactTitleOnly and ExactTitle) or (not ExactTitleOnly and (TitleHits > 0 or ContentHits > 0)):
                Results.append((PageData[0], PageData[2], ExactTitle, TitleHits, ContentHits))
        Results = sorted(Results, key=lambda Result: (Result[2], Result[3], Result[4]), reverse=True)
        return Results
