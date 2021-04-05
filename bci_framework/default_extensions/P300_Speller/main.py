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

CHARACTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


########################################################################
class P300Speller(StimuliAPI):
    """Classic P300 speller."""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        self.add_stylesheet('styles.css')

        self.stimuli_area.style = {'background-color': 'black'}
        self.build_grid()

        self.dashboard <= w.label('P300 Speller', 'headline4')
        self.dashboard <= w.slider(
            label='Trials:',
            min=1,
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
        inter_stimulus = w.get_value('inter_stimulus')
        duration = w.get_value('duration')

        self.trials = []
        for _ in range(w.get_value('trials')):
            stimuli_array = []
            for i in range(6):
                stimuli_array.append(
                    [e.text for e in document.select(f'.col-{i}')])
                stimuli_array.append(
                    [e.text for e in document.select(f'.row-{i}')])
            random.shuffle(stimuli_array)

            self.trials.append({'target': random.choice(CHARACTERS),
                                'array': stimuli_array})

        random.shuffle(self.trials)

        self.pipeline_trial = [
            (lambda ** kwargs: None, 500),
            (self.target_notice, w.get_value('notice')),
            (self.inter_stimulus, 3000)
        ]

        [self.pipeline_trial.extend(
            [(self.activate, 300),
             (self.inter_stimulus, 300)]) for _ in range(12)]

    # ----------------------------------------------------------------------
    def target_notice(self, target: str, array: List[str]) -> None:
        """Highlight the character that's subject must focus on."""
        target = document.select_one(f".p300-{target}-")
        target.style = {'color': '#00ff00',
                        'opacity': 0.5, 'font-weight': 'bold'}

    # ----------------------------------------------------------------------
    def inter_stimulus(self, **kwargs) -> None:
        """Remove the highlight over the focus character."""
        for element in document.select('.p300-char'):
            element.style = {'opacity': 0.3,
                             'color': '#ffffff',
                             'font-weight': 'normal',
                             }

    # ----------------------------------------------------------------------
    def activate(self, target: str, array: List[str]) -> None:
        """Highlight a column or a row."""
        elements = [document.select_one(
            f".p300-{char}-") for char in array.pop(0)]
        for element in elements:
            element.style = {'opacity': 1,
                             'font-weight': 'bold',
                             }

    # ----------------------------------------------------------------------
    def build_grid(self) -> None:
        """Create the grid with the letters."""
        table = html.TABLE(CLass='p300')
        tr = html.TR()
        table <= tr

        for i, char in enumerate(CHARACTERS):
            col = i // 6
            row = i % 6
            tr <= html.TD(
                char, Class=f'p300-char p300-{char}- col-{col} row-{row}')
            if i != 0 and not (i + 1) % 6:
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


if __name__ == '__main__':
    P300Speller()


