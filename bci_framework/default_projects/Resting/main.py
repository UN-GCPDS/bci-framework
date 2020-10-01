from bci_framework.projects.server import StimuliServer, StimuliAPI, DeliveryInstance
from bci_framework.projects import properties as prop
from bci_framework.projects.sound import Tone
from bci_framework.projects.widgets import Widgets
from bci_framework.projects.utils import timeit

from browser import document, timer, html, window

import time
import random
# random.seed(8511)


UNICODE_HINTS = {

    'eye': '&#x1f441;',

}


########################################################################
class Resting(StimuliAPI):

    # ----------------------------------------------------------------------
    def __init__(self):
        """"""
        self.add_stylesheet('styles.css')

        self.stimuli_area
        self.dashboard

        self.on_trial = False

        self.widgets = Widgets()
        self.widgets.add_run_progressbar()

        self.tone = Tone()

        self.build_dashboard()
        # self.add_cross()

        self.show_hint('eye')

    # ----------------------------------------------------------------------
    def add_cross(self):
        """"""
        self.stimuli_area <= html.DIV(Class='cross_contrast')
        self.stimuli_area <= html.DIV(Class='cross')

    # ----------------------------------------------------------------------
    def build_dashboard(self):
        """"""
        self.dashboard <= self.widgets.title('Visual working memory', 'headline3', style={'margin-bottom': '15px', 'display': 'flex', })
        self.dashboard <= html.BR()

    # ----------------------------------------------------------------------
    def show_hint(self, hint):
        """"""

        if not hasattr(self, 'hint'):
            self.hint = html.SPAN('', id='hint')
            self.stimuli_area <= self.hint

        self.hint.html = UNICODE_HINTS[hint]
        self.hint.style = {'display': 'flex'}


if __name__ == '__main__':
    StimuliServer('Resting')


