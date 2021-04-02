"""
=====================
4-Class Motor Imagery
=====================

"""

from bci_framework.extensions.stimuli_delivery import StimuliAPI
from bci_framework.extensions.stimuli_delivery.utils import Widgets as w

from browser import html, timer
import random
import logging

UNICODE_CUES = {
    'Right': '&#x1f86a;',
    'Left': '&#x1f868;',
    'Up': '&#x1f869;',
    'Bottom': '&#x1f86b;',
}


########################################################################
class FourClassMotorImagery(StimuliAPI):
    """Classic arrow cues for motor imagery."""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        self.add_stylesheet('styles.css')

        self.build_areas()
        self.show_cross()
        self.show_blink_area()

        self.dashboard <= w.label('4-Class motor imagery<br>', 'headline4')

        self.dashboard <= w.checkbox(
            'Cues',
            options=[[cue, True] for cue in UNICODE_CUES],
            on_change=None,
            id='cues',
        )
        self.dashboard <= w.slider(
            label='Repetitions by class:',
            min=1,
            max=40,
            value=10,
            step=1,
            discrete=True,
            marks=True,
            id='repetitions',
        )
        self.dashboard <= w.slider(
            label='Stimulus duration',
            min=2000,
            max=5000,
            value=4000,
            step=100,
            unit='ms',
            id='duration',
        )
        self.dashboard <= w.range_slider(
            label='Inter trial',
            min=2000,
            max=3000,
            value_lower=2000,
            value_upper=3000,
            step=100,
            unit='ms',
            id='soa',
        )
        self.dashboard <= w.switch(
            label='Record EEG',
            checked=False,
            on_change=None,
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
            self.pipeline_trial, self.trials, callback=self.soa), 2000)

    # ----------------------------------------------------------------------
    def stop(self) -> None:
        """Stop pipeline execution."""
        self.stop_pipeline()
        self.cue_placeholder.html = ''
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
        self.trials = w.get_value('cues') * w.get_value('repetitions')
        random.shuffle(self.trials)

        self.pipeline_trial = [
            (self.soa, 'soa'),  # `soa` is a range reference
            (self.trial, 'duration'),  # `duration` is a slider reference
        ]

    # ----------------------------------------------------------------------
    def soa(self, *args) -> None:
        """Stimulus onset asynchronously.

        This is a pipeline method, that explains the `*args` arguments.
        """
        if element := getattr(self, 'cue_placeholder', None):
            element.html = ''

    # ----------------------------------------------------------------------
    def trial(self, cue: str) -> None:
        """Cue visualization.

        This is a pipeline method, that means it receives the respective trial
        as argument each time is called.
        """
        if not hasattr(self, 'cue_placeholder'):
            self.cue_placeholder = html.SPAN('', id='cue')
            self.stimuli_area <= self.cue_placeholder

        self.send_marker(cue)
        self.cue_placeholder.html = UNICODE_CUES[cue]
        self.cue_placeholder.style = {'display': 'flex'}


if __name__ == '__main__':
    FourClassMotorImagery()

