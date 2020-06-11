from PySide2.QtWidgets import QTextEdit
from PySide2.QtGui import QTextOption, QWheelEvent
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
        font-family: 'monospace';
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
            self.linenumber.setHtml(f'<p style="text-align: right; line-height: 18px">{"<br>".join(content)}</p>')
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

        # Comment
        if (event.key() == Qt.Key_Slash) and bool(event.modifiers() & Qt.ControlModifier):
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
                        commented.append(" " * start_ + '# ' + line[start_:])
                        end += 2
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
                    tc.insertText(" " * start + '# ' + line[start:])
            return

        # Uncomment
        if (event.key() == Qt.Key_Question) and bool(event.modifiers() & Qt.ControlModifier):
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

                        if line[start_:start_ + 2] == '# ':
                            uncommented.append(line.replace('# ', '', 1))
                        else:
                            tc.insertText(selected)
                            return
                        end -= 2
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
                    start = line.find(line.replace(' ', '')[0])
                    if line[start:start + 2] == '# ':
                        tc.insertText(line.replace('# ', '', 1))
                    else:
                        tc.insertText(line)
            return

        if event.key() in [Qt.Key_Enter, Qt.Key_Enter - 1]:
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

        super().keyPressEvent(event)
