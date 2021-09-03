"""
============
P300 Speller
============

"""

from bci_framework.extensions.stimuli_delivery import StimuliAPI
from bci_framework.extensions.stimuli_delivery.utils import Widgets as w
from bci_framework.extensions.stimuli_delivery.utils import Tone as t

from browser import document, html, timer
import random
import logging
from typing import List

CHARACTERS = "ABCDEF😂GHIJKL😍MNOPQR😘STUVWX😭YZ0123⎵456789⌫", 7

CHARACTERS_SRLZ = ["A", "B", "C", "D", "E", "F", "aa",
                   "G", "H", "I", "J", "K", "L", "bb",
                   "M", "N", "O", "P", "Q", "R", "cc",
                   "S", "T", "U", "V", "W", "X", "dd",
                   "Y", "Z", "0", "1", "2", "3", "ee",
                   "4", "5", "6", "7", "8", "9", "ff"]


########################################################################
class P300Speller(StimuliAPI):
    """Classic P300 speller."""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        self.add_stylesheet('styles.css')

        self.stimuli_area.style = {'background-color': 'black'}

        self.build_speller()
        self.build_grid()
        self.listen_feedbacks(self.on_feedback)

        self.dashboard <= w.label('P300 Speller', 'headline4')
        self.dashboard <= w.switch(
            label='Activate feedback speller',
            checked=False,
            on_change=self.show_speller,
            id='speller',
        )
        self.dashboard <= w.slider(
            label='Trials:',
            min=-1,
            max=15,
            value=5,
            step=1,
            discrete=True,
            marks=True,
            id='trials'
        )
        self.dashboard <= w.slider(
            label='Target notice:',
            min=500,
            max=5000,
            value=2000,
            step=100,
            unit='ms',
            id='notice'
        )
        self.dashboard <= w.slider(
            label='Flash duration:',
            min=100,
            max=500,
            value=125,
            step=5,
            unit='ms',
            id='duration'
        )
        self.dashboard <= w.slider(
            label='Inter stimulus interval:',
            min=10,
            max=500,
            value=62.5,
            step=5,
            unit='ms',
            id='inter_stimulus'
        )
        self.dashboard <= w.switch(
            label='Record EEG',
            checked=False,
            id='record',
        )
        self.dashboard <= w.switch(
            label='External marker synchronizer',
            checked=False,
            on_change=self.synchronizer,
            id='record',
        )

        self.dashboard <= w.button('Start run', on_click=self.start)
        self.dashboard <= w.button('Stop run', on_click=self.stop)

    # ----------------------------------------------------------------------
    def start(self) -> None:
        """Start the run.

        A run consist in a consecutive pipeline trials execution.
        """
        if w.get_value('record'):
            self.start_record()

        self.build_trials()
        timer.set_timeout(lambda: self.run_pipeline(
            self.pipeline_trial, self.trials), 2000)

    # ----------------------------------------------------------------------

    def stop(self) -> None:
        """Stop pipeline execution."""
        self.stop_pipeline()
        if w.get_value('record'):
            timer.set_timeout(self.stop_record, 2000)

    # ----------------------------------------------------------------------
    def build_trials(self) -> None:
        """Define the `trials` and `pipeline trials`.

        The `trials` consist (in this case) in a list of cues.
        The `pipeline trials` is a set of couples `(callable, duration)` that
        define a single trial, this list of functions are executed asynchronously
        and repeated for each trial.
        """
        self.propagate_seed()
        inter_stimulus = w.get_value('inter_stimulus')
        duration = w.get_value('duration')
        chars, ncols = CHARACTERS
        nrows = len(chars) // ncols

        self.trials = []
        trials = w.get_value('trials')
        if trials == -1:
            trials = 99
        for _ in range(trials):
            stimuli_array = []
            for i in range(ncols):
                stimuli_array.append(f'.col-{i}')
            for i in range(nrows):
                stimuli_array.append(f'.row-{i}')

            random.shuffle(stimuli_array)

            self.trials.append({'target': random.choice(CHARACTERS_SRLZ),
                                'array': stimuli_array})

        random.shuffle(self.trials)

        if not w.get_value('speller'):
            self.pipeline_trial = [
                ['none', 500],
                ['target_notice', w.get_value('notice')],
                ['inter_stimulus', 3000]
            ]
        else:
            self.pipeline_trial = []

        [self.pipeline_trial.extend(
            [['activate', 300],
             ['inter_stimulus', 300]]) for _ in range(nrows + ncols)]

    def none(self):
        pass

    # ----------------------------------------------------------------------
    def target_notice(self, target: str) -> None:
        """Highlight the character that's subject must focus on."""
        # self.send_marker(f"TARGET:{target}")
        target = document.select_one(f".p300-{target}-")
        target.style = {'color': '#00ff00',
                        'opacity': 0.5, 'font-weight': 'bold'}

    # ----------------------------------------------------------------------
    def inter_stimulus(self) -> None:
        """Remove the highlight over the focus character."""
        for element in document.select('.p300-char'):
            element.style = {'opacity': 0.3,
                             'color': '#ffffff',
                             'font-weight': 'normal',
                             }

    # ----------------------------------------------------------------------
    def activate(self, array: List[str], target: str) -> None:
        """Highlight a column or a row."""

        selector = array.pop(0)
        elements = document.select(selector)
        # self.send_marker(f"ERP:{selector[1:]}")

        if target in [e.attrs['char'] for e in elements]:
            self.send_marker("TARGET")
        else:
            self.send_marker("NO-TARGET")

        for element in elements:
            element.style = {'opacity': 1,
                             'font-weight': 'bold',
                             }

    # ----------------------------------------------------------------------
    def show_speller(self, visible) -> None:
        """"""
        if visible:
            self.speller.style = {'display': 'block'}
            self.last_value = w.component['trials'].mdc.getValue()
            w.component['trials'].mdc.setValue(-1)
            document.select_one('#value_trials').html = ' infinite'

        else:
            self.speller.style = {'display': 'none'}
            w.component['trials'].mdc.setValue(self.last_value)
            document.select_one('#value_trials').html = f' {self.last_value}'

    # ----------------------------------------------------------------------
    def build_speller(self) -> None:
        """"""
        self.speller = html.INPUT(
            Class="p300-speller", readonly=True, style={'display': 'none'})
        self.speller.value = '_'
        self.stimuli_area <= self.speller

    # ----------------------------------------------------------------------
    def build_grid(self) -> None:
        """Create the grid with the letters."""
        table = html.TABLE(CLass='p300')
        tr = html.TR()
        table <= tr

        characters_train, ncols = CHARACTERS

        for i, char in enumerate(characters_train):
            char_print = CHARACTERS_SRLZ[i]
            row = i // ncols
            col = i % ncols
            if row == 6:
                style = {"font-size": "6vh"}
            else:
                style = {}
            td = html.TD(
                char, Class=f'p300-char p300-{char_print}- col-{col} row-{row}', style=style)
            td.attrs['char'] = char_print
            tr <= td
            if i != 0 and not (i + 1) % ncols:
                tr = html.TR()
                table <= tr
        self.stimuli_area <= table

    # ----------------------------------------------------------------------
    def synchronizer(self, value: bool) -> None:
        """Show or hide synchronizer."""
        if value:
            self.show_synchronizer()
        else:
            self.hide_synchronizer()

    # ----------------------------------------------------------------------
    def on_feedback(self, value) -> None:
        """"""
        print(value)
        # if w.get_value('speller'):
            # self.speller.value = self.speller.value[:-1] + value + '_'


if __name__ == '__main__':
    P300Speller()


