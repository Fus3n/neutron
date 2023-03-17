from typing import TYPE_CHECKING

from pathlib import Path
from PyQt5.Qsci import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from lexer import PyCustomLexer
from autocompleter import AutoCompleter

if TYPE_CHECKING:
    from main import MainWindow


class Editor(QsciScintilla):

    def __init__(self, main_window, parent=None, path: Path = None,  python_file=True, env=None):
        super(Editor, self).__init__(parent)
        # UPDATED EP 9
        self.first_launch = True # variable to keep track of if it's first launch
        self.main_window: MainWindow = main_window

        self.path = path
        self.full_path = self.path.absolute()
        self.is_python_file = python_file
        self.venv = env
        self._current_file_changed = False        
    
        # EDITOR
        self.cursorPositionChanged.connect(self.cursorPositionChangedCustom)
        # UPDATED EP 9
        self.textChanged.connect(self.textChangedCustom)
 
        # encoding       
        self.setUtf8(True)
        # font
        self.font = QFont("Consolas", 14)
        self.setFont(self.font)
        
        # brace mactching
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)

        # indentation
        self.setTabWidth(4)
        self.setIndentationGuides(True)
        self.setIndentationsUseTabs(False) # don't use tabs, otherwise jedi can't work
        self.setAutoIndent(True)

        # autocomplete
        self.setAutoCompletionSource(QsciScintilla.AcsAPIs)
        self.setAutoCompletionThreshold(1)
        self.setAutoCompletionCaseSensitivity(False)
        self.setAutoCompletionUseSingle(QsciScintilla.AcusNever)

        self.setCallTipsStyle(QsciScintilla.CallTipsNoContext)
        # Set the number of calltips that will be displayed at one time.
        # 0 shows all applicable call tips.
        self.setCallTipsVisible(0)
        # This selects the position at which the call tip rectangle will appear.
        # If it is not possible to show the call tip rectangle at the selected position
        # because it would be displayed outside the bounds of the document, it will be
        # displayed where it is possible.
        self.setCallTipsPosition(QsciScintilla.CallTipsAboveText)
        # Select the various highlight colors
        # Background
        self.setCallTipsBackgroundColor(QColor(0xff, 0xff, 0xff, 0xff))
        # Text
        self.setCallTipsForegroundColor(QColor(0x50, 0x50, 0x50, 0xff))
        # Current argument text
        self.setCallTipsHighlightColor(QColor(0xff, 0x00, 0x00, 0xff))

        # caret
        self.setCaretForegroundColor(QColor("#dedcdc"))
        self.setCaretLineVisible(True)
        self.setCaretWidth(2)
        self.setCaretLineBackgroundColor(QColor("#2c313c"))

        # bracket matching colors
        self.setMatchedBraceBackgroundColor(QColor("#c678dd"))
        self.setMatchedBraceForegroundColor(QColor("#F2E3E3"))

        # EOL
        self.setEolMode(QsciScintilla.EolMode.EolWindows)
        self.setEolVisibility(False)

        if self.is_python_file:
            # lexer
            self.pylexer = PyCustomLexer(self)
            # QsciLexerPython
            self.pylexer.setDefaultFont(self.font)

            # Api AUTOCOMPLETION
            # API
            self.__api = QsciAPIs(self.pylexer)
            # autocompletion_image = QPixmap("./src/icons/close-icon.svg")
            # self.registerImage(1, autocompletion_image)

            self.auto_completer = AutoCompleter(self.full_path, self.__api)
            self.auto_completer.finished.connect(self.loaded_autocomp)
            
            self.setLexer(self.pylexer)
        else:
            # self.lexer = QsciLexer()
            self.setPaper(QColor("#282c34"))
            self.setColor(QColor("#abb2bf"))
            # self.lexer.setDefaultColor("#abb2bf")
            # self.lexer.setDefaultFont(QFont("Consolas", 14))
            # self.setLexer(self.lexer)

        # style
        self.setIndentationGuidesBackgroundColor(QColor("#dedcdc"))
        self.setIndentationGuidesForegroundColor(QColor("#dedcdc"))
        self.SendScintilla(self.SCI_STYLESETBACK, self.STYLE_DEFAULT, QColor("#282c34"))
        self.setEdgeColor(QColor("#2c313c"))
        self.setEdgeMode(QsciScintilla.EdgeLine)
        self.setWhitespaceBackgroundColor(QColor("#2c313c"))
        self.setWhitespaceForegroundColor(QColor("#ffffff"))
        self.setContentsMargins(0, 0, 0, 0)
        self.setSelectionBackgroundColor(QColor("#333a46"))

        # markers
        # text_edit.markerDefine(QsciScintilla.Circle, 1)
        # text_edit.setMarkerBackgroundColor(QColor("#FF0000"), 1)
        # text_edit.setMarkerForegroundColor(QColor("#FFFFFF"), 1)

        # margin 0 = Line nr margin
        self.setMarginType(0, QsciScintilla.NumberMargin)
        self.setMarginWidth(0, "0000")
        self.setMarginsForegroundColor(QColor("#ff888888"))
        self.setMarginsBackgroundColor(QColor("#282c34"))
        self.setMarginsFont(self.font)

        # folding
        # self.setMarginType(1, QsciScintilla)
        # self.setMarginWidth(1, "000")
        # self.setMarginMarkerMask(1, 0b1111)
        # self.setMarginSensitivity(1, True)
        self.setFolding(QsciScintilla.BoxedFoldStyle, 1)
        self.setFoldMarginColors(QColor("#2c313c"), QColor("#2c313c"))

        # margin 1 = Symbol margin
        # editor.setMarginType(1, QsciScintilla.SymbolMargin)
        # editor.setMarginWidth(1, "000")
        # editor.setMarginMarkerMask(1, 0b1111)
        # editor.setMarginSensitivity(1, True)

        # debug_circle = QImage("./src/imgs/Basic_red_dot.png").scaled(QSize(13, 13))
        # # smooth circle
        # debug_circle.setDevicePixelRatio(self.devicePixelRatioF())
        # editor.markerDefine(debug_circle, 1)
        # editor.marginClickEolWindowsed.connect(self.handle_margin)

        self.indicatorDefine(QsciScintilla.SquigglePixmapIndicator, 0)

    # UPDATED EP 9
    @property
    def current_file_changed(self):
        return self._current_file_changed
    
    # UPDATED EP 9
    @current_file_changed.setter
    def current_file_changed(self, value: bool):
        curr_indx = self.main_window.tab_view.currentIndex()
        if value:
            self.main_window.tab_view.setTabText(curr_indx, "*" + self.path.name)
            self.main_window.setWindowTitle(f"*{self.path.name} - {self.main_window.app_name}")
        else:
            if self.main_window.tab_view.tabText(curr_indx).startswith("*"):
                self.main_window.tab_view.setTabText(
                    curr_indx, 
                    self.main_window.tab_view.tabText(curr_indx)[1:]
                )
                self.main_window.setWindowTitle(self.main_window.windowTitle()[1:])

        self._current_file_changed = value

    @property
    def autocomplete(self):
        return self.complete_flag
    
    @autocomplete.setter
    def set_autocomplete(self, value):
        self.complete_flag = value

    def toggle_comment(self, text: str) -> str:
        lines = text.split('\n')
        toggled_lines = []
        for line in lines:
            if line.startswith('#'):
                # remove the comment symbol from the line
                toggled_lines.append(line[1:].lstrip())
            else:
                # add the comment symbol to the line
                toggled_lines.append('# ' + line)
        return '\n'.join(toggled_lines)

    def keyPressEvent(self, e: QKeyEvent) -> None:
        if e.modifiers() == Qt.ControlModifier and e.key() == Qt.Key_Space:
            if self.is_python_file:
                pos = self.getCursorPosition()
                self.auto_completer.get_completion(pos[0]+1, pos[1], self.text())
                self.autoCompleteFromAPIs()
                return

        # UPDATED EP 9
        if e.modifiers() == Qt.ControlModifier and e.key() == Qt.Key_X: # CUT SHORTCUT
            if not self.hasSelectedText():
                line, index = self.getCursorPosition()
                self.setSelection(line, 0, line, self.lineLength(line))
                self.cut()
                return 
            
        # UPDATED EP 9
        if e.modifiers() == Qt.ControlModifier and e.text() == "/": # COMMENT SHORTCUT
            if self.hasSelectedText():
                start, startl, end, endl = self.getSelection()
                self.setSelection(start, 0, end, self.lineLength(end)-1)
                self.replaceSelectedText(self.toggle_comment(self.selectedText()))
                self.setSelection(start, startl, end, endl)
            else:
                line, idx = self.getCursorPosition()
                self.setSelection(line, 0, line, self.lineLength(line)-1)
                self.replaceSelectedText(self.toggle_comment(self.selectedText()))
                self.setSelection(-1, -1, -1, -1) # reset selection
            
            return 

        return super().keyPressEvent(e)

    def cursorPositionChangedCustom(self, line: int, index: int) -> None:
        if self.is_python_file:
            self.auto_completer.get_completion(line+1, index, self.text())

    def loaded_autocomp(self):
        pass

    # UPDATED EP 9
    def textChangedCustom(self) -> None:
        if not self.current_file_changed and not self.first_launch:
            self.current_file_changed = True
        if self.first_launch:
            self.first_launch = False
