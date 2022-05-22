import json
import re
import webbrowser

import mistune
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor, QSyntaxHighlighter, QTextCursor, QTextCharFormat
from PyQt5.QtWidgets import QTextEdit, QInputDialog, QMessageBox

from Core import MarkdownRenderers
from Interface.Dialogs.InsertLinksDialog import InsertLinksDialog
from Interface.Dialogs.InsertTableDialog import InsertTableDialog, TableDimensionsDialog
from Interface.Dialogs.InsertImageDialog import InsertImageDialog


class TextWidget(QTextEdit):
    def __init__(self, Notebook, MainWindow):
        super().__init__()

        # Store Parameters
        self.Notebook = Notebook
        self.MainWindow = MainWindow

        # Variables
        self.CurrentPage = self.Notebook.RootPage
        self.DisplayChanging = False
        self.ReadMode = True
        self.DefaultCharacterFormat = QTextCharFormat()

        # Create Markdown Parser
        self.Renderer = MarkdownRenderers.Renderer(self.Notebook)
        self.MarkdownParser = mistune.Markdown(renderer=self.Renderer)

        # Create Syntax Highlighter
        self.SyntaxHighlighter = SyntaxHighlighter(self)

        # Tab Behavior
        self.setTabChangesFocus(True)

        # Set Read Only
        self.setReadOnly(True)

        # Set Style Sheet
        self.setStyleSheet("selection-background-color: rgb(0, 120, 215); selection-color: white")

        # Set Up Auto Scrolling Method
        self.verticalScrollBar().rangeChanged.connect(self.AutoScroll)

    def UpdateText(self):
        self.DisplayChanging = True
        if self.ReadMode:
            DisplayText = MarkdownRenderers.ConstructMarkdownStringFromPage(self.CurrentPage, self.Notebook)
            HTMLText = self.MarkdownParser(DisplayText)
            self.setHtml(HTMLText)
        else:
            self.setCurrentCharFormat(self.DefaultCharacterFormat)
            self.setPlainText(self.CurrentPage["Content"])
        self.DisplayChanging = False

    def SetCurrentPage(self, Page):
        self.CurrentPage = Page
        self.UpdateText()

    def SetReadMode(self, ReadMode):
        self.ReadMode = ReadMode
        self.setReadOnly(self.ReadMode)
        self.UpdateText()

    def AutoScroll(self):
        if self.MainWindow.AutoScrollQueue is not None:
            if self.verticalScrollBar().maximum() == self.MainWindow.AutoScrollQueue["ScrollBarMaximum"]:
                self.verticalScrollBar().setValue(self.MainWindow.AutoScrollQueue["TargetScrollPosition"])
                self.MainWindow.AutoScrollQueue = None

    # Internal Text and Cursor Methods
    def SelectionSpanWrap(self, WrapPrefix, WrapSuffix):
        Cursor = self.textCursor()
        TextToWrap = Cursor.selectedText()
        if "\u2029" in TextToWrap:
            return
        Cursor.beginEditBlock()
        WrappedText = WrapPrefix + TextToWrap + WrapSuffix
        self.insertPlainText(WrappedText)
        for Character in range(len(WrapSuffix)):
            self.moveCursor(QTextCursor.Left)
        Cursor.endEditBlock()

    def SingleBlockPrefix(self, Prefix):
        Cursor = self.textCursor()
        SelectedText = Cursor.selectedText()
        if "\u2029" in SelectedText:
            return
        Cursor.beginEditBlock()
        Cursor.movePosition(QTextCursor.StartOfBlock)
        Cursor.insertText(Prefix)
        self.MakeCursorVisible()
        Cursor.endEditBlock()

    def SelectBlocks(self, Cursor):
        CursorPosition = Cursor.position()
        AnchorPosition = Cursor.anchor()

        if AnchorPosition > CursorPosition:
            AnchorPosition, CursorPosition = CursorPosition, AnchorPosition

        Cursor.setPosition(AnchorPosition)
        Cursor.movePosition(QTextCursor.StartOfBlock)
        BlockStartPosition = Cursor.position()

        Cursor.setPosition(CursorPosition)
        Cursor.movePosition(QTextCursor.EndOfBlock)
        BlockEndPosition = Cursor.position()

        Cursor.setPosition(BlockStartPosition)
        Cursor.setPosition(BlockEndPosition, QTextCursor.KeepAnchor)

    def MultipleBlockPrefix(self, Prefix):
        Cursor = self.textCursor()
        self.SelectBlocks(Cursor)
        Blocks = Cursor.selectedText().split("\u2029")
        PrefixedText = ""

        if Prefix == "1. ":
            CurrentPrefixInt = 1
            for Block in Blocks:
                if Block != "":
                    PrefixedText += str(CurrentPrefixInt) + ". " + Block + "\u2029"
                    CurrentPrefixInt += 1
                else:
                    PrefixedText += Block + "\u2029"
        else:
            for Block in Blocks:
                PrefixedText += (Prefix if Block != "" else "") + Block + "\u2029"

        Cursor.beginEditBlock()
        Cursor.insertText(PrefixedText[:-1])
        self.MakeCursorVisible()
        Cursor.endEditBlock()

    def MultipleBlockWrap(self, WrapSymbol):
        Cursor = self.textCursor()
        self.SelectBlocks(Cursor)
        SelectedBlocksText = Cursor.selectedText()
        WrappedText = WrapSymbol + "\u2029" + SelectedBlocksText + "\u2029" + WrapSymbol

        Cursor.beginEditBlock()
        Cursor.insertText(WrappedText)
        for Character in range(len(WrapSymbol) + 1):
            self.moveCursor(QTextCursor.Left)
        self.MakeCursorVisible()
        Cursor.endEditBlock()

    def InsertOnBlankLine(self, InsertSymbol):
        Cursor = self.textCursor()
        if self.CursorOnBlankLine(Cursor):
            Cursor.beginEditBlock()
            self.insertPlainText(InsertSymbol)
            self.MakeCursorVisible()
            Cursor.endEditBlock()

    def MoveLine(self, Delta):
        if Delta != 0:
            LineData = self.GetLineData()
            if (Delta < 0 and LineData[1] > 0) or (Delta > 0 and LineData[1] < len(LineData[0]) - 1):
                CurrentLine = LineData[0][LineData[1]]
                TargetIndex = LineData[1] + (-1 if Delta < 0 else 1)
                TargetLine = LineData[0][TargetIndex]
                LineData[0][LineData[1]] = TargetLine
                LineData[0][TargetIndex] = CurrentLine
                Text = self.GetTextFromLineData(LineData)
                NewPosition = LineData[2] + ((len(TargetLine) + 1) * (-1 if Delta < 0 else 1))
                self.setPlainText(Text)
                Cursor = self.textCursor()
                Cursor.setPosition(NewPosition)
                self.setTextCursor(Cursor)
                self.VerticallyCenterCursor()

    def GetLineData(self, CursorToCopy=None):
        Text = self.toPlainText()
        Lines = Text.splitlines()
        if Text.endswith("\n"):
            Lines.append("")
        Cursor = self.textCursor() if CursorToCopy is None else QTextCursor(CursorToCopy)
        AbsolutePosition = Cursor.position()
        BlockPosition = Cursor.positionInBlock()
        LineIndex = 0
        CurrentPosition = AbsolutePosition
        for Index in range(len(Lines)):
            LineLength = len(Lines[Index])
            if LineLength < CurrentPosition:
                CurrentPosition -= LineLength + 1
            else:
                LineIndex = Index
                break
        LineData = (Lines, LineIndex, AbsolutePosition, BlockPosition)
        return LineData

    def GetTextFromLineData(self, LineData):
        Text = "\n".join(LineData[0])
        return Text

    def CursorOnBlankLine(self, Cursor):
        Cursor.select(QTextCursor.LineUnderCursor)
        LineText = Cursor.selectedText()
        return LineText == ""

    def VerticallyCenterCursor(self):
        CursorVerticalPosition = self.cursorRect().top()
        ViewportHeight = self.viewport().height()
        VerticalScrollBar = self.verticalScrollBar()
        VerticalScrollBar.setValue(VerticalScrollBar.value() + CursorVerticalPosition - (ViewportHeight / 2))

    def MakeCursorVisible(self):
        QTimer.singleShot(0, self.ensureCursorVisible)

    # Events
    def insertFromMimeData(self, QMimeData):
        self.insertPlainText(QMimeData.text())

    def wheelEvent(self, QWheelEvent):
        if QWheelEvent.modifiers() == QtCore.Qt.ControlModifier:
            QWheelEvent.accept()
        else:
            super().wheelEvent(QWheelEvent)

    def mouseDoubleClickEvent(self, QMouseEvent):
        Anchor = self.anchorAt(QMouseEvent.pos())
        if Anchor != "":
            if self.Notebook.StringIsValidIndexPath(Anchor):
                self.MainWindow.NotebookDisplayWidgetInst.SelectTreeItemFromIndexPathString(Anchor)
                QMouseEvent.accept()
            else:
                webbrowser.open(Anchor)
        else:
            super().mouseDoubleClickEvent(QMouseEvent)

    # Action Methods
    def Italics(self):
        if not self.ReadMode and self.hasFocus():
            self.SelectionSpanWrap("*", "*")

    def Bold(self):
        if not self.ReadMode and self.hasFocus():
            self.SelectionSpanWrap("**", "**")

    def Strikethrough(self):
        if not self.ReadMode and self.hasFocus():
            self.SelectionSpanWrap("~~", "~~")

    def CodeSpan(self):
        if not self.ReadMode and self.hasFocus():
            self.SelectionSpanWrap("`", "`")

    def Header(self, Level):
        if not self.ReadMode and self.hasFocus():
            self.SingleBlockPrefix(("#" * Level) + " ")

    def BulletList(self):
        if not self.ReadMode and self.hasFocus():
            self.MultipleBlockPrefix("* ")

    def NumberList(self):
        if not self.ReadMode and self.hasFocus():
            self.MultipleBlockPrefix("1. ")

    def Quote(self):
        if not self.ReadMode and self.hasFocus():
            self.MultipleBlockPrefix("> ")

    def CodeBlock(self):
        if not self.ReadMode and self.hasFocus():
            self.MultipleBlockWrap("```")

    def HorizontalRule(self):
        if not self.ReadMode and self.hasFocus():
            self.InsertOnBlankLine("***")

    def Footnote(self):
        if not self.ReadMode and self.hasFocus():
            FootnoteLabel, OK = QInputDialog.getText(self, "Add Footnote", "Enter a footnote label:")
            if OK:
                if FootnoteLabel == "":
                    self.MainWindow.DisplayMessageBox("Footnote labels cannot be blank.")
                else:
                    FootnoteSymbol = "[^" + FootnoteLabel + "]"
                    Cursor = self.textCursor()
                    Cursor.beginEditBlock()
                    self.insertPlainText(FootnoteSymbol)
                    if self.MainWindow.InlineFootnoteStyle:
                        Cursor.movePosition(QTextCursor.EndOfBlock)
                        NextLineBlank = self.NextLineBlank(Cursor)
                        while not NextLineBlank and not NextLineBlank is None:
                            Cursor.movePosition(QTextCursor.NextCharacter)
                            Cursor.movePosition(QTextCursor.EndOfBlock)
                            NextLineBlank = self.NextLineBlank(Cursor)
                    else:
                        Cursor.movePosition(QTextCursor.End)
                    Cursor.insertText(("\u2029" * 2) + FootnoteSymbol + ": ")
                    self.setTextCursor(Cursor)
                    self.MakeCursorVisible()
                    QTimer.singleShot(0, self.VerticallyCenterCursor)
                    Cursor.endEditBlock()

    def NextLineBlank(self, Cursor):
        LineData = self.GetLineData(CursorToCopy=Cursor)
        CurrentLineIndex = LineData[1]
        if CurrentLineIndex == len(LineData[0]) - 1:
            return None
        NextLine = LineData[0][CurrentLineIndex + 1]
        return NextLine == ""

    def InsertLinks(self):
        if not self.ReadMode and self.hasFocus():
            InsertLinksDialogInst = InsertLinksDialog(self.Notebook, self.MainWindow, self)
            if InsertLinksDialogInst.InsertAccepted:
                Cursor = self.textCursor()
                Cursor.beginEditBlock()
                if InsertLinksDialogInst.InsertIndexPath is not None:
                    self.SelectionSpanWrap("[", "](" + json.dumps(InsertLinksDialogInst.InsertIndexPath) + (" \"" + InsertLinksDialogInst.ToolTipText + "\"" if InsertLinksDialogInst.AddToolTip else "") + ")")
                elif InsertLinksDialogInst.InsertIndexPaths is not None and InsertLinksDialogInst.SubPageLinksSeparator is not None:
                    InsertString = ""
                    for SubPagePath in InsertLinksDialogInst.InsertIndexPaths:
                        InsertString += "[" + SubPagePath[0] + "](" + json.dumps(SubPagePath[1]) + ")" + InsertLinksDialogInst.SubPageLinksSeparator
                    InsertString = InsertString.rstrip()
                    self.InsertOnBlankLine(InsertString)
                    self.MakeCursorVisible()
                Cursor.endEditBlock()

    def InsertExternalLink(self):
        if not self.ReadMode and self.hasFocus():
            LinkString, OK = QInputDialog.getText(self, "Insert External Link", "Enter a link URL:")
            if OK:
                self.SelectionSpanWrap("[", "](" + LinkString + ")")

    def TextToLink(self):
        if not self.ReadMode and self.hasFocus():
            Cursor = self.textCursor()
            SearchText = Cursor.selectedText()
            if SearchText != "" and "\u2029" not in SearchText:
                SearchResults = self.Notebook.GetSearchResults(SearchText, ExactTitleOnly=True)
                SearchResultsLength = len(SearchResults["ResultsList"])
                if SearchResultsLength > 0:
                    if SearchResultsLength > 1:
                        self.MainWindow.DisplayMessageBox("Multiple pages found.  Use the full link dialog to insert a link.", Icon=QMessageBox.Warning)
                    else:
                        TopResultIndexPath = SearchResults["ResultsList"][0][1]
                        TopResultTitle = SearchResults["ResultsList"][0][0]
                        self.SelectionSpanWrap("[", "](" + json.dumps(TopResultIndexPath) + " \"" + TopResultTitle + "\"" + ")")
                else:
                    self.MainWindow.DisplayMessageBox("No pages with this title found.")

    def InsertTable(self):
        if not self.ReadMode and self.hasFocus():
            Cursor = self.textCursor()
            if self.CursorOnBlankLine(Cursor):
                TableDimensionsDialogInst = TableDimensionsDialog(self.MainWindow, self)
                if TableDimensionsDialogInst.ContinueTable:
                    InsertTableDialogInst = InsertTableDialog(TableDimensionsDialogInst.Rows, TableDimensionsDialogInst.Columns, self.MainWindow, self)
                    if InsertTableDialogInst.InsertTable:
                        self.InsertOnBlankLine(InsertTableDialogInst.TableString)
                        self.MakeCursorVisible()

    def InsertImage(self):
        if not self.ReadMode and self.hasFocus():
            if len(self.Notebook.Images) < 1:
                self.MainWindow.DisplayMessageBox("No images are attached to the notebook.\n\nUse the Image Manager in the Notebook menu to add images to the notebook.")
            else:
                InsertImageDialogInst = InsertImageDialog(self.Notebook, self.MainWindow)
                if InsertImageDialogInst.InsertAccepted:
                    self.insertPlainText("![](" + InsertImageDialogInst.ImageFileName + ")")
                    self.MakeCursorVisible()
                else:
                    self.MainWindow.FlashStatusBar("No image inserted.")

    def MoveLineUp(self):
        if not self.ReadMode and self.hasFocus():
            self.MoveLine(-1)

    def MoveLineDown(self):
        if not self.ReadMode and self.hasFocus():
            self.MoveLine(1)

    def DuplicateLines(self):
        if not self.ReadMode and self.hasFocus():
            LineData = self.GetLineData()
            CurrentLine = LineData[0][LineData[1]]
            LineData[0].insert(LineData[1] + 1, CurrentLine)
            Text = self.GetTextFromLineData(LineData)
            NewPosition = LineData[2] + len(CurrentLine) + 1
            self.setPlainText(Text)
            Cursor = self.textCursor()
            Cursor.setPosition(NewPosition)
            self.setTextCursor(Cursor)
            self.VerticallyCenterCursor()

    def DeleteLine(self):
        if not self.ReadMode and self.hasFocus():
            LineData = self.GetLineData()
            if len(LineData[0]) > 0:
                del LineData[0][LineData[1]]
                Text = self.GetTextFromLineData(LineData)
                self.setPlainText(Text)
                PositionOfLineStart = LineData[2] - LineData[3]
                if LineData[1] < len(LineData[0]):
                    NewPosition = PositionOfLineStart + len(LineData[0][LineData[1]])
                else:
                    NewPosition = PositionOfLineStart - 1
                NewPosition = max(0, NewPosition)
                Cursor = self.textCursor()
                Cursor.setPosition(NewPosition)
                self.setTextCursor(Cursor)
                self.VerticallyCenterCursor()


class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, TextWidget):
        super().__init__(TextWidget)

        # Store Parameters
        self.TextWidget = TextWidget

        # Create Formats
        self.CreateFormats()

        # Create Highlight Targets
        self.CreateHighlightTargets()

    def CreateFormats(self):
        # External Links
        self.ExternalLinksFormat = QTextCharFormat()
        self.ExternalLinksFormat.setBackground(QColor("darkBlue"))
        self.ExternalLinksFormat.setForeground(QColor("white"))

        # Internal Links
        self.InternalLinksFormat = QTextCharFormat()
        self.InternalLinksFormat.setBackground(QColor("darkCyan"))
        self.InternalLinksFormat.setForeground(QColor("white"))

        # Images
        self.ImagesFormat = QTextCharFormat()
        self.ImagesFormat.setBackground(QColor("darkRed"))
        self.ImagesFormat.setForeground(QColor("white"))

        # Footnotes
        self.FootnotesFormat = QTextCharFormat()
        self.FootnotesFormat.setBackground(QColor("darkGreen"))
        self.FootnotesFormat.setForeground(QColor("white"))

        # Search Highlight
        self.SearchHighlightFormat = QTextCharFormat()
        self.SearchHighlightFormat.setBackground(QColor("darkMagenta"))
        self.SearchHighlightFormat.setForeground(QColor("white"))

    def CreateHighlightTargets(self):
        # Highlight Targets
        self.HighlightTargets = []

        # Link-Type
        self.HighlightTargets.append({"RegEx": r"(!?)\[([^\[\]\n]*?)\]\((.+?)( \".+?\")?\)", "FormatCallable": self.GetLinksFormat})

        # Footnotes
        self.HighlightTargets.append({"RegEx": r"\[\^[^\]]+?\]", "FormatCallable": self.GetFootnotesFormat})

    def GetLinksFormat(self, Match):
        if Match.group(1) == "!":
            return self.ImagesFormat
        elif Match.group(2) != "" and Match.group(3).startswith("[") and Match.group(3).endswith("]"):
            return self.InternalLinksFormat
        elif Match.group(2) != "" and not (Match.group(3).startswith("[") and Match.group(3).endswith("]")):
            return self.ExternalLinksFormat
        else:
            return None

    def GetFootnotesFormat(self, Match):
        return self.FootnotesFormat

    def highlightBlock(self, Text):
        if self.TextWidget.MainWindow.HighlightSyntax and not self.TextWidget.ReadMode:
            for HighlightTarget in self.HighlightTargets:
                TargetIterator = re.finditer(HighlightTarget["RegEx"], Text)
                for Target in TargetIterator:
                    Format = HighlightTarget["FormatCallable"](Target)
                    if Format is not None:
                        self.setFormat(Target.start(), Target.end() - Target.start(), Format)
        if self.TextWidget.MainWindow.SearchWidgetInst.HighlightCheckBox.isChecked():
            SearchText = self.TextWidget.MainWindow.SearchWidgetInst.SearchTextLineEdit.text()
            if SearchText != "":
                MatchCase = self.TextWidget.MainWindow.SearchWidgetInst.MatchCaseCheckBox.isChecked()
                if MatchCase:
                    TargetIterator = re.finditer(re.escape(SearchText), Text)
                else:
                    TargetIterator = re.finditer(re.escape(SearchText), Text, re.IGNORECASE)
                for Target in TargetIterator:
                    self.setFormat(Target.start(), Target.end() - Target.start(), self.SearchHighlightFormat)
