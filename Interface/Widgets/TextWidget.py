import json
import re
import webbrowser

import mistune
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor, QSyntaxHighlighter, QTextCursor, QTextCharFormat
from PyQt5.QtWidgets import QTextEdit, QInputDialog, QMessageBox, QAction

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
                self.verticalScrollBar().setValue(int(self.MainWindow.AutoScrollQueue["TargetScrollPosition"]))
                self.MainWindow.AutoScrollQueue = None

    # Internal Text and Cursor Methods
    def SelectionSpanWrap(self, WrapPrefix, WrapSuffix):
        Cursor = self.textCursor()
        TextToWrap = Cursor.selectedText()
        if "\u2029" in TextToWrap:
            return
        Cursor.beginEditBlock()
        WrappedText = f"{WrapPrefix}{TextToWrap}{WrapSuffix}"
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
                    PrefixedText += f"{str(CurrentPrefixInt)}. {Block}\u2029"
                    CurrentPrefixInt += 1
                else:
                    PrefixedText += f"{Block}\u2029"
        else:
            for Block in Blocks:
                PrefixedText += f"{Prefix if Block != "" else ""}{Block}\u2029"

        Cursor.beginEditBlock()
        Cursor.insertText(PrefixedText[:-1])
        self.MakeCursorVisible()
        Cursor.endEditBlock()

    def MultipleBlockWrap(self, WrapSymbol):
        Cursor = self.textCursor()
        self.SelectBlocks(Cursor)
        SelectedBlocksText = Cursor.selectedText()
        WrappedText = f"{WrapSymbol}\u2029{SelectedBlocksText}\u2029{WrapSymbol}"

        Cursor.beginEditBlock()
        Cursor.insertText(WrappedText)
        for Character in range(len(WrapSymbol) + 1):
            self.moveCursor(QTextCursor.Left)
        self.MakeCursorVisible()
        Cursor.endEditBlock()

    def MultipleBlockStripPrefix(self, Prefix):
        Cursor = self.textCursor()
        self.SelectBlocks(Cursor)
        Blocks = Cursor.selectedText().split("\u2029")
        StrippedText = ""

        for Block in Blocks:
            StrippedText += (f"{Block[len(Prefix):]}\u2029") if Block.startswith(Prefix) else (f"{Block}\u2029")

        Cursor.beginEditBlock()
        Cursor.insertText(StrippedText[:-1])
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
        VerticalScrollBar.setValue(int(VerticalScrollBar.value() + CursorVerticalPosition - (ViewportHeight / 2)))

    def MakeCursorVisible(self):
        QTimer.singleShot(0, self.ensureCursorVisible)

    # Events
    def contextMenuEvent(self, QContextMenuEvent):
        ContextMenu = self.createStandardContextMenu()
        ContextMenu.addSeparator()
        ContextMenu.addAction(self.MainWindow.CopyLinkToCurrentPageAction)
        ContextMenu.addAction(self.MainWindow.CopyIndexPathToCurrentPageAction)
        ContextMenu.addSeparator()
        ContextMenu.addAction(self.MainWindow.PopOutPageAction)
        Anchor = self.anchorAt(QContextMenuEvent.pos())
        if Anchor != "":
            if self.Notebook.StringIsValidIndexPath(Anchor):
                IndexPath = json.loads(Anchor)
                ContextMenu.addAction(self.MainWindow.PopOutPageIcon, "Pop Out Linked Page", lambda: self.MainWindow.PopOutPage(IndexPath))
        ContextMenu.exec_(self.mapToGlobal(QContextMenuEvent.pos()))

    def insertFromMimeData(self, QMimeData):
        self.insertPlainText(QMimeData.text())

    def wheelEvent(self, QWheelEvent):
        if QWheelEvent.modifiers() == Qt.ControlModifier:
            QWheelEvent.accept()
        else:
            super().wheelEvent(QWheelEvent)

    def mouseDoubleClickEvent(self, QMouseEvent):
        Anchor = self.anchorAt(QMouseEvent.pos())
        if Anchor != "" and QMouseEvent.button() == Qt.LeftButton:
            self.NavigateToLink(Anchor, QMouseEvent) if not self.MainWindow.SwapLeftAndMiddleClickForLinks else self.OpenLinkAsPopup(Anchor, QMouseEvent)
        else:
            super().mouseDoubleClickEvent(QMouseEvent)

    def mouseReleaseEvent(self, QMouseEvent):
        Anchor = self.anchorAt(QMouseEvent.pos())
        if Anchor != "" and QMouseEvent.button() == Qt.MiddleButton:
            self.OpenLinkAsPopup(Anchor, QMouseEvent) if not self.MainWindow.SwapLeftAndMiddleClickForLinks else self.NavigateToLink(Anchor, QMouseEvent)
        else:
            super().mouseReleaseEvent(QMouseEvent)

    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.ForwardButton:
            self.MainWindow.ForwardAction.trigger()
            QMouseEvent.accept()
        elif QMouseEvent.button() == Qt.BackButton:
            self.MainWindow.BackAction.trigger()
            QMouseEvent.accept()
        else:
            super().mousePressEvent(QMouseEvent)

    def mouseMoveEvent(self, QMouseEvent):
        Anchor = self.anchorAt(QMouseEvent.pos())
        if Anchor != "":
            self.viewport().setCursor(Qt.PointingHandCursor)
        else:
            self.viewport().setCursor(Qt.IBeamCursor)
        return super().mouseMoveEvent(QMouseEvent)

    # Link Methods
    def NavigateToLink(self, Anchor, QMouseEvent):
        if self.Notebook.StringIsValidIndexPath(Anchor):
            self.MainWindow.NotebookDisplayWidgetInst.SelectTreeItemFromIndexPathString(Anchor)
            QMouseEvent.accept()
        else:
            if Anchor.startswith("[0,"):
                self.MainWindow.DisplayMessageBox("Linked page not found.")
                QMouseEvent.accept()
            else:
                webbrowser.open(Anchor)
                QMouseEvent.accept()

    def OpenLinkAsPopup(self, Anchor, QMouseEvent):
        if self.Notebook.StringIsValidIndexPath(Anchor):
            IndexPath = json.loads(Anchor)
            self.MainWindow.PopOutPage(IndexPath)
            QMouseEvent.accept()
        else:
            if Anchor.startswith("[0,"):
                self.MainWindow.DisplayMessageBox("Linked page not found.")
                QMouseEvent.accept()
            else:
                webbrowser.open(Anchor)
                QMouseEvent.accept()

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
            self.SingleBlockPrefix(f"{"#" * Level} ")

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

    def Indent(self):
        if not self.ReadMode and self.hasFocus():
            self.MultipleBlockPrefix("  ")

    def Outdent(self):
        if not self.ReadMode and self.hasFocus():
            self.MultipleBlockStripPrefix("  ")

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
                    FootnoteSymbol = f"[^{FootnoteLabel}]"
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
                    Cursor.insertText(f"\u2029\u2029{FootnoteSymbol}: ")
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
                    IndexPath = json.dumps(InsertLinksDialogInst.InsertIndexPath)
                    ToolTipText = f" \"{InsertLinksDialogInst.ToolTipText}\"" if InsertLinksDialogInst.AddToolTip else ""
                    self.SelectionSpanWrap("[", f"]({IndexPath}{ToolTipText})")
                elif InsertLinksDialogInst.InsertIndexPaths is not None and InsertLinksDialogInst.SubPageLinksSeparator is not None:
                    InsertString = ""
                    for SubPagePath in InsertLinksDialogInst.InsertIndexPaths:
                        SubPageTitle = SubPagePath[0]
                        SubPageIndexPath = json.dumps(SubPagePath[1])
                        SubPageToolTipText = f" \"{SubPageTitle}\"" if InsertLinksDialogInst.AddToolTip else ""
                        InsertString += f"[{SubPageTitle}]({SubPageIndexPath}{SubPageToolTipText}){InsertLinksDialogInst.SubPageLinksSeparator}"
                    InsertString = InsertString.rstrip()
                    self.InsertOnBlankLine(InsertString)
                    self.MakeCursorVisible()
                Cursor.endEditBlock()

    def InsertExternalLink(self):
        if not self.ReadMode and self.hasFocus():
            LinkString, OK = QInputDialog.getText(self, "Insert External Link", "Enter a link URL:")
            if OK:
                self.SelectionSpanWrap("[", f"]({LinkString})")

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
                        self.SelectionSpanWrap("[", f"]({json.dumps(TopResultIndexPath)} \"{TopResultTitle}\")")
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
                    self.insertPlainText(f"![]({InsertImageDialogInst.ImageFileName})")
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

    def SortLines(self):
        if not self.ReadMode and self.hasFocus():
            Cursor = self.textCursor()
            self.SelectBlocks(Cursor)
            Blocks = Cursor.selectedText().split("\u2029")
            if len(Blocks) > 1:
                Blocks.sort(key=str.casefold)
                SortedLines = "\u2029".join(Blocks)
                Cursor.beginEditBlock()
                Cursor.insertText(SortedLines)
                self.MakeCursorVisible()
                Cursor.endEditBlock()


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
        # Headers
        self.HeaderFormat = QTextCharFormat()
        self.HeaderFormat.setBackground(QColor("seagreen"))
        self.HeaderFormat.setForeground(QColor("white"))

        # External Links
        self.ExternalLinksFormat = QTextCharFormat()
        self.ExternalLinksFormat.setBackground(QColor("darkSlateBlue"))
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
        self.FootnotesFormat.setBackground(QColor("darkGoldenrod"))
        self.FootnotesFormat.setForeground(QColor("white"))

        # Text Highlight
        self.TextHighlightFormat = QTextCharFormat()
        self.TextHighlightFormat.setBackground(QColor("darkOrange"))
        self.TextHighlightFormat.setForeground(QColor("white"))

        # Search Highlight
        self.SearchHighlightFormat = QTextCharFormat()
        self.SearchHighlightFormat.setBackground(QColor("darkMagenta"))
        self.SearchHighlightFormat.setForeground(QColor("white"))

    def CreateHighlightTargets(self):
        # Highlight Targets
        self.HighlightTargets = []

        # Headers
        self.HighlightTargets.append({"RegEx": r"(?m)^#{1,6}(?!#) (.+)", "FormatCallable": self.GetHeaderFormat})

        # Link-Type
        self.HighlightTargets.append({"RegEx": r"(!?)\[([^\[\]\n]*?)\]\((.+?)( \".+?\")?\)", "FormatCallable": self.GetLinksFormat})

        # Footnotes
        self.HighlightTargets.append({"RegEx": r"\[\^[^\]]+?\]", "FormatCallable": self.GetFootnotesFormat})

    def GetHeaderFormat(self, Match):
        return self.HeaderFormat

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
        for HighlightText in self.TextWidget.MainWindow.TextToHighlight:
            if self.TextWidget.MainWindow.TextToHighlightMatchCase:
                TargetIterator = re.finditer(re.escape(HighlightText), Text)
            else:
                TargetIterator = re.finditer(re.escape(HighlightText), Text, re.IGNORECASE)
            for Target in TargetIterator:
                self.setFormat(Target.start(), Target.end() - Target.start(), self.TextHighlightFormat)
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
