"""
=======================================
4-Class motor imagery using Pacman cues
=======================================

"""

from bci_framework.extensions.stimuli_delivery import StimuliAPI
from bci_framework.extensions.stimuli_delivery.utils import Widgets as w
import logging
from pacman import create_pacman
from browser import document
from browser import html, timer
from typing import Literal

import random

CUES = [
    'Right',
    'Left',
    'Up',
    'Bottom',
]


########################################################################
class PacmanMotorImagery(StimuliAPI):
    """4-Class motor imagery with Pacman cues."""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_stylesheet('styles.css')

        self.show_cross()
        self.stimuli_area <= create_pacman()

        self.dashboard <= w.label(
            '4-Class motor imagery (Pacman)', 'headline4')
        self.dashboard <= w.checkbox(
            label='Cues',
            options=[[cue, True] for cue in CUES],
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

        A run consist in a consecutive pipeline trials execution.
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
            ['trial', 4000],
        ]

    # ----------------------------------------------------------------------
    def soa(self, *args) -> None:
        """Stimulus onset asynchronously.

        This is a pipeline method, that explains the `*args` arguments.
        """
        if element := getattr(self, 'cue_placeholder', None):
            element.html = ''

    # ----------------------------------------------------------------------
    def trial(self, cue: Literal['Right', 'Left', 'Up', 'Bottom']) -> None:
        """"""
        self.send_marker(cue)
        self.to_center()
        timer.set_timeout(getattr(self, f'on_{cue.lower()}'), 10)

    # ----------------------------------------------------------------------
    def on_right(self) -> None:
        """Start Pacman right walk animation."""
        pacman = document.select_one('.pacman')
        pacman.class_name += ' pacman-walk_right'

        for i in range(20):
            style = {
                'position': 'absolute',
                'top': 'calc(50% - 8px)',
                'left': f'calc(50% - 8px + 80px + {i*45}px)',
                'z-index': 50,
            }
            self.stimuli_area <= html.DIV(
                Class='food food__float', style=style)

    # ----------------------------------------------------------------------
    def on_left(self) -> None:
        """Start Pacman left walk animation."""
        pacman = document.select_one('.pacman')
        pacman.class_name += ' pacman-walk_left'

        for i in range(20):
            style = {
                'position': 'absolute',
                'top': 'calc(50% - 8px)',
                'left': f'calc(50% - 8px - 80px - {i*45}px)',
                'z-index': 50,
            }
            self.stimuli_area <= html.DIV(
                Class='food food__float', style=style)

    # ----------------------------------------------------------------------
    def on_up(self) -> None:
        """Start Pacman up walk animation."""
        pacman = document.select_one('.pacman')
        pacman.class_name += ' pacman-walk_top'

        for i in range(20):
            style = {
                'position': 'absolute',
                'left': 'calc(50% - 8px)',
                'top': f'calc(50% - 8px - 80px - {i*45}px)',
                'z-index': 50,
            }
            self.stimuli_area <= html.DIV(
                Class='food food__float', style=style)

    # ----------------------------------------------------------------------
    def on_bottom(self) -> None:
        """Start Pacman bottom walk animation."""
        pacman = document.select_one('.pacman')
        pacman.class_name += ' pacman-walk_bottom'

        for i in range(20):
            style = {
                'position': 'absolute',
                'left': 'calc(50% - 8px)',
                'top': f'calc(50% - 8px + 80px + {i*45}px)',
                'z-index': 50,
            }
            self.stimuli_area <= html.DIV(
                Class='food food__float', style=style)

    # ----------------------------------------------------------------------
    def to_center(self) -> None:
        """Reset Pacman position."""
        pacman = document.select_one('.pacman')
        pacman.class_name = 'pacman'

        for element in document.select('.food__float'):
            element.remove()

    # ----------------------------------------------------------------------
    def synchronizer(self, value: bool) -> None:
        """Show or hide synchronizer."""
        if value:
            self.show_synchronizer()
        else:
            self.hide_synchronizer()
            




if __name__ == '__main__':
    PacmanMotorImagery()


