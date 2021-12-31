"""
=============
Autocompleter
=============

Auxiliar pop-up list of options with frequent use snippets and methods.
"""

from typing import Literal

from PySide6 import QtCore
from PySide6.QtWidgets import QCompleter

from .snippets import STIMULI_KEYWORDS, ANALISYS_KEYWORDS, VISUALIZATION_KEYWORDS
from .snippets import analysis_snippets, stimuli_snippets, visualizations_snippets, snippets, locktime_snippets


########################################################################
class Autocompleter(QCompleter):
    """Autocompleter for Python Scripts."""

    insertText = QtCore.Signal(str)

    # ----------------------------------------------------------------------
    def __init__(self, mode: Literal['stimuli', 'visualization', 'analysis', 'locktime'], parent=None):
        """"""
        if mode == 'stimuli':
            QCompleter.__init__(self, STIMULI_KEYWORDS, parent)
            self.snippets = {**snippets, **stimuli_snippets}
        elif mode == 'visualization':
            QCompleter.__init__(self, VISUALIZATION_KEYWORDS, parent)
            self.snippets = {**visualizations_snippets, **snippets}
        elif mode == 'analysis':
            QCompleter.__init__(self, ANALISYS_KEYWORDS, parent)
            self.snippets = {**analysis_snippets, **snippets}
        elif mode == 'locktime':
            QCompleter.__init__(self, ANALISYS_KEYWORDS, parent)
            self.snippets = {**locktime_snippets, **snippets}

        self.connect(self, QtCore.SIGNAL(
            "activated(const QString&)"), self.changeCompletion)
        self.connect(self, QtCore.SIGNAL(
            "highlighted(const QString&)"), self.changeHighlighted)

        self.regular_items = self.model().stringList()

        self.setMaxVisibleItems(15)
        self.popup().setStyleSheet("""
        *{
        font-size:  15px;
        min-height: 30px;
        }
        """)

    # ----------------------------------------------------------------------
    def changeCompletion(self, completion: str) -> None:
        """Update list options."""
        if completion.find("(") != -1:
            completion = completion[:completion.find("(")]
        self.insertText.emit(completion)

    # ----------------------------------------------------------------------
    def changeHighlighted(self, value: str) -> None:
        """Retain the last option selected."""
        self.last_highlighted = value

    # # ----------------------------------------------------------------------
    # def set_temporal(self, values):
        # """"""
        # m = self.model()
        # m.setStringList(self.regular_items + values)
        # # self.setModel(m)

