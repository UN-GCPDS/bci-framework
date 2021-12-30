"""
===============
CSS Highlighter
===============

QSyntaxHighlighter for CSS syntax.
"""

import os

from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter


########################################################################
class CSSHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for CSS style sheets."""

    keywords = ['important', ]

    # Python operators
    operators = ['=',
                 # Comparison
                 '==', '!=', '<', '<=', '>', '>=',
                 # Arithmetic
                 '\+', '-', '\*', '/', '//', '\%', '\*\*',
                 # In-place
                 '\+=', '-=', '\*=', '/=', '\%=',
                 # Bitwise
                 '\^', '\|', '\&', '\~', '>>', '<<',
                 ]

    # Python braces
    braces = ['\{', '\}', '\(', '\)', '\[', '\]', ]

    # ----------------------------------------------------------------------
    def __init__(self, document):
        """"""
        QSyntaxHighlighter.__init__(self, document)

        rules = []

        # Keyword, operator, and brace rules
        rules += [(r'\b%s\b' % w, 0, self.styles['keyword'])
                  for w in CSSHighlighter.keywords]

        rules += [(r'( )', 0, format('#4f5b62'))]

        # All other rules
        rules += [(r'"[^"\\]*(\\.[^"\\]*)*"', 0, self.styles['value']),
                  (r"'[^'\\]*(\\.[^'\\]*)*'", 0, self.styles['value']),

                  (r'^([\w]+)[#\.\w\[\]=]*\s*\{',
                   1, self.styles['selector']),
                  (r'^\s*([\w-]+)\s*:\s*([\w\'"#]+)', 1, self.styles['key']),
                  (r'^\s*([\w-]+)\s*:\s*([\w\'"#]+)',
                   2, self.styles['value']),

                  # Numeric literals
                  (r'\b[+-]?[0-9]+[lL]?\b', 0, self.styles['numbers']),
                  (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b',
                   0, self.styles['numbers']),
                  (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b',
                   0, self.styles['numbers']),
                  ]

        # Build a QRegularExpression for each pattern
        self.rules = [(QRegularExpression(pat), index, fmt)
                      for (pat, index, fmt) in rules]

    # ----------------------------------------------------------------------
    def highlightBlock(self, text: str) -> None:
        """Apply syntax highlighting to the given block of text."""
        # Do other syntax formatting
        for expression, nth, format_ in self.rules:
            index = expression.match(text, 0).capturedStart(nth)

            start = 0
            while index >= 0:
                # We actually want the index of the nth match
                index = expression.match(text, start).capturedStart(nth)
                length = expression.match(text, start).capturedLength(nth)
                end = expression.match(text, start).capturedEnd(nth)

                self.setFormat(index, length, format_)
                start = end

        self.setCurrentBlockState(0)

    # ----------------------------------------------------------------------
    @classmethod
    def get_format(cls, color: str, style='', fontsize=None) -> QTextCharFormat:
        """Return a QTextCharFormat with the given attributes."""
        _color = QColor()
        _color.setNamedColor(color)

        _format = QTextCharFormat()
        _format.setForeground(_color)
        if 'bold' in style:
            _format.setFontWeight(QFont.Bold)
        if 'italic' in style:
            _format.setFontItalic(True)

        if fontsize:
            _format.setFontPointSize(fontsize)

        return _format

    # ----------------------------------------------------------------------
    @property
    def styles(self):
        """The styles depend on the theme."""
        if 'light' in os.environ['QTMATERIAL_THEME']:

            # Syntax self.styles that can be shared by all languages
            return {
                'selector': self.get_format('#00007f', 'bold'),
                'keyword': self.get_format('#ff7c00', 'bold'),
                'numbers': self.get_format('#007f7f'),
                'key': self.get_format('#0040e0'),  # .
                'value': self.get_format('#7f007f'),  # .

            }
        else:
            return {
                'selector': self.get_format('#8080ff', 'bold'),
                'key': self.get_format('#63a3ff'),
                'value': self.get_format('#ff7ed8'),
                'keyword': self.get_format('#ff7c00', 'bold'),
                'numbers': self.get_format('#72e4e4'),
            }
