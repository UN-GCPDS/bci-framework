# syntax.py

import sys

from PySide2.QtCore import QRegExp
from PySide2.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter


def format(color, style='', fontsize=None):
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


# Syntax styles that can be shared by all languages
STYLES = {
    'keyword': format('#8080ff', 'bold'),
    'keyword2': format('#afdfff'),
    'comment': format('#7efb7e'),
    'operator': format('white', 'bold'),
    'decorator': format('#ffcf7f'),
    'brace': format('white'),
    'def': format('#7cf7f7', 'bold'),
    'class': format('#4444ff', 'bold'),
    'string': format('#ff80ff'),
    'string2': format('#ac5656'),
    'numbers': format('#72e4e4'),
}


class PythonHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for the Python language.
    """
    # Python keywords
    keywords_bold = [
        'and', 'assert', 'break', 'class', 'continue', 'def',
        'del', 'elif', 'else', 'except', 'exec', 'finally',
        'for', 'from', 'global', 'if', 'import', 'in',
        'is', 'lambda', 'not', 'or', 'pass', 'print',
        'raise', 'return', 'try', 'while', 'yield',
        'None', 'True', 'False', 'as'
    ]

    keywords = [
        '__name__', 'format', 'int', 'float', 'str', 'list', 'tuple', 'dict',
        'set', 'len', 'super', 'range', 'enumerate', 'hasattr', 'getattr',
    ]

    # Python operators
    operators = [
        '=', ':='
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
    braces = [
        '\{', '\}', '\(', '\)', '\[', '\]',
    ]

    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)

        # Multi-line strings (expression, flag, style)
        # FIXME: The triple-quotes in these two lines will mess up the
        # syntax highlighting from this point onward
        self.tri_single = (QRegExp("'''"), 1, STYLES['string2'])
        self.tri_double = (QRegExp('"""'), 2, STYLES['string2'])

        rules = []

        # Keyword, operator, and brace rules
        rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
                  for w in PythonHighlighter.keywords_bold]
        rules += [(r'\b%s\b' % w, 0, STYLES['keyword2'])
                  for w in PythonHighlighter.keywords]
        rules += [(r'\b%s\b' % o, 0, STYLES['operator'])
                  for o in PythonHighlighter.operators]
        rules += [(r'\b%s\b' % b, 0, STYLES['brace'])
                  for b in PythonHighlighter.braces]

        rules += [(r'( )', 0, format('#4f5b62'))]

        # All other rules
        rules += [
            # 'self'
            # (r'\bself\b', 0, STYLES['self']),

            # # Double-quoted string, possibly containing escape sequences
            # (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            # # Single-quoted string, possibly containing escape sequences
            # (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),

            # 'def' followed by an identifier
            (r'\bdef\b\s*(\w+)', 1, STYLES['def']),
            # 'class' followed by an identifier
            (r'\bclass\b\s*(\w+)', 1, STYLES['class']),


            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b',
             0, STYLES['numbers']),

            # From '#' until a newline
            # (r'(^"){1}(#\s*[^\n]*)(^"){1}', 1, STYLES['comment']),

            # (r'#.*(".*")+', 1, STYLES['comment']),
            # (r"#.*('.*')+", 1, STYLES['comment']),

            # (r'#[^\n"{2}]*', 0, STYLES['comment']),
            (r"""#[^\n'{2}"{2}]*""", 0, STYLES['comment']),

            # Double and Single-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),

            # Complete line commented
            (r'^[\s]*(#[^\n]*)', 1, STYLES['comment']),

            # Decorators
            (r'^[\s]*(@[^(]*)', 1, STYLES['decorator']),







        ]

        # Build a QRegExp for each pattern
        self.rules = [(QRegExp(pat), index, fmt)
                      for (pat, index, fmt) in rules]

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

    def match_multiline(self, text, delimiter, in_state, style):
        """Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QRegExp`` for triple-single-quotes or triple-double-quotes, and
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

