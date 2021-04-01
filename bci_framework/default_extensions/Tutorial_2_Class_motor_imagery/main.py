from bci_framework.extensions.stimuli_delivery import StimuliServer, StimuliAPI, DeliveryInstance
from bci_framework.extensions.stimuli_delivery.utils import Widgets as w

from browser import html, timer
import random

UNICODE_HINTS = {
    'Right': '&#x1f86a;',
    'Left': '&#x1f868;',
}

########################################################################
class TwoClassMotorImagery(StimuliAPI):

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        self.add_stylesheet('styles.css')

        self.build_areas()

        self.dashboard <= w.label(
            'BCI 2-Class motor imagery<br><br>', 'headline4')

        self.dashboard <= w.slider(label='Repetitions by class:', min=1, max=40,
                                   value=10, step=1, discrete=True, marks=True, id='repetitions')
        self.dashboard <= w.slider(label='Stimulus duration', min=1000,
                                   max=8000, value=4000, step=100, unit='ms', id='duration')
        self.dashboard <= w.range_slider(
            'Delay duration', min=500, max=2000, value_lower=700, value_upper=1500, step=100, unit='ms', id='pause')

        self.dashboard <= w.switch(
            'Record EEG', checked=False, on_change=None, id='record')
            
        self.dashboard <= w.button('Start run', on_click=self.start)
        self.dashboard <= w.button('Stop run', on_click=self.stop)
        
        self.dashboard <= html.BR()
        self.dashboard <= w.button('Test Left', on_click=lambda: self.trial('Left', 1000), style={'margin': '0 15px'})
        self.dashboard <= w.button('Test Right', on_click=lambda: self.trial('Right', 1000), style={'margin': '0 15px'})
            
        self.dashboard <= html.BR()
        self.dashboard <= w.button('Show cross', on_click=self.show_cross)
        self.dashboard <= w.button('Hide cross', on_click=self.hide_cross)
        
        self.dashboard <= html.BR()
        self.dashboard <= w.button('Show blink area', on_click=self.show_blink_area)
        self.dashboard <= w.button('Hide blink area', on_click=self.hide_blink_area)

    # ----------------------------------------------------------------------
    def start(self):
        """"""
        if w.get_value('record'):
            self.start_record()
        timer.set_timeout(self.run, 2000)

    # ----------------------------------------------------------------------
    def stop(self):
        """"""
        timer.clear_timeout(self.timer_cue)
        self.hint.html = ''
        if w.get_value('record'):
            timer.set_timeout(self.stop_record, 2000)

    # ----------------------------------------------------------------------
    @DeliveryInstance.both
    def trial(self, hint, duration):
        if not hasattr(self, 'hint'):
            self.hint = html.SPAN('', id='hint')
            self.stimuli_area <= self.hint

        self.send_marker(hint)
        self.hint.html = UNICODE_HINTS[hint]
        self.hint.style = {'display': 'flex'}
        timer.set_timeout(lambda: setattr(
            self.hint, 'style', {'display': 'none'}), duration)

    # ----------------------------------------------------------------------
    def run(self):
        repetitions = w.get_value('repetitions')
        self.duration = w.get_value('duration')
        self.pause = w.get_value('pause')

        self.hints = ['Right'] * repetitions + ['Left'] * repetitions
        random.shuffle(self.hints)

        self.show_hints()

    # ----------------------------------------------------------------------
    def show_hints(self):
        if self.hints:
            hint = self.hints.pop(0)
            self.trial(hint, self.duration)
            pause = random.randint(*self.pause)
            self.timer_cue = timer.set_timeout(
                self.show_hints, self.duration + pause)
        else:
            self.stop()


if __name__ == '__main__':
    StimuliServer('TwoClassMotorImagery')


