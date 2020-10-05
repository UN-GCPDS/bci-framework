from bci_framework.projects.server import StimuliServer, StimuliAPI, DeliveryInstance
from bci_framework.projects import properties as prop
from bci_framework.projects import Tone, Widgets
from bci_framework.projects.utils import timeit

from browser import document, timer, html, window

import time
import random


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
        self.tone = Tone()

        self.build_dashboard()

        self.add_cross()
        self.run_progressbar = self.add_run_progressbar()

        self.add_blink_area()

        # self.show_hint('eye')

    # ----------------------------------------------------------------------
    def build_dashboard(self):
        """"""
        min_ = 0.1
        max_ = 5
        valuenow = 1

        self.dashboard <= self.widgets.title('Resting state and noise acquisition', 'headline3', style={'margin-bottom': '15px', 'display': 'flex', })
        self.dashboard <= html.BR()

        self.dashboard <= self.widgets.switch('Resting with open eyes', True, id='resting_open_switch')
        self.dashboard <= self.widgets.slider('Duration', min=min_, max=max_, step=0.1, valuenow=valuenow, unit='minutes', id='resting_open')
        self.dashboard <= html.BR()

        self.dashboard <= self.widgets.switch('Resting with close eyes', True, id='resting_close_switch')
        self.dashboard <= self.widgets.slider('Duration', min=min_, max=max_, step=0.1, valuenow=valuenow, unit='minutes', id='resting_close')
        self.dashboard <= html.BR()

        self.dashboard <= self.widgets.switch('Eye blinking', True, id='eye_blinking_switch')
        self.dashboard <= self.widgets.slider('Duration', min=min_, max=max_, step=0.1, valuenow=valuenow, unit='minutes', id='eye_blinking')
        self.dashboard <= html.BR()

        self.dashboard <= self.widgets.switch('Eyeball movement up/down', True, id='eyeball_up_down_switch')
        self.dashboard <= self.widgets.slider('Duration', min=min_, max=max_, step=0.1, valuenow=valuenow, unit='minutes', id='eyeball_up_down')
        self.dashboard <= html.BR()

        self.dashboard <= self.widgets.switch('Eyeball movement left/right', True, id='eyeball_left_right_switch')
        self.dashboard <= self.widgets.slider('Duration', min=min_, max=max_, step=0.1, valuenow=valuenow, unit='minutes', id='eyeball_left_right')
        self.dashboard <= html.BR()

        self.dashboard <= self.widgets.switch('Head movement left/right', True, id='head_left_right_switch')
        self.dashboard <= self.widgets.slider('Duration', min=min_, max=max_, step=0.1, valuenow=valuenow, unit='minutes', id='head_left_right')
        self.dashboard <= html.BR()

        self.dashboard <= self.widgets.switch('Jaw clenching', True, id='jaw_clenching_switch')
        self.dashboard <= self.widgets.slider('Duration', min=min_, max=max_, step=0.1, valuenow=valuenow, unit='minutes', id='jaw_clenching')
        self.dashboard <= html.BR()

        button_box = html.DIV(style={'margin-top': '50px', 'margin-bottom': '50px', })
        self.dashboard <= button_box

        button_box <= self.widgets.button('Test single trial', connect=self.single_trial, style={'margin': '0 15px'})
        button_box <= self.widgets.button('Start run', connect=self.start_run, style={'margin': '0 15px'})

    # ----------------------------------------------------------------------
    def configure(self):
        """"""
        self.tasks = [
            ('resting_open',
             '<p>Resting with <b>open</b> eyes</p>',
             '<p>Press the button and close the eyes, the acquisition begins with the single beep, <b>keep eyes closed until two beeps</b>.</p>'
             ),

            ('resting_close',
             '<p>Resting with <b>close</b> eyes</p>',
             '<p>Press the button and close the eyes, the acquisition begins with the single beep, keeped eyes closed until two beeps.</p>'
             ),

            ('eye_blinking',
             '<p>Eyes <b>blinking</b></p>',
             '<p>Press the button and close the eyes, the acquisition begins with the single beep, keeped eyes closed until two beeps.</p>'
             ),

            ('eyeball_up_down',
             '<p>Eyeball movement <b>Up</b> and <b>Down</b></p>',
             '<p>Press the button and close the eyes, the acquisition begins with the single beep, keeped eyes closed until two beeps.</p>'
             ),

            ('eyeball_left_right',
             '<p>Eyeball movement <b>Left</b> and <b>Right</b></p>',
             '<p>Press the button and close the eyes, the acquisition begins with the single beep, keeped eyes closed until two beeps.</p>'
             ),

            ('head_left_right',
             '<p>Head movement <b>Left</b> and <b>Right</b></p>',
             '<p>Press the button and close the eyes, the acquisition begins with the single beep, keeped eyes closed until two beeps.</p>'
             ),

            ('jaw_clenching',
             '<p>Jaw <b>clenching</b></p>',
             '<p>Press the button and close the eyes, the acquisition begins with the single beep, keeped eyes closed until two beeps.</p>'
             ),
        ]

    # ----------------------------------------------------------------------

    def start_run(self):
        """"""
        self.configure()
        self.prepare()

    # ----------------------------------------------------------------------

    def single_trial(self):
        """"""
        self.show_hint()

    # ----------------------------------------------------------------------

    def start_trial(self):
        """"""
        self.prepare()

    # ----------------------------------------------------------------------

    def prepare(self):
        """"""
        self.show_hint()

        self.button_start = self.widgets.button('Start (space)', unelevated=False, outlined=True, style={
            'bottom': '15px',
            'width': '50%',
            'right': '25%',
            'position': 'absolute',
            'color': '#2ca02c',
            'border-color': '#2ca02c',
            'display': 'block',
        }, connect=self.execute)

        self.stimuli_area <= self.button_start

    # ----------------------------------------------------------------------
    def execute(self):
        """"""

        duration = self.widgets.get_value(self.tasks[0][0]) * 60 * 1000
        self.tasks.pop(0)
        self.button_start.remove()

        # start
        timer.set_timeout(lambda: self.tone("C#6", 200), 2000)
        timer.set_timeout(lambda: self.send_marker(self.tasks[0][0], 100), 2000)

        # execution
        timer.set_timeout(lambda: self.tone("C#6", 100), duration + 2000)
        timer.set_timeout(lambda: self.tone("C#6", 100), duration + 2000 + 150)

        # next
        timer.set_timeout(self.prepare, duration + 2250 + 2000)

    # ----------------------------------------------------------------------

    @DeliveryInstance.both
    def show_hint(self):
        """"""

        if not hasattr(self, 'hint'):
            self.hint = self.widgets.title('', 'headline2', id='hint')
            self.stimuli_area <= self.hint
            self.hint2 = self.widgets.title('', 'headline2', id='hint2')
            self.stimuli_area <= self.hint2

        self.hint.html = self.tasks[0][1]
        self.hint2.html = self.tasks[0][2]


if __name__ == '__main__':
    StimuliServer('Resting')


