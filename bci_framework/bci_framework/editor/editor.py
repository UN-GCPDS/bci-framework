from PySide2.QtWidgets import QTextEdit
from PySide2.QtGui import QTextOption, QWheelEvent, QKeySequence
from PySide2.QtCore import Qt, QPoint
# from PySide2 import QtGui, QtCore
from .highlighters import PythonHighlighter, CSSHighlighter


########################################################################
class BCIEditor(QTextEdit):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, linenumber=None, extension='.py', *args, **kwargs):
        """Constructor"""

        super().__init__(*args, **kwargs)

        self.set_options()

        self.linenumber = linenumber

        # editor = QTextEdit()
        self.setStyleSheet("""
        QTextEdit {
        background-color: #000a12;
        color: white;
        height: 18px;
        font-weight: normal;
        font-family: 'DejaVu Sans Mono';
        font-size: 15px;
        line-height: 15px;
        border: 1px solid #263238;
        border-radius: 4px;
        height: 18px;
        padding: 0px;
        padding-top: 8px;
        }
        """)

        if extension == '.py':
            PythonHighlighter(self.document())
        elif extension == '.css':
            CSSHighlighter(self.document())

        self.connect_()

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

        document.setDefaultTextOption(option)
        self.setAcceptRichText(False)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

    # ----------------------------------------------------------------------
    def keyPressEvent(self, event):
        """"""
        # Replace Tabs with Spaces
        if event.key() == Qt.Key_Tab:
            tc = self.textCursor()
            tc.insertText(" " * 4)
            return

        print(event.key())

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

