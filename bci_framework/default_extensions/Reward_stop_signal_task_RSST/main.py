from bci_framework.extensions.stimuli_delivery import StimuliAPI
from bci_framework.extensions.stimuli_delivery.utils import Widgets as w
from bci_framework.extensions.stimuli_delivery.utils import keypress
import logging
from browser import html, timer
import random

from figures import Stimuli  
  
from typing import Literal     


########################################################################
class StimuliDelivery(StimuliAPI):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_stylesheet('styles.css')

        # self.stimuli = Stimuli('original')
        self.stimuli = Stimuli()

        self.stimuli_area <= self.stimuli.canvas
        self.stimuli_area <= self.stimuli.score

        self.builded = False
        self.response = None
        self.show_cross()
        self.show_synchronizer()

        self.dashboard <= w.label(
            'Reward stop signal task - RSST', 'headline4')
        self.dashboard <= html.BR()

        self.dashboard <= w.switch(
            label='Original assets',
            checked=True,
            on_change=self.set_assets,
            id='assets',
        )

        self.dashboard <= w.range_slider(
            label='Inter stimulus interval',
            min=500,
            max=4000,
            value_lower=1600,
            value_upper=2000,
            step=100,
            unit='ms',
            id='isi',
        )

        self.dashboard <= w.slider(
            label='Stmuli duration',
            min=50,
            max=1000,
            value=170,
            step=10,
            unit='ms',
            id='stimuli_duration',
        )

        self.dashboard <= w.slider(
            label='Initial delay',
            min=250,
            max=950,
            value=500,
            step=50,
            unit='ms',
            id='delay',
        )

        self.dashboard <= w.slider(
            label='Trials',
            min=10,
            max=100,
            value=60,
            step=1,
            unit='',
            id='trials',
        )

        self.dashboard <= w.slider(
            label='Probability for inhibition',
            min=0.2,
            max=0.3,
            value=0.25,
            step=0.01,
            unit='',
            id='p',
        )

        self.dashboard <= w.switch(
            label='External marker synchronizer',
            checked=False,
            on_change=self.synchronizer,
        )

        self.dashboard <= w.switch(
            label='External marker synchronizer (Top square)',
            checked=False,
            on_change=self.synchronizer_square,
        )

        self.dashboard <= w.toggle_button(
            [('Start run', self.start), ('Stop run', self.stop)], id='run')

        self.dashboard <= html.BR()

        self.dashboard <= w.button('Target left', on_click=lambda: self.stimuli.show_target(
            'left', w.get_value('stimuli_duration')))
        self.dashboard <= w.button('Target right', on_click=lambda: self.stimuli.show_target(
            'right', w.get_value('stimuli_duration')))
        self.dashboard <= w.button('Fail', on_click=lambda: self.stimuli.show_fail(
            w.get_value('stimuli_duration')))
        self.dashboard <= w.button('Coin', on_click=lambda: self.stimuli.show_coin(
            w.get_value('stimuli_duration')))
        self.dashboard <= w.button(
            'Remove coin', on_click=self.stimuli.remove_coin)
        self.dashboard <= w.button(
            'Build trials', on_click=self.build_trials)
        self.dashboard <= w.toggle_button([('Start marker synchronization', self.start_marker_synchronization), (
            'Stop marker synchronization', self.start_marker_synchronization)], id='sync')

    # ----------------------------------------------------------------------

    def set_assets(self, value) -> None:
        """"""
        if value:
            self.stimuli.set_style('original')
        else:
            self.stimuli.set_style('fancy')

    # ----------------------------------------------------------------------
    def start(self) -> None:
        """Start the run.

        A run consist in a consecutive trials execution.
        """
        if w.get_value('record'):
            self.start_record()

        # self.delay = w.get_value('delay')
        # self.trials_count = w.get_value('trials')

        # self.build_trials()
        timer.set_timeout(self.run_trials, 2000)

        self.show_progressbar(w.get_value('trials') * 2)

        logging.warning(
            f'Probability to see an inhibition event: {w.get_value("p")}')

    # ----------------------------------------------------------------------
    def run_trials(self) -> None:
        """"""
        if not self.builded:
            self.build_trials()

        self.prepare_trial(self.delay)

        logging.warning('#' * 32)
        logging.warning(
            f'Trial: {w.get_value("trials") - self.trials_count}')

        if self.trials_count > 1:
            self.run_pipeline(self.pipeline_trial, self.trials,
                              callback='run_trials', show_progressbar=False)
        else:
            self.run_pipeline(self.pipeline_trial, self.trials,
                              callback='stop_run', show_progressbar=False)

        self.trials_count -= 1

    # ----------------------------------------------------------------------
    def stop(self) -> None:
        """Stop pipeline execution."""
        self.stop_pipeline()

    # ----------------------------------------------------------------------
    def stop_run(self) -> None:
        """Stop pipeline execution."""
        self.isi()
        w.get_value('run').off()
        if w.get_value('record'):
            timer.set_timeout(self.stop_record, 2000)

    # ----------------------------------------------------------------------
    def build_trials(self) -> None:
        """"""
        self.delay = w.get_value('delay')
        self.trials_count = w.get_value('trials')

        self.inhibitions_array = self.generate_trials(
            p=w.get_value('p'), count=w.get_value('trials'))
        self.trials_array = random.choices(
            ['Right', 'Left'], k=w.get_value('trials'))
        logging.warning(
            f'{[f"{t}:{i}" for t, i in zip(self.trials_array, self.inhibitions_array)]}')
        self.builded = True

    # ----------------------------------------------------------------------
    def generate_trials(self, p, count):
        """"""
        min_ = round(count * p)
        validated = False
        while True:
            a = ''.join(map(str, random.choices(
                [1, 0], (p, 1 - p), k=count)))
            if a.startswith('1'):
                continue
            if '11' in a:
                continue
            if a.count('1') < min_:
                continue
            break

        return [l == '1' for l in list(a)]

    # ----------------------------------------------------------------------
    def prepare_trial(self, delay=250) -> None:
        """Define the `trials` and `pipeline trials`.

        The `trials` consist (in this case) in a list of cues.
        The `pipeline trials` is a set of couples `(callable, duration)` that
        define a single trial, this list of functions are executed asynchronously
        and repeated for each trial.
        """

        self.trials = [{'cue': self.trials_array.pop(0),
                        'inhibition': self.inhibitions_array.pop(0),
                        'delay': delay,
                        }]

        self.pipeline_trial = [
            ['target', delay],
            ['inhibition', 'stimuli_duration'],
            ['isi', 'isi'],
        ]

    # ----------------------------------------------------------------------
    def isi(self, *args) -> None:
        """Stimulus onset asynchronously.

        This is a pipeline method, that explains the unused `*args` arguments.
        """
        # self.stimuli.hide()

    # ----------------------------------------------------------------------
    def get_delay(self, *args) -> None:
        """"""
        return self.delay

    # ----------------------------------------------------------------------
    def target(self, cue: Literal['Right', 'Left'], inhibition: bool, delay: int):
        """"""
        self.stimuli.show_target(cue, w.get_value('stimuli_duration'))
        logging.warning(f'Delay: {delay}')
        self.previous_response = self.response
        self.response = None
        self.key_timer = keypress(self.handle_response, delay - 8)

    # ----------------------------------------------------------------------
    def inhibition(self, cue, inhibition: bool, delay: int) -> None:
        """Cue visualization.

        This is a pipeline method, that means it receives the respective trial
        as argument each time is called.
        """
        logging.warning(
            f'Inhibition: {inhibition} | Response: {self.response}')

        if inhibition:
            if self.response is None:

                if delay > 250:
                    self.delay = delay - 50

                if self.previous_response:
                    self.stimuli.show_coin(w.get_value('stimuli_duration'))
                    logging.warning(f'Coin!')
                else:
                    logging.warning(f'Fail because no previous response')

            elif self.response in ['Right', 'Left']:
                logging.warning(f'Fail!!')
                self.stimuli.show_fail(w.get_value('stimuli_duration'))
                if delay < 950:
                    self.delay = delay + 50

    # ----------------------------------------------------------------------
    def handle_response(self, response: str) -> None:
        """Capture the subject keyboard response."""

        if response == 'q':
            self.response = 'Left'
        elif response == 'p':
            self.response = 'Right'
        else:
            self.response = None

        logging.warning(f'Previous Response: {self.previous_response}')
        logging.warning(f'Response: {self.response}')

    # ----------------------------------------------------------------------
    def synchronizer(self, value: bool) -> None:
        """Show or hide synchronizer."""
        if value:
            self.show_synchronizer()
        else:
            self.hide_synchronizer()

    # ----------------------------------------------------------------------
    def synchronizer_square(self, value: bool) -> None:
        """Show or hide synchronizer."""
        if value:
            self.show_synchronizer(
                size=60, type='square', position='upper left')
        else:
            self.hide_synchronizer()
            



if __name__ == '__main__':
    StimuliDelivery()


