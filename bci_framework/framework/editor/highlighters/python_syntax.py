"""
==================
Python Highlighter
==================

QSyntaxHighlighter for Python syntax.
"""

import os

from PySide2.QtCore import QRegExp as QRegularExpression
from PySide2.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter


########################################################################
class PythonHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for the Python language.
    """
    # Python keywords
    keywords_bold = ['and', 'assert', 'break', 'class', 'continue', 'def',
                     'del', 'elif', 'else', 'except', 'exec', 'finally',
                     'for', 'from', 'global', 'if', 'import', 'in',
                     'is', 'lambda', 'not', 'or', 'pass', 'print',
                     'raise', 'return', 'try', 'while', 'yield',
                     'None', 'True', 'False', 'as',
                     ]

    keywords = ['__name__', 'format', 'int', 'float', 'str', 'list', 'tuple',
                'dict', 'set', 'len', 'super', 'range', 'enumerate', 'hasattr',
                'getattr', 'setattr', 'isinstance', 'issubclass', 'sum', 'ord',
                'chr', 'zip', 'bool'
                ]

    # Python operators
    operators = ['=', ':='
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
        QSyntaxHighlighter.__init__(self, document)

        # Multi-line strings (expression, flag, style) FIXME: The triple-quotes
        # in these two lines will mess up the syntax highlighting from this
        # point onward
        self.tri_single = (QRegularExpression("'''"), 1, self.styles['string2'])
        self.tri_double = (QRegularExpression('"""'), 2, self.styles['string2'])

        rules = []

        # Keyword, operator, and brace rules
        rules += [(r'\b%s\b' % w, 0, self.styles['keyword'])
                  for w in PythonHighlighter.keywords_bold]
        rules += [(r'\b%s\b' % w, 0, self.styles['keyword2'])
                  for w in PythonHighlighter.keywords]
        rules += [(r'\b%s\b' % o, 0, self.styles['operator'])
                  for o in PythonHighlighter.operators]
        rules += [(r'\b%s\b' % b, 0, self.styles['brace'])
                  for b in PythonHighlighter.braces]

        # All other rules
        rules += [
            # 'def' followed by an identifier
            (r'\bdef\b\s*(\w+)', 1, self.styles['def']),
            # 'class' followed by an identifier
            (r'\bclass\b\s*(\w+)', 1, self.styles['class']),

            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, self.styles['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, self.styles['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b',
             0, self.styles['numbers']),

            # From '#' until a newline
            (r"""#[^\n'{2}"{2}]*""", 0, self.styles['comment']),

            # Double and Single-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, self.styles['string']),
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, self.styles['string']),

            # Complete line commented
            (r'^[\s]*(#[^\n]*)', 1, self.styles['comment']),

            # Decorators
            (r'^[\s]*(@[^(]*)', 1, self.styles['decorator']),
        ]

        # Build a QRegularExpression for each pattern
        self.rules = [(QRegularExpression(pat), index, fmt)
                      for (pat, index, fmt) in rules]

    # ----------------------------------------------------------------------
    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """
        # Do other syntax formatting
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = len(expression.cap(nth))
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        # Do multi-line strings
        in_multiline = self.match_multiline(text, *self.tri_single)
        if not in_multiline:
            in_multiline = self.match_multiline(text, *self.tri_double)

    # ----------------------------------------------------------------------
    def match_multiline(self, text, delimiter, in_state, style):
        """Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QRegularExpression`` for triple-single-quotes or triple-double-quotes, and
        ``in_state`` should be a unique integer to represent the corresponding
        state changes when inside those strings. Returns True if we're still
        inside a multi-line string when this function is finished.
        """
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = delimiter.indexIn(text)
            # Move past this match
            add = delimiter.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimiter.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add
            # Apply formatting
            self.setFormat(start, length, style)
            # Look for the next match
            start = delimiter.indexIn(text, start + length)

        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False

    # ----------------------------------------------------------------------
    @classmethod
    def get_format(cls, color, style='', fontsize=None):
        """Return a QTextCharFormat with the given attributes.
        """
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
        # Syntax styles that can be shared by all languages
        if 'light' in os.environ['QTMATERIAL_THEME']:
            return {
                'operator': self.get_format('black', 'bold'),
                'brace': self.get_format('black'),
                'numbers': self.get_format('#007f7f'),
                'decorator': self.get_format('#805000'),
                'comment': self.get_format('#007f00'),
                'def': self.get_format('#007f7f', 'bold'),
                'keyword': self.get_format('#00007f', 'bold'),
                'class': self.get_format('#0000ff', 'bold'),
                'keyword2': self.get_format('#407090'),
                'string': self.get_format('#7f007f'),
                'string2': self.get_format('#7f0000'),

            }
        else:
            return {
                'keyword': self.get_format('#8080ff', 'bold'),
                'keyword2': self.get_format('#afdfff'),
                'comment': self.get_format('#7efb7e'),
                'operator': self.get_format('white', 'bold'),
                'decorator': self.get_format('#ffcf7f'),
                'brace': self.get_format('white'),
                'def': self.get_format('#7cf7f7', 'bold'),
                'class': self.get_format('#4444ff', 'bold'),
                'string': self.get_format('#ff80ff'),
                'string2': self.get_format('#ac5656'),
                'numbers': self.get_format('#72e4e4'),
            }
