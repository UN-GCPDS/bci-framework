# ===============================================================================
# MyDictionaryCompleter
# ===============================================================================
from PySide2 import QtGui, QtCore
from PySide2.QtWidgets import QCompleter

from .snippets import KEYWORDS, snippets


########################################################################
class MyDictionaryCompleter(QCompleter):
    """"""
    insertText = QtCore.Signal(str)
    snippets = snippets

    def __init__(self, myKeywords=None, parent=None):

        QCompleter.__init__(self, KEYWORDS, parent)
        self.connect(self, QtCore.SIGNAL("activated(const QString&)"), self.changeCompletion)
        self.connect(self, QtCore.SIGNAL("highlighted(const QString&)"), self.changeHighlighted)

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

