from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QLineEdit, QGridLayout, QComboBox, QLabel, QPushButton, QSpinBox, QScrollArea, QFrame


class InsertTableDialog(QDialog):
    def __init__(self, Rows, Columns, MainWindow, Parent):
        # Store Parameters
        self.Rows = Rows
        self.Columns = Columns
        self.MainWindow = MainWindow
        self.Parent = Parent

        # QDialog Init
        super().__init__(parent=self.Parent)

        # Variables
        self.InsertTable = False
        self.TableString = ""
        self.Width = max(self.Parent.width() - 100, 100)
        self.Height = max(self.Parent.height() - 100, 100)

        # Header Alignment Symbols
        self.HeaderAlignmentSymbols = {}
        self.HeaderAlignmentSymbols["Left"] = ":--"
        self.HeaderAlignmentSymbols["Center"] = ":-:"
        self.HeaderAlignmentSymbols["Right"] = "--:"

        # Table Input Labels
        self.HeadersLabel = QLabel("Header(s):")
        self.HeaderAlignmentsLabel = QLabel("Header Alignment(s):")
        self.RowsLabel = QLabel("Row(s):")

        # Construct Table Input Widgets
        self.HeaderInputsList = []
        self.HeaderAlignmentsList = []
        for Column in range(self.Columns):
            self.HeaderInputsList.append(TableLineEdit(self, 0, Column))
            HeaderAlignmentComboBox = QComboBox()
            HeaderAlignmentComboBox.addItem("Left")
            HeaderAlignmentComboBox.addItem("Center")
            HeaderAlignmentComboBox.addItem("Right")
            HeaderAlignmentComboBox.setEditable(False)
            self.HeaderAlignmentsList.append(HeaderAlignmentComboBox)
        self.RowsList = []
        for Row in range(self.Rows):
            RowInputs = []
            for Column in range(self.Columns):
                RowInputs.append(TableLineEdit(self, Row + 1, Column))
            self.RowsList.append(RowInputs)

        # Buttons
        self.InsertButton = QPushButton("Insert")
        self.InsertButton.clicked.connect(self.Insert)
        self.CancelButton = QPushButton("Cancel")
        self.CancelButton.clicked.connect(self.Cancel)

        # Construct and set Layout
        self.TableLayout = QGridLayout()
        self.TableLayout.addWidget(self.HeadersLabel, 0, 0)
        self.TableLayout.addWidget(self.HeaderAlignmentsLabel, 1, 0)
        self.TableLayout.addWidget(self.RowsLabel, 2, 0)
        for HeaderInputIndex in range(len(self.HeaderInputsList)):
            self.TableLayout.addWidget(self.HeaderInputsList[HeaderInputIndex], 0, HeaderInputIndex + 1)
        for HeaderInputIndex in range(len(self.HeaderInputsList)):
            self.TableLayout.addWidget(self.HeaderAlignmentsList[HeaderInputIndex], 1, HeaderInputIndex + 1)
        for RowIndex in range(len(self.RowsList)):
            for ColumnIndex in range(self.Columns):
                self.TableLayout.addWidget(self.RowsList[RowIndex][ColumnIndex], RowIndex + 2, ColumnIndex + 1)
        self.ScrollFrame = QFrame()
        self.ScrollFrame.setLayout(self.TableLayout)
        self.ScrollArea = QScrollArea()
        self.ScrollArea.setWidget(self.ScrollFrame)
        self.Layout = QGridLayout()
        self.Layout.addWidget(self.ScrollArea, 0, 0)
        self.ButtonsLayout = QGridLayout()
        self.ButtonsLayout.addWidget(self.InsertButton, 0, 0)
        self.ButtonsLayout.addWidget(self.CancelButton, 0, 1)
        self.Layout.addLayout(self.ButtonsLayout, 1, 0)
        self.setLayout(self.Layout)

        # Set Window Title and Icon
        self.setWindowTitle(self.MainWindow.ScriptName)
        self.setWindowIcon(self.MainWindow.WindowIcon)

        # Window Resize
        self.Resize()

        # Execute Dialog
        self.exec_()

    def ConstructTableString(self):
        TableString = ""
        CurrentRow = "|"
        for HeaderInput in self.HeaderInputsList:
            CurrentRow += " " + HeaderInput.text() + " |"
        TableString += CurrentRow + "\n"
        CurrentRow = "|"
        for HeaderAlignment in self.HeaderAlignmentsList:
            CurrentRow += " " + self.HeaderAlignmentSymbols[HeaderAlignment.currentText()] + " |"
        TableString += CurrentRow + "\n"
        for RowIndex in range(len(self.RowsList)):
            CurrentRow = "|"
            for ColumnIndex in range(self.Columns):
                CurrentRow += " " + self.RowsList[RowIndex][ColumnIndex].text() + " |"
            TableString += CurrentRow + "\n"
        TableString = TableString.rstrip()
        return TableString

    def Insert(self):
        self.InsertTable = True
        self.TableString = self.ConstructTableString()
        self.close()

    def Cancel(self):
        self.close()

    def Resize(self):
        self.resize(self.Width, self.Height)


class TableDimensionsDialog(QDialog):
    def __init__(self, MainWindow, Parent):
        super().__init__(parent=Parent)

        # Store Parameters
        self.MainWindow = MainWindow

        # Variables
        self.Rows = 1
        self.Columns = 1
        self.ContinueTable = False

        # Labels
        self.RowsLabel = QLabel("Rows:")
        self.ColumnsLabel = QLabel("Columns:")

        # SpinBoxes
        self.RowsSpinBox = QSpinBox()
        self.RowsSpinBox.setMinimum(1)
        self.RowsSpinBox.valueChanged.connect(self.UpdateRows)
        self.ColumnsSpinBox = QSpinBox()
        self.ColumnsSpinBox.setMinimum(1)
        self.ColumnsSpinBox.valueChanged.connect(self.UpdateColumns)

        # Buttons
        self.ContinueButton = QPushButton("Continue")
        self.ContinueButton.clicked.connect(self.Continue)
        self.CancelButton = QPushButton("Cancel")
        self.CancelButton.clicked.connect(self.Cancel)

        # Set Layout
        self.Layout = QGridLayout()
        self.Layout.addWidget(self.RowsLabel, 0, 0)
        self.Layout.addWidget(self.ColumnsLabel, 1, 0)
        self.Layout.addWidget(self.RowsSpinBox, 0, 1)
        self.Layout.addWidget(self.ColumnsSpinBox, 1, 1)
        self.ButtonsLayout = QGridLayout()
        self.ButtonsLayout.addWidget(self.ContinueButton, 0, 0)
        self.ButtonsLayout.addWidget(self.CancelButton, 0, 1)
        self.Layout.addLayout(self.ButtonsLayout, 2, 0, 1, 2)
        self.setLayout(self.Layout)

        # Set Window Title and Icon
        self.setWindowTitle(self.MainWindow.ScriptName)
        self.setWindowIcon(self.MainWindow.WindowIcon)

        # Execute Dialog
        self.exec_()

    def UpdateRows(self, NewValue):
        self.Rows = NewValue

    def UpdateColumns(self, NewValue):
        self.Columns = NewValue

    def Continue(self):
        self.ContinueTable = True
        self.close()

    def Cancel(self):
        self.close()


class TableLineEdit(QLineEdit):
    def __init__(self, Dialog, Row, Column):
        # QLineEdit Init
        super().__init__()

        # Store Parameters
        self.Dialog = Dialog
        self.Row = Row
        self.Column = Column

    def keyPressEvent(self, QKeyEvent):
        KeyPressed = QKeyEvent.key()
        if KeyPressed == QtCore.Qt.Key_Up or KeyPressed == QtCore.Qt.Key_Down:
            if self.Row > 0:
                AdjustedRow = self.Row + 1
            else:
                AdjustedRow = self.Row
            AdjustedColumn = self.Column + 1
            if KeyPressed == QtCore.Qt.Key_Up:
                if AdjustedRow == 2:
                    NextItemRow = 0
                else:
                    NextItemRow = AdjustedRow - 1
            else:
                if AdjustedRow == 0:
                    NextItemRow = 2
                else:
                    NextItemRow = AdjustedRow + 1
            NextItem = self.Dialog.TableLayout.itemAtPosition(NextItemRow, AdjustedColumn)
            if NextItem is not None:
                NextWidget = NextItem.widget()
                NextWidget.setFocus()
                NextWidget.selectAll()
        else:
            super().keyPressEvent(QKeyEvent)
