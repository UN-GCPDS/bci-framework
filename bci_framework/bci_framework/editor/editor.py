from PySide2.QtWidgets import QTextEdit, QCompleter
from PySide2.QtGui import QTextOption, QWheelEvent, QKeySequence, QTextCursor
from PySide2.QtCore import Qt, QPoint
# from PySide2 import QtGui

from .highlighters import PythonHighlighter, CSSHighlighter

import os


########################################################################
class BCIEditor(QTextEdit):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, linenumber=None, extension='.py', *args, **kwargs):
        """Constructor"""

        super().__init__(*args, **kwargs)

        self.set_options()

        self.linenumber = linenumber

        if 'light' in os.environ.get('QTMATERIAL_THEME'):
            font_color = 'black'
        else:
            font_color = 'white'

        # editor = QTextEdit()
        self.setStyleSheet(f"""
        QTextEdit {{
        background-color: {os.environ.get('QTMATERIAL_SECONDARYDARKCOLOR')};
        color: {font_color};
        height: 18px;
        font-weight: normal;
        font-family: 'DejaVu Sans Mono';
        font-size: 15px;
        line-height: 15px;
        border: 1px solid {os.environ.get('QTMATERIAL_SECONDARYDARKCOLOR')};
        border-radius: 4px;
        height: 18px;
        padding: 0px;
        padding-top: 8px;
        }}
        """)

        if extension == '.py':
            PythonHighlighter(self.document())
        elif extension == '.css':
            CSSHighlighter(self.document())

        self.connect_()

        self.completer = None

    # ----------------------------------------------------------------------

    def connect_(self):
        """"""
        if self.linenumber:
            self.textChanged.connect(self.update_linenumber)

    # ----------------------------------------------------------------------
    def wheelEvent(self, evt):
        """"""
        # self.last_wheel_evt = QWheelEvent(evt.pos(), evt.delta(), evt.buttons(), evt.modifiers())
        # print(evt.pos(), evt.delta(), evt.buttons(), evt.modifiers())
        if self.linenumber:
            self.linenumber.wheelEvent(evt)
        return super().wheelEvent(evt)

    # ----------------------------------------------------------------------
    def update_linenumber(self):
        """"""
        lines = len(self.toPlainText().split('\n'))
        lines_ln = len(self.linenumber.toPlainText().split('\n'))

        if lines != lines_ln:
            content = [f'{l}' for l in range(1, lines + 1)]
            self.linenumber.setHtml(
                f'<p style="text-align: right; line-height: 18px">{"<br>".join(content)}</p>')
        self.linenumber.verticalScrollBar().setValue(self.verticalScrollBar().value())

    # ----------------------------------------------------------------------
    def set_options(self):
        """"""
        document = self.document()
        option = QTextOption()

        # option.setFlags(QTextOption.ShowTabsAndSpaces)

        document.setDefaultTextOption(option)
        self.setAcceptRichText(False)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

    # ----------------------------------------------------------------------
    def keyPressEvent(self, event):
        """"""
        completionPrefix = self.textUnderCursor()
        if self.completer and len(completionPrefix) < 3 and self.completer.popup().isVisible():
            self.completer.popup().hide()

        # Replace Tabs with Spaces
        # if event.key() in [Qt.Key_Tab, Qt.Key_Enter, Qt.Key_Enter - 1]:

            # if self.completer and self.completer.popup().isVisible():
                # self.completer.insertText.emit(self.completer.last_highlighted)
                # self.completer.popup().hide()
            # else:
                # tc = self.textCursor()
                # tc.insertText(" " * 4)
            # return

        if event.key() in [Qt.Key_Tab, Qt.Key_Enter, Qt.Key_Enter - 1]:
            if self.completer and self.completer.popup().isVisible():
                self.completer.insertText.emit(self.completer.last_highlighted)
                self.completer.popup().hide()
                return

        if event.key() == Qt.Key_Tab:
            tc = self.textCursor()
            tc.insertText(" " * 4)
            return

        # Toggle comment
        if (event.key() == Qt.Key_Period) and bool(event.modifiers() & Qt.ControlModifier):
            tc = self.textCursor()
            # pos = tc.position()
            tc.select(tc.LineUnderCursor)
            line = tc.selectedText()

            if line.strip()[0] == '#':
                self._remove_symbol('# ')
            else:
                self._insert_symbol('# ')

        # Comment
        if (event.key() == Qt.Key_Slash) and bool(event.modifiers() & Qt.ControlModifier):
            return self._insert_symbol('# ')

        # Uncomment
        if (event.key() == Qt.Key_Question) and bool(event.modifiers() & Qt.ControlModifier):
            return self._remove_symbol('# ')

        # Unindent
        if (event.key() == Qt.Key_Less) and bool(event.modifiers() & Qt.ControlModifier):
            return self._remove_symbol('    ')

        # Indent
        if (event.key() == Qt.Key_Greater) and bool(event.modifiers() & Qt.ControlModifier):
            return self._insert_symbol('    ')

        # On enter
        if event.key() in [Qt.Key_Enter, Qt.Key_Enter - 1]:
            return self._on_enter()

        # On back space
        if event.key() == Qt.Key_Backspace:
            return self._on_back_space(event)

        super().keyPressEvent(event)

        # if event.key() in (
                # Qt.Key_Enter,
                # Qt.Key_Return,
                # Qt.Key_Escape,
                # Qt.Key_Tab,
                # Qt.Key_Backtab, ) or event.modifiers() in (Qt.ControlModifier, ):

                # return
        if self.completer and event.text():
            completionPrefix = self.textUnderCursor()
            if len(completionPrefix) >= 3:
                self.show_completer(completionPrefix)
            elif self.completer.popup().isVisible():
                self.completer.popup().hide()

    # ----------------------------------------------------------------------
    def _on_back_space(self, event):
        """"""
        tc = self.textCursor()

        if tc.selectedText():
            return super().keyPressEvent(event)

        pos = tc.position()
        tc.movePosition(tc.StartOfLine, tc.KeepAnchor)
        previous = tc.selectedText()

        if previous[-4:] == '    ':
            if d := len(previous) % 4:
                previous = previous[:-d]
            else:
                previous = previous[:-4]
            tc.insertText(previous)
            return
        # elif not previous:
            # return super().keyPressEvent(event)
        else:
            # tc.insertText(previous[:-1])
            return super().keyPressEvent(event)

    # ----------------------------------------------------------------------

    def _on_enter(self):
        """"""
        tc = self.textCursor()
        pos = tc.position()
        tc.select(tc.LineUnderCursor)
        line = tc.selectedText()

        if line.isspace() or line == "":
            len_s = len(line)
        else:
            normal = line.replace(" ", "")
            len_s = line.find(normal[0])

        if line.strip().endswith(':'):
            len_s += 4

        tc.setPosition(pos)
        tc.insertText("\n" + " " * len_s)
        return

    # ----------------------------------------------------------------------
    def _remove_symbol(self, char='#'):
        """"""
        tc = self.textCursor()

        if tc.selectedText():
            start = tc.selectionStart()
            end = tc.selectionEnd()

            tc.setPosition(start, tc.MoveAnchor)
            tc.movePosition(tc.StartOfLine, tc.MoveAnchor)
            start = tc.position()

            tc.setPosition(end, tc.MoveAnchor)
            tc.movePosition(tc.EndOfLine, tc.MoveAnchor)
            end = tc.position()

            tc.setPosition(start, tc.MoveAnchor)
            tc.setPosition(end, tc.KeepAnchor)
            selected = tc.selectedText()
            tc.removeSelectedText()

            uncommented = []
            for line in selected.split('\u2029'):
                if line.strip():
                    start_ = line.find(line.replace(' ', '')[0])

                    if char.isspace():
                        uncommented.append(line.replace(f'{char}', '', 1))
                    else:
                        if line[start_:start_ + len(char)] == f'{char}':
                            uncommented.append(
                                line.replace(f'{char}', '', 1))
                        else:
                            tc.insertText(selected)
                            return

                    end -= len(char)
                else:
                    uncommented.append(line)

            if uncommented:
                tc.insertText('\u2029'.join(uncommented))
                tc.setPosition(start, tc.MoveAnchor)
                tc.setPosition(end, tc.KeepAnchor)
                self.setTextCursor(tc)
            else:
                tc.insertText(selected)

        else:
            tc.select(tc.LineUnderCursor)
            if line := tc.selectedText():
                tc.removeSelectedText()

                if char.isspace():
                    tc.insertText(line.replace(f'{char}', '', 1))
                else:
                    start = line.find(line.replace(' ', '')[0])
                    if line[start:start + len(char)] == f'{char}':
                        tc.insertText(line.replace(f'{char}', '', 1))
                    else:
                        tc.insertText(line)

    # ----------------------------------------------------------------------
    def _insert_symbol(self, char='#'):
        """"""
        tc = self.textCursor()

        if tc.selectedText():
            start = tc.selectionStart()
            end = tc.selectionEnd()

            tc.setPosition(start, tc.MoveAnchor)
            tc.movePosition(tc.StartOfLine, tc.MoveAnchor)
            start = tc.position()

            tc.setPosition(end, tc.MoveAnchor)
            tc.movePosition(tc.EndOfLine, tc.MoveAnchor)
            end = tc.position()

            tc.setPosition(start, tc.MoveAnchor)
            tc.setPosition(end, tc.KeepAnchor)
            selected = tc.selectedText()
            tc.removeSelectedText()

            commented = []
            for line in selected.split('\u2029'):
                if line.strip():
                    start_ = line.find(line.replace(' ', '')[0])
                    commented.append(
                        " " * start_ + f'{char}' + line[start_:])
                    end += len(char)
                else:
                    commented.append(line)
            tc.insertText('\u2029'.join(commented))
            tc.setPosition(start, tc.MoveAnchor)
            tc.setPosition(end, tc.KeepAnchor)
            self.setTextCursor(tc)

        else:
            tc.select(tc.LineUnderCursor)
            if line := tc.selectedText():
                tc.removeSelectedText()
                start = line.find(line.replace(' ', '')[0])
                tc.insertText(" " * start + f'{char}' + line[start:])

    # ----------------------------------------------------------------------

    def setCompleter(self, completer):
        """"""
        if self.completer:
            self.disconnect(self.completer)
        if not completer:
            return

        completer.setWidget(self)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer = completer
       # self.connect(self.completer,
           # QtCore.SIGNAL("activated(const QString&)"), self.insertCompletion)
        self.completer.insertText.connect(self.insertCompletion)

    # ----------------------------------------------------------------------
    def insertCompletion(self, completion):
        """"""
        tc = self.textCursor()

        self.textUnderCursor(tc)
        tc.removeSelectedText()

        pos = tc.position()  # len(self.completer.completionPrefix())

        if completion in self.completer.snippets:
            completion = self.completer.snippets[completion]

        # extra = (len(completion) - len(self.completer.completionPrefix()))
        extra = completion  # [-extra:]

        text_position = extra.find("[!]")
        extra = extra.replace("[!]", "")

        position_in_line = tc.positionInBlock()
        extra = extra.replace("\n", "\n" + " " * position_in_line)

        # tc.movePosition(QTextCursor.Left)
        # tc.movePosition(QTextCursor.EndOfWord)
        tc.insertText(extra)

        if text_position > 0:
            tc.setPosition(pos + text_position + (4 * extra[:text_position].count('\n')))

        self.setTextCursor(tc)

    # ----------------------------------------------------------------------

    def textUnderCursor(self, tc=None):
        """"""

        if tc is None:
            tc = self.textCursor()

        # word like: cdc|
        tc.movePosition(tc.WordLeft, tc.KeepAnchor)

        # word like: cdc.|
        if tc.selectedText().startswith("."):
            tc.movePosition(tc.WordLeft, tc.KeepAnchor)

        # word like: cdc.pri|
        tc.movePosition(tc.WordLeft, tc.KeepAnchor)
        if tc.selectedText().startswith("."):
            tc.movePosition(tc.WordLeft, tc.KeepAnchor)
        else:
            tc.movePosition(tc.WordRight, tc.KeepAnchor)

        # tc.select(QTextCursor.WordUnderCursor)
        completionPrefix = tc.selectedText()

        if completionPrefix.endswith('.') and completionPrefix.count('.') > 1:
            index = completionPrefix.rfind('.', 0, completionPrefix.rfind('.'))
            completionPrefix = completionPrefix[index + 1:]
            for _ in range(tc.selectedText().count('.') - 1):
                tc.movePosition(tc.WordRight, tc.KeepAnchor)
                tc.movePosition(tc.WordRight, tc.KeepAnchor)

        return completionPrefix

    # ----------------------------------------------------------------------
    def focusInEvent(self, event):
        """"""
        if self.completer:
            self.completer.setWidget(self)
        QTextEdit.focusInEvent(self, event)

    # ----------------------------------------------------------------------
    def show_completer(self, completionPrefix):
        """"""
        self.completer.setCompletionPrefix(completionPrefix)
        popup = self.completer.popup()
        popup.setCurrentIndex(self.completer.completionModel().index(0, 0))
        cr = self.cursorRect()
        cr.setWidth(self.completer.popup().sizeHintForColumn(0) + self.completer.popup().verticalScrollBar().sizeHint().width() + 15)
        cr.setHeight(30)

        self.completer.complete(cr)
