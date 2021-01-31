from bci_framework.extensions.stimuli_delivery import StimuliServer, StimuliAPI, DeliveryInstance
from bci_framework.extensions.stimuli_delivery.utils import Widgets, Tone

# from radiant.sound import Tone

import random

from browser import document, html, timer


import os
for key in os.environ.keys():
    if key.startswith('BCISTREAM_'):
        print(f'{key}: {os.environ[key]}')



UNICODE_HINTS = {
    'Right': '&#x1f86a;',
    'Left': '&#x1f868;',
    'Up': '&#x1f869;',
    'Bottom': '&#x1f86b;',
}

########################################################################


class ExampleDelivery(StimuliAPI):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)

        self.add_stylesheet('styles.css')

        self.stimuli_area
        self.dashboard

        self.tone = Tone()
        self.widgets = Widgets()
        # self.add_run_progressbar()

        self.add_cross()
        self.build_dashboard()
        self.add_cross()
        self.add_blink_area()

    # ----------------------------------------------------------------------

    def build_dashboard(self):
        """"""
        self.dashboard <= self.widgets.title('BCI 4-Class motor imagery', 'headline3', style={'margin-bottom': '15px', 'display': 'flex', })
        self.dashboard <= html.BR()

        self.dashboard <= self.widgets.checkbox('Classes', (['Right', True], ['Left', True], ['Up', True], ['Bottom', True], ), on_change=self.update_observations, id='classes')
        self.dashboard <= self.widgets.slider(label='Repetitions by class:', min=1, max=40, value=10, step=1, discrete=True, marks=True, on_change=self.update_observations, id='repetitions')
        self.dashboard <= self.widgets.slider(label='Stimulus duration', min=1000, max=8000, value=4000, step=100, unit='ms', on_change=self.update_observations, id='duration')
        self.dashboard <= self.widgets.range_slider('Delay duration', min_lower=500, max_lower=1000, value_lower=700, min_upper=1000, max_upper=2000, value_upper=1500, step=100, unit='ms', on_change=self.update_observations, id='delay')

        self.dashboard <= self.widgets.switch('Dark background', False, id='dark', on_change=self.change_theme)

        self.dashboard <= self.widgets.title('Observations', 'headline4')
        self.dashboard <= html.BR()
        self.observations = self.widgets.title('', 'body1')
        self.dashboard <= self.observations
        self.dashboard <= html.BR()

        button_box = html.DIV(style={'margin-top': '50px', 'margin-bottom': '50px', })
        self.dashboard <= button_box

        button_box <= self.widgets.button('Test single trial', connect=self.single_trial, style={'margin': '0 15px'})
        button_box <= self.widgets.button('Start run', connect=self.start_run, style={'margin': '0 15px'})
        button_box <= self.widgets.button('Stop run', connect=lambda: setattr(self, 'trials', []), style={'margin': '0 15px'})
        button_box <= self.widgets.button('Simple trial', connect=self.test_marker, style={'margin': '0 15px'})

        self.update_observations()

    # ----------------------------------------------------------------------
    def test_marker(self):
        """"""
        self.send_marker('Right', 500)
        # self.show_hint('Right', 1000)

    # ----------------------------------------------------------------------

    def update_observations(self, *args, **kwargs):
        """"""
        duration = self.widgets.get_value('duration') + 1400
        repetitions = self.widgets.get_value('repetitions')
        classes = len(self.widgets.get_value('classes'))

        trials = classes * repetitions
        duration *= trials
        duration = (duration / 1000) / 60

        self.observations.html = f"There will performed <b>{trials}</b> trials per run and will lasts <b>{duration:.1f}</b> minutes."

    # ----------------------------------------------------------------------
    def start_run(self):
        """"""
        self.start_record()
        self.configure()
        self.tone("C#6", 200)
        timer.set_timeout(lambda: self.start_trial(single=False), 3000)

    # ----------------------------------------------------------------------
    def single_trial(self):
        """"""
        self.configure()
        self.start_trial()

    # ----------------------------------------------------------------------
    @DeliveryInstance.both
    def configure(self):
        """"""
        self.propagate_seed()
        repetitions = self.widgets.get_value('repetitions')
        classes = self.widgets.get_value('classes')
        self.trials = classes * repetitions

        self.total_trials = len(self.trials)
        random.shuffle(self.trials)

    # ----------------------------------------------------------------------
    def start_trial(self, single=True):
        """"""
        self.set_progress(1 - (len(self.trials) - 1) / self.total_trials)
        duration = self.widgets.get_value('duration')

        trial = self.trials.pop(0)
        self.show_hint(trial, duration)
        # self.send_marker(trial)

        if not single and self.trials:
            # random_trial_interval = random.randint(1000, 1800)
            random_trial_interval = 500
            print(f'Random trial interval: {random_trial_interval}')
            timer.set_timeout(lambda: self.start_trial(False), duration + random_trial_interval)

        if not single and not self.trials:
            timer.set_timeout(lambda: self.tone("C#6", 200), duration + 1000)
            timer.set_timeout(self.stop_record, duration + 1000 + 3000)

    # ----------------------------------------------------------------------
    # @DeliveryInstance.both
    def show_hint(self, trial, duration):
        """"""
        if not hasattr(self, 'hint'):
            self.hint = html.SPAN('', id='hint')
            self.stimuli_area <= self.hint

        self.hint.html = UNICODE_HINTS[trial]

        self.hint.style = {'display': 'flex'}
        # self.send_marker(trial)
        # timer.set_timeout(self.hide_hint, duration)

    # ----------------------------------------------------------------------
    # @DeliveryInstance.both
    def hide_hint(self):
        """"""
        self.hint.style = {'display': 'none'}

    # ----------------------------------------------------------------------
    @DeliveryInstance.both
    def change_theme(self, dark):
        """"""
        if dark:
            self.stimuli_area.style = {'background-color': '#000a12', }
        else:
            self.stimuli_area.style = {'background-color': '#f5f5f5', }


if __name__ == '__main__':
    StimuliServer('ExampleDelivery',)


