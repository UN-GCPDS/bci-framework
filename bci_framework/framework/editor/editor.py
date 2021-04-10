"""
=========
BCIEditor
=========

"""

import os
from typing import Literal, TypeVar

from PySide2.QtWidgets import QTextEdit, QCompleter
from PySide2.QtGui import QTextOption
from PySide2.QtCore import Qt

from .highlighters import PythonHighlighter, CSSHighlighter


AUTOCOMPLETER = TypeVar('Autocompleter')


########################################################################
class BCIEditor(QTextEdit):
    """Custom QTextEdit with autocompleter and linenumbers.

    Parameters
    ----------
    linenumber
        QTextEdit object that will be updated with linenumbers.
    extension
        To set the highlighter.
    """

    # ----------------------------------------------------------------------
    def __init__(self, linenumber: QTextEdit, extension: Literal['.py', '.css'] = '.py', *args, **kwargs):
        """"""
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
    def connect_(self) -> None:
        """Update linenumber."""
        self.textChanged.connect(self.update_linenumber)

    # ----------------------------------------------------------------------
    def wheelEvent(self, evt):
        """Update the offset of the linenumber."""
        if self.linenumber:
            self.linenumber.wheelEvent(evt)
        return super().wheelEvent(evt)

    # ----------------------------------------------------------------------
    def update_linenumber(self) -> None:
        """Update linenumber."""
        lines = len(self.toPlainText().split('\n'))
        lines_ln = len(self.linenumber.toPlainText().split('\n'))

        if lines != lines_ln:
            content = [f'{l}' for l in range(1, lines + 1)]
            self.linenumber.setHtml(
                f'<p style="text-align: right; line-height: 18px">{"<br>".join(content)}</p>')
        self.linenumber.verticalScrollBar().setValue(self.verticalScrollBar().value())

    # ----------------------------------------------------------------------
    def set_options(self) -> None:
        """Configure QTextEdit."""
        document = self.document()
        option = QTextOption()

        document.setDefaultTextOption(option)
        self.setAcceptRichText(False)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

    # ----------------------------------------------------------------------
    def keyPressEvent(self, event):
        """Process key events."""

        completionPrefix = self.text_under_cursor()
        if self.completer and len(completionPrefix) < 3 and self.completer.popup().isVisible():
            self.completer.popup().hide()

        if event.key() in [Qt.Key_Tab, Qt.Key_Enter, Qt.Key_Enter - 1]:
            if self.completer and self.completer.popup().isVisible():
                self.completer.insertText.emit(self.completer.last_highlighted)
                self.completer.popup().hide()
                return

        if event.key() == Qt.Key_Tab:
            tc = self.textCursor()
            tc.insertText(" " * 4)
            return

        # Manage {([ for seleceted text
        for text, *keys in (["({})", Qt.Key_ParenLeft, Qt.Key_ParenRight],
                            ["[{}]", Qt.Key_BracketLeft, Qt.Key_BracketRight],
                            ["{{{}}}", Qt.Key_BraceLeft, Qt.Key_BraceRight],
                            ):
            if event.key() in keys:
                tc = self.textCursor()
                start = tc.selectionStart()
                if selected := tc.selectedText():
                    tc.removeSelectedText()
                    tc.insertText(text.format(selected))
                    if event.key() == keys[0]:
                        tc.setPosition(start, tc.MoveAnchor)
                    self.setTextCursor(tc)
                    return

        # Manage quotation for selected text
        for text, *keys in (['"{}"', Qt.Key_QuoteDbl],
                            ["'{}'", Qt.Key_Apostrophe, ]
                            ):
            if event.key() in keys:
                tc = self.textCursor()
                start = tc.selectionStart()
                if selected := tc.selectedText():
                    tc.removeSelectedText()
                    tc.insertText(text.format(selected))
                    self.setTextCursor(tc)
                    return

        # Toggle comment
        if (event.key() == Qt.Key_Period) and bool(event.modifiers() & Qt.ControlModifier):
            tc = self.textCursor()
            # pos = tc.position()
            tc.select(tc.LineUnderCursor)
            line = tc.selectedText()

            if line.strip() and line.strip()[0] == '#':
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

        if self.completer and event.text():
            completionPrefix = self.text_under_cursor()
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
        else:
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
                if line.strip():
                    tc.removeSelectedText()
                    start = line.find(line.replace(' ', '')[0])
                    tc.insertText(" " * start + f'{char}' + line[start:])

    # ----------------------------------------------------------------------
    def set_completer(self, completer: AUTOCOMPLETER) -> None:
        """Update the autocompleter used."""
        if self.completer:
            self.disconnect(self.completer)
        if not completer:
            return

        completer.setWidget(self)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer = completer
        self.completer.insertText.connect(self.insert_completion)

    # ----------------------------------------------------------------------
    def insert_completion(self, completion: str) -> None:
        """Process and inset the desired option."""
        tc = self.textCursor()
        self.text_under_cursor(tc)
        tc.removeSelectedText()
        pos = tc.position()

        if completion in self.completer.snippets:
            completion = self.completer.snippets[completion]

        extra = completion

        text_position = extra.find("[!]")
        extra = extra.replace("[!]", "")

        position_in_line = tc.positionInBlock()
        extra = extra.replace("\n", "\n" + " " * position_in_line)

        tc.insertText(extra)

        if text_position > 0:
            tc.setPosition(pos + text_position
                           + (4 * extra[:text_position].count('\n')))

        self.setTextCursor(tc)

    # ----------------------------------------------------------------------
    def text_under_cursor(self, tc=None) -> str:
        """Return de text under cursor."""

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
    def focusInEvent(self, event) -> None:
        """Keep the focus on the editor."""
        if self.completer:
            self.completer.setWidget(self)
        QTextEdit.focusInEvent(self, event)

    # ----------------------------------------------------------------------
    def show_completer(self, completion_prefix: str) -> None:
        """Show better options for current text."""
        self.completer.setCompletionPrefix(completion_prefix)
        popup = self.completer.popup()
        popup.setCurrentIndex(self.completer.completionModel().index(0, 0))
        cr = self.cursorRect()
        cr.setWidth(self.completer.popup().sizeHintForColumn(
            0) + self.completer.popup().verticalScrollBar().sizeHint().width() + 15)
        cr.setHeight(30)

        self.completer.complete(cr)
