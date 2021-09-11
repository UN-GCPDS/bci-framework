"""
=====================
4-Class motor imagery
=====================

"""
from bci_framework.extensions.stimuli_delivery import StimuliAPI
from bci_framework.extensions.stimuli_delivery.utils import Widgets as w

from browser import html, timer
import random
import logging
from typing import Literal

UNICODE_CUES = {
    'Right': 'arrow-right-short',
    'Left': 'arrow-left-short',
    'Up': 'arrow-up-short',
    'Bottom': 'arrow-down-short',
}


########################################################################
class FourClassMotorImagery(StimuliAPI):
    """Classic arrow cues for motor imagery."""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        self.add_stylesheet('styles.css')

        self.show_cross()

        self.dashboard <= w.label('4-Class motor imagery', 'headline4')
        self.dashboard <= w.checkbox(
            label='Cues',
            options=[[cue, True] for cue in UNICODE_CUES],
            on_change=None,
            id='cues',
        )
        self.dashboard <= w.slider(
            label='Trials per class:',
            min=1,
            max=100,
            value=10,
            step=1,
            discrete=True,
            marks=True,
            id='repetitions',
        )
        self.dashboard <= w.slider(
            label='Stimulus duration',
            min=2000,
            max=6000,
            value=4000,
            step=100,
            unit='ms',
            id='duration',
        )
        self.dashboard <= w.range_slider(
            label='Stimulus onset asynchronously',
            min=1000,
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
            id='record',
        )
        self.dashboard <= w.switch(
            label='External marker synchronizer',
            checked=False,
            on_change=self.synchronizer,
        )

        self.dashboard <= w.toggle_button([('Start run', self.start), ('Stop run', self.stop)], id='run')
        self.dashboard <= w.toggle_button([('Start marker synchronization', self.start_marker_synchronization), ('Stop marker synchronization', self.start_marker_synchronization)], id='sync')


    # ----------------------------------------------------------------------
    def start(self) -> None:
        """Start the run.

        A run consist in a consecutive trials execution.
        """
        if w.get_value('record'):
            self.start_record()

        self.build_trials()
        timer.set_timeout(lambda: self.run_pipeline(
            self.pipeline_trial, self.trials, callback='stop_run'), 2000)

    # ----------------------------------------------------------------------
    def stop(self) -> None:
        """Stop pipeline execution."""
        self.stop_pipeline()

    # ----------------------------------------------------------------------
    def stop_run(self) -> None:
        """Stop pipeline execution."""
        self.soa()
        w.get_value('run').off()
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
        self.trials = [{'cue': trial} for trial in self.trials]

        self.pipeline_trial = [
            ['soa', 'soa'],  # `soa` is a range reference
            ['trial', 'duration'],  # `duration` is a slider reference
        ]

    # ----------------------------------------------------------------------
    def soa(self, *args) -> None:
        """Stimulus onset asynchronously.

        This is a pipeline method, that explains the unused `*args` arguments.
        """
        if element := getattr(self, 'cue_placeholder', None):
            element.class_name = ''

    # ----------------------------------------------------------------------
    def trial(self, cue: Literal['Right', 'Left', 'Up', 'Bottom']) -> None:
        """Cue visualization.

        This is a pipeline method, that means it receives the respective trial
        as argument each time is called.
        """
        if not hasattr(self, 'cue_placeholder'):
            self.cue_placeholder = html.I('', id='cue')
            self.stimuli_area <= self.cue_placeholder

        self.send_marker(cue)
        self.cue_placeholder.class_name = f'bi bi-{UNICODE_CUES[cue]}'
        self.cue_placeholder.style = {'display': 'flex'}

    # ----------------------------------------------------------------------
    def synchronizer(self, value: bool) -> None:
        """Show or hide synchronizer."""
        if value:
            self.show_synchronizer()
        else:
            self.hide_synchronizer()


if __name__ == '__main__':
    FourClassMotorImagery()

