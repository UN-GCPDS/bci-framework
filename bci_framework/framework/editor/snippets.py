# General snippets

snippets = {
    "def (snippet)": "# ----------------------------------------------------------------------\ndef [!](self):\n    \"\"\"\"\"\"",

}

snippets_ = [
    "random.randint([!])", "random.shuffle([!])",
]


keywords = [
    'and', 'assert', 'break', 'class', 'continue',
    'del', 'elif', 'else', 'except', 'exec', 'finally',
    'for', 'from', 'global', 'if', 'import', 'in',
    'is', 'lambda', 'not', 'or', 'pass', 'print',
    'raise', 'return', 'try', 'while', 'yield',
    'None', 'True', 'False', 'as', '__name__', 'format', 'int', 'float', 'str',
    'list', 'tuple', 'dict', 'set', 'len', 'super', 'range', 'enumerate', 'hasattr', 'getattr',
]

# Stimuli delivery snippets

stimuli_snippets = {

    # Widgets
    "widgets.label (snippet)": "widgets.label('[!]', typo='body1')",
    "widgets.button (snippet)": "widgets.button('[!]', on_click=None)",
    "widgets.switch (snippet)": "widgets.switch('[!]', checked=True, on_change=None, id='')",
    "widgets.checkbox (snippet)": "widgets.checkbox('[!]', [[str, bool], ...], on_change=None, id='')",
    "widgets.radios (snippet)": "widgets.radios('[!]', [[str, [str], ...]], on_change=None, id='')",
    "widgets.select (snippet)": "widgets.select('[!]', [[str, [str], ...]], on_change=None, id='')",
    "widgets.slider (snippet)": "widgets.slider('[!]', min=1, max=10, step=0.1, value=5, unit='', on_change=None, id='')",
    "widgets.range_slider (snippet)": "widgets.range_slider('[!]', min=0, max=20, value_lower=5, value_upper=15, step=1, on_change=None, id='')",
    "widgets.get_value()": "self.widgets.get_value('[!]')",


}

stimuli_snippets_ = [

    # API
    'self.set_progress([!])', 'self.send_marker(\'[!]\')', 'self.send_marker(\'[!]\', blink=100)',

    # Brython
    'timer.set_timeout([!], 1000)',
    'timer.clear_timeout([!])',
    'timer.set_interval([!], 1000)',
    'timer.clear_interval([!])',
]


stimuly_keywords = [
    '@DeliveryInstance.local', '@DeliveryInstance.remote', '@DeliveryInstance.both',
    'self.dashboard', 'self.stimuli_area',
    'self.build_areas()', 'self.add_cross()', 'self.add_blink_area()', 'self.remove_blink_area()',
    'self.start_record()', 'self.stop_record()', 'self.add_run_progressbar()',

    'self.add_stylesheet()',
    'self.widgets',
]


# Data analisys snippets

analysis_snippets = {

}

analysis_snippets_ = [

]

analysis_keywords = [

]

# Visualizations snippets

visualizations_snippets = {

}

visualizations_snippets_ = [

]

visualizations_keywords = [

]


[stimuli_snippets.update({key.replace('[!]', ''): key})
 for key in stimuli_snippets_]
[analysis_snippets.update({key.replace('[!]', ''): key})
 for key in analysis_snippets_]
[visualizations_snippets.update({key.replace('[!]', ''): key})
 for key in visualizations_snippets_]


[snippets.update({key.replace('[!]', ''): key}) for key in snippets_]


STIMULI_KEYWORDS = stimuly_keywords + \
    list(stimuli_snippets.keys()) + list(snippets.keys())
ANALISYS_KEYWORDS = analysis_keywords + \
    list(analysis_snippets.keys()) + list(snippets.keys())
VISUALIZATION_KEYWORDS = visualizations_keywords + \
    list(visualizations_snippets.keys()) + list(snippets.keys())
