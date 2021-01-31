snippets = {

    "widgets.label (snippet)": "widgets.label('[!]', typo='body1')",
    "widgets.button (snippet)": "widgets.button('[!]', on_click=None)",
    "widgets.switch (snippet)": "widgets.switch('[!]', checked=True, on_change=None, id='')",
    "widgets.checkbox (snippet)": "widgets.checkbox('[!]', [[str, bool], ...], on_change=None, id='')",
    "widgets.radios (snippet)": "widgets.radios('[!]', [[str, [str], ...]], on_change=None, id='')",
    "widgets.select (snippet)": "widgets.select('[!]', [[str, [str], ...]], on_change=None, id='')",
    "widgets.slider (snippet)": "widgets.slider('[!]', min=1, max=10, step=0.1, value=5, on_change=None, id='')",
    "widgets.range_slider (snippet)": "widgets.range_slider('[!]', min=0, max=20, value_lower=5, value_upper=15, step=1, on_change=None, id='')",

    "def (snippet)": "# ----------------------------------------------------------------------\ndef [!](self):\n\t\"\"\"\"\"\"",


}


keywords = [
    'and', 'assert', 'break', 'class', 'continue',
    'del', 'elif', 'else', 'except', 'exec', 'finally',
    'for', 'from', 'global', 'if', 'import', 'in',
    'is', 'lambda', 'not', 'or', 'pass', 'print',
    'raise', 'return', 'try', 'while', 'yield',
    'None', 'True', 'False', 'as', '__name__', 'format', 'int', 'float', 'str', 'list', 'tuple', 'dict',
    'set', 'len', 'super', 'range', 'enumerate', 'hasattr', 'getattr',

    '@DeliveryInstance.local', '@DeliveryInstance.remote', '@DeliveryInstance.both',

    'dashboard', 'stimuli_area',

    'self.build_areas()', 'self.add_cross()', 'self.add_run_progressbar()',

]

KEYWORDS = keywords + list(snippets.keys())
