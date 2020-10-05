from bci_framework.projects.server import StimuliServer, StimuliAPI, DeliveryInstance
from bci_framework.projects import properties as prop

from bci_framework.projects.sound import Tone
from bci_framework.projects.widgets import Widgets
from bci_framework.projects.utils import timeit

from browser import document, timer, html

import random
random.seed(8511)


UNICODE_HINTS = {
    'Right': '&#x1f86a;',
    'Left': '&#x1f868;',
    'Up': '&#x1f869;',
    'Bottom': '&#x1f86b;',
}


########################################################################
class Arrows(StimuliAPI):

    # ----------------------------------------------------------------------
    def __init__(self):
        """"""
        self.add_stylesheet('styles.css')

        self.stimuli_area
        self.dashboard

        self.tone = Tone()

        self.widgets = Widgets()
        self.widgets.add_run_progressbar()

        self.build_dashboard()
        self.add_cross()

    # ----------------------------------------------------------------------
    def build_dashboard(self):
        """"""
        self.dashboard <= self.widgets.title('BCI 4-Class motor imagery', 'headline3', style={'margin-bottom': '15px', 'display': 'flex', })
        self.dashboard <= html.BR()

        self.dashboard <= self.widgets.checkbox('Classes', (['Right', True], ['Left', True], ['Up', True], ['Bottom', True], ), on_change=self.update_observations, id='classes')
        self.dashboard <= self.widgets.slider(label='Repetitions by class:', min=1, max=40, valuenow=10, discrete=True, markers=True, on_change=self.update_observations, id='repetitions')
        self.dashboard <= self.widgets.slider('Stimulus duration', min=1000, max=8000, step=100, valuenow=4000, unit='ms', on_change=self.update_observations, id='duration')

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

        self.update_observations()

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
        self.configure()
        self.tone("C#6", 200)
        timer.set_timeout(lambda: self.start_trial(single=False), 1000)

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
        self.widgets.run_progressbar.mdc.set_progress(1 - (len(self.trials) - 1) / self.total_trials)
        duration = self.widgets.get_value('duration')

        self.show_hint(self.trials.pop(0))
        timer.set_timeout(self.hide_hint, duration)

        if not single and self.trials:
            random_trial_interval = random.randint(1000, 1800)
            print(f'Random trial interval: {random_trial_interval}')
            timer.set_timeout(lambda: self.start_trial(False), duration + random_trial_interval)

        if not single and not self.trials:
            timer.set_timeout(lambda: self.tone("C#6", 200), duration + 1000)

    # ----------------------------------------------------------------------
    @DeliveryInstance.both
    def show_hint(self, trial):
        """"""
        if not hasattr(self, 'hint'):
            self.hint = html.SPAN('', id='hint')
            self.stimuli_area <= self.hint

        self.hint.html = UNICODE_HINTS[trial]
        self.hint.style = {'display': 'flex'}

    # ----------------------------------------------------------------------
    @DeliveryInstance.both
    def hide_hint(self):
        """"""
        self.hint.style = {'display': 'none'}

    # ----------------------------------------------------------------------
    @DeliveryInstance.both
    def change_theme(self, dark):
        """"""
        print(self._bci_mode, dark)
        if dark:
            self.stimuli_area.style = {'background-color': '#000a12', }
        else:
            self.stimuli_area.style = {'background-color': '#f5f5f5', }


if __name__ == '__main__':
    StimuliServer('Arrows')


