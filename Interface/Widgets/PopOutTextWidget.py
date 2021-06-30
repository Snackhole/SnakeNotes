from PyQt5.QtWidgets import QTextEdit

from Core import MarkdownRenderers


class PopOutTextWidget(QTextEdit):
    def __init__(self, Page, Notebook, PopOutMarkdownParser):
        super().__init__()

        # Store Parameters
        self.Page = Page
        self.Notebook = Notebook
        self.PopOutMarkdownParser = PopOutMarkdownParser

        # Tab Behavior
        self.setTabChangesFocus(True)

        # Set Read Only
        self.setReadOnly(True)

        # Set Style Sheet
        self.setStyleSheet("selection-background-color: rgb(0, 120, 215); selection-color: white")

    def RefreshPageDisplay(self):
        DisplayText = MarkdownRenderers.ConstructMarkdownStringFromPage(self.Page, self.Notebook)
        HTMLText = self.PopOutMarkdownParser(DisplayText)
        self.setHtml(HTMLText)
