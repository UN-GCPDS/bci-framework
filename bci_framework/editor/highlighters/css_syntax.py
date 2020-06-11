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
    'selector': format('#8080FF', 'bold'),
    'key': format('#63A3FF'),
    'value': format('#FF7ED8'),
    'keyword': format('#ff7c00', 'bold'),
    'numbers': format('#72e4e4'),
    # 'string': format('#ff80ff'),

    # 'keyword': format('#8080ff', 'bold'),
    # 'comment': format('#7efb7e'),
    # 'operator': format('white', 'bold'),
    # 'brace': format('white'),
    # 'class': format('#4444ff', 'bold'),
    # 'string2': format('#ac5656'),
}


class CSSHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for the Python language.
    """
    # # Python keywords
    # keywords_bold = [
        # 'and', 'assert', 'break', 'class', 'continue', 'def',
        # 'del', 'elif', 'else', 'except', 'exec', 'finally',
        # 'for', 'from', 'global', 'if', 'import', 'in',
        # 'is', 'lambda', 'not', 'or', 'pass', 'print',
        # 'raise', 'return', 'try', 'while', 'yield',
        # 'None', 'True', 'False',
    # ]

    keywords = [
        'important',
    ]

    # Python operators
    operators = [
        '=',
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
        # self.tri_single = (QRegExp("'''"), 1, STYLES['string2'])
        # self.tri_double = (QRegExp(r'\b([\w]*)\b\s\{[ \t\r\s\n\w:;\-\'"!]*\}'), 2, STYLES['string2'])

        rules = []

        # Keyword, operator, and brace rules
        rules += [(r'\b%s\b' % w, 0, STYLES['keyword']) for w in CSSHighlighter.keywords]
        # rules += [(r'%s' % w, 0, STYLES['keyword2']) for w in CSSHighlighter.keywords]
        # rules += [(r'%s' % o, 0, STYLES['operator']) for o in CSSHighlighter.operators]
        # rules += [(r'%s' % b, 0, STYLES['brace']) for b in CSSHighlighter.braces]

        # rules += [(r'\b([\w]*)\b\s\{[ \t\r\s\n\w:;\-\'"!]*\}')]

        rules += [(r'( )', 0, format('#4f5b62'))]

        # All other rules
        rules += [
            # 'self'
            # (r'\bself\b', 0, STYLES['self']),

            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['value']),
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['value']),



            (r'^([\w]+)[#\.\w\[\]=]*\s*\{', 1, STYLES['selector']),
            # (r'^\s*([\w-]+)\s*:', 1, STYLES['key']),
            (r'^\s*([\w-]+)\s*:\s*([\w\'"#]+)', 1, STYLES['key']),
            (r'^\s*([\w-]+)\s*:\s*([\w\'"#]+)', 2, STYLES['value']),


            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers']),

        ]

        # Build a QRegExp for each pattern
        self.rules = [(QRegExp(pat), index, fmt)
                      for (pat, index, fmt) in rules]

    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """
        # if not text:
            # self.setCurrentBlockState(0)
            # return

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

        # # Do multi-line strings
        # in_multiline = self.match_multiline(text, *self.tri_single)
        # if not in_multiline:
            # in_multiline = self.match_multiline(text, *self.tri_double)

    # def match_multiline(self, text, delimiter, in_state, style):
        # """Do highlighting of multi-line strings. ``delimiter`` should be a
        # ``QRegExp`` for triple-single-quotes or triple-double-quotes, and
        # ``in_state`` should be a unique integer to represent the corresponding
        # state changes when inside those strings. Returns True if we're still
        # inside a multi-line string when this function is finished.
        # """
        # # If inside triple-single quotes, start at 0
        # if self.previousBlockState() == in_state:
            # start = 0
            # add = 0
        # # Otherwise, look for the delimiter on this line
        # else:
            # start = delimiter.indexIn(text)
            # # Move past this match
            # add = delimiter.matchedLength()

        # # As long as there's a delimiter match on this line...
        # while start >= 0:
            # # Look for the ending delimiter
            # end = delimiter.indexIn(text, start + add)
            # # Ending delimiter on this line?
            # if end >= add:
                # length = end - start + add + delimiter.matchedLength()
                # self.setCurrentBlockState(0)
            # # No; multi-line string
            # else:
                # self.setCurrentBlockState(in_state)
                # length = len(text) - start + add
            # # Apply formatting
            # self.setFormat(start, length, style)
            # # Look for the next match
            # start = delimiter.indexIn(text, start + length)

        # # Return True if still inside a multi-line string, False otherwise
        # if self.currentBlockState() == in_state:
            # return True
        # else:
            # return False

