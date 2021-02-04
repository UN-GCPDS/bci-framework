from PySide2 import QtCore
from PySide2.QtWidgets import QCompleter

from .snippets import STIMULI_KEYWORDS, ANALISYS_KEYWORDS, analisys_snippets, stimuli_snippets, snippets


########################################################################
class Autocompleter(QCompleter):
    """"""
    insertText = QtCore.Signal(str)

    # ----------------------------------------------------------------------
    def __init__(self, mode, parent=None):
        """"""
        if mode == 'stimuli':
            QCompleter.__init__(self, STIMULI_KEYWORDS, parent)
            self.snippets = {**snippets, **stimuli_snippets}
        elif mode == 'visualization':
            QCompleter.__init__(self, ANALISYS_KEYWORDS, parent)
            self.snippets = {**analisys_snippets, **snippets}

        self.connect(self, QtCore.SIGNAL(
            "activated(const QString&)"), self.changeCompletion)
        self.connect(self, QtCore.SIGNAL(
            "highlighted(const QString&)"), self.changeHighlighted)

        self.setMaxVisibleItems(15)
        self.popup().setStyleSheet("""
        *{
        font-size:  15px;
        min-height: 30px;
        }
        """)

    # ----------------------------------------------------------------------
    def changeCompletion(self, completion):
        if completion.find("(") != -1:
            completion = completion[:completion.find("(")]
        self.insertText.emit(completion)

    # ----------------------------------------------------------------------
    def changeHighlighted(self, value):
        """"""
        self.last_highlighted = value

