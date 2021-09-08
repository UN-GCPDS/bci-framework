"""
===================================
Resting state and noise acquisition
===================================

"""

from bci_framework.extensions.stimuli_delivery import StimuliAPI, DeliveryInstance
from bci_framework.extensions.stimuli_delivery.utils import Widgets as w
from bci_framework.extensions.stimuli_delivery.utils import Tone as t
from bci_framework.extensions.stimuli_delivery.utils import keypress
import logging

from browser import document, timer, html

TASKS = {

    'resting_open': ['Resting with open eyes',
                     '<p>Resting with <b>open</b> eyes</p>',
                     '<p>Press the button and center your eyes on the fixation \
                     cross, the acquisition begins with the single beep, \
                     <b>keep this position until listen two beeps</b>.</p>'],

    'resting_close': ['Resting with close eyes',
                      '<p>Resting with <b>close</b> eyes</p>',
                      '<p>Press the button and close the eyes, the acquisition \
                      begins with the single beep, <b>keep eyes closed until \
                      listen two beeps</b>.</p>'],

    'eye_blinking': ['Eye blinking',
                     '<p>Eyes <b>blinking</b></p>',
                     '<p>Press the button and starts to blink periodically, \
                     the acquisition begins with the single beep, <b>keep this \
                     action until listen two beeps</b>.</p>'],

    'eyeball_up_down': ['Eyeball movement up/down',
                        '<p>Eyeball movement <b>Up</b> and <b>Down</b></p>',
                        '<p>Press the button and move your eyes up and down \
                        periodically, the acquisition begins with the single \
                        beep, <b>keep this action until listen two beeps</b>.</p>'],

    'eyeball_left_right': ['Eyeball movement left/right',
                           '<p>Eyeball movement <b>Left</b> and <b>Right</b></p>',
                           '<p>Press the button and move your eyes right and \
                           left periodically, the acquisition begins with the \
                           single beep, <b>keep this action until listen two \
                           beeps</b>.</p>'],

    'head_left_right': ['Head movement left/right',
                        '<p>Head movement <b>Left</b> and <b>Right</b></p>',
                        '<p>Press the button and move your head from left to \
                        right and right to left periodically, the acquisition \
                        begins with the single beep, <b>keep this action until \
                        listen two beeps</b>.</p>'],

    'jaw_clenching': ['Jaw clenching',
                      '<p>Jaw <b>clenching</b></p>',
                      '<p>Press the button and clench the jaw periodically, the \
                      acquisition begins with the single beep, <b>keep this \
                      action until listen two beeps</b>.</p>'],

}


########################################################################
class RestingNoiseAcquisition(StimuliAPI):
    """Resting state and noise acquisition"""
    DEBUG = True

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        self.add_stylesheet('styles.css')

        self.show_cross()

        self.dashboard <= w.label(
            'Resting state and noise acquisition<br><br>', 'headline4')

        for i, task_id in enumerate(TASKS):
            title = TASKS[task_id][0]

            if i < 2:
                value = 0.1
            else:
                value = 0
            self.dashboard <= w.slider(
                title, min=0, max=5, step=0.1, value=value, unit='minutes', id=task_id)

        self.dashboard <= w.switch(
            label='Record EEG',
            checked=False,
            id='record',
        )
        self.dashboard <= w.switch(
            label='External marker synchronizer',
            checked=False,
            on_change=self.synchronizer,
            id='synchronizer',
        )

        self.dashboard <= w.toggle_button([('Start run', self.start), ('Stop run', self.stop)], id='run')

        self.button_start = w.button(
            'Start (space)', outlined=True, on_click=self.syncrhonous_trial, id='syncrhonous-button')

    # ----------------------------------------------------------------------
    def start(self) -> None:
        """Start the run.

        A run consist in a consecutive pipeline trials execution.
        """
        if w.get_value('record'):
            self.start_record()
        self.build_trials()

    # ----------------------------------------------------------------------
    def stop(self) -> None:
        """Stop pipeline execution."""
        self.stop_run()
        self.stop_pipeline()

    # ----------------------------------------------------------------------
    def stop_run(self) -> None:
        """Stop pipeline execution."""
        # self.soa()
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
        self.trials = []
        self.pipeline_trial = []

        for trial in TASKS:

            if w.get_value(trial):
                
                logging.warning(w.get_value(trial))
                
                self.trials.append([{'title': TASKS[trial][0],
                                     'label': TASKS[trial][1],
                                     'instruction': TASKS[trial][2],
                                     }])

                self.pipeline_trial.append([
                    ('prepare', 1500),
                    ('trial', w.get_value(trial) * 60 * 1000),
                    ('end_trial', 1000),
                ])

        self.trial_instruction(**self.trials[0][0])

    # ----------------------------------------------------------------------
    @DeliveryInstance.rboth
    def syncrhonous_trial(self) -> None:
        """Start a trial after subject decision."""

        if self.mode == 'dashboard':
            pipeline_trial = self.pipeline_trial.pop(0)
            trial = self.trials.pop(0)
            self.run_pipeline(pipeline_trial, trial,
                              callback='wrap_trial_instruction')

    # ----------------------------------------------------------------------
    def wrap_trial_instruction(self):
        """"""
        try:
            self.trial_instruction(**self.trials[0][0])
        except:
            pass

    # ----------------------------------------------------------------------
    @DeliveryInstance.both
    def trial_instruction(self, title: str, label: str, instruction: str) -> None:
        """Show the trial instructions to the subject."""
        self.stimuli_area.clear()
        self.show_cross()
        self.stimuli_area <= w.label(label, 'headline2', id='hint')
        self.stimuli_area <= w.label(instruction, 'headline2', id='hint2')

        self.stimuli_area <= self.button_start
        keypress(self.handle_response, timeout=None)

    # ----------------------------------------------------------------------
    def handle_response(self, response: str) -> None:
        """Key pressed."""
        if response == ' ':
            self.syncrhonous_trial()

    # ----------------------------------------------------------------------
    def prepare(self, title: str, label: str, instruction: str) -> None:
        """A small pause before acquisition."""
        self.stimuli_area.clear()
        self.show_cross()

    # ----------------------------------------------------------------------
    def trial(self, title: str, label: str, instruction: str) -> None:
        """Full trial."""
        self.beep(1)
        self.send_marker(f'{title} | Start')

    # ----------------------------------------------------------------------
    def end_trial(self, title, label, instruction) -> None:
        """End of trial."""
        self.beep(2)
        self.send_marker(f'{title} | End')

        logging.warning(len(self.pipeline_trial))
        if not len(self.pipeline_trial):
            self.stop()

    # ----------------------------------------------------------------------
    def synchronizer(self, value: bool) -> None:
        """Show or hide synchronizer."""
        if value:
            self.show_synchronizer()
        else:
            self.hide_synchronizer()

    # ----------------------------------------------------------------------
    def beep(self, n=1) -> None:
        """Play `n` beeps."""
        note = 'C#6'
        gain = 0.1
        duration = 100

        t(note, duration, gain)
        if n > 1:
            for i in range(1, n):
                timer.set_timeout(
                    lambda: t(note, duration, gain), (duration + 50) * i)


if __name__ == '__main__':
    RestingNoiseAcquisition()


