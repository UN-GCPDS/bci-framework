from bci_framework.extensions.stimuli_delivery import StimuliServer, StimuliAPI, DeliveryInstance
from bci_framework.extensions.stimuli_delivery.utils import Widgets

from browser import html, timer
import random

UNICODE_HINTS = {
    'Right': '&#x1f86a;',
    'Left': '&#x1f868;',
    'Up': '&#x1f869;',
    'Bottom': '&#x1f86b;',
}


########################################################################
class FourClassMotorImagery(StimuliAPI):

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        self.add_stylesheet('styles.css')

        self.build_areas()
        self.add_cross()
        self.add_blink_area()
        self.add_run_progressbar()
        
        self.widgets = Widgets()

        self.dashboard <= self.widgets.label('BCI 4-Class motor imagery<br>', 'headline4')
        
        self.dashboard <= self.widgets.checkbox('Cues', [[cue, True] for cue in UNICODE_HINTS], on_change=None, id='cues')

        self.dashboard <= self.widgets.slider(label='Repetitions by class:', min=1, max=40, value=10, step=1, discrete=True, marks=True, id='repetitions')
        self.dashboard <= self.widgets.slider(label='Stimulus duration', min=1000, max=8000, value=4000, step=100, unit='ms', id='duration')
        self.dashboard <= self.widgets.range_slider('Delay duration', min=500, max=2000, value_lower=700, value_upper=1500, step=100, unit='ms', id='pause')

        self.dashboard <= self.widgets.switch('Record EEG', checked=False, on_change=None, id='record')
        # self.dashboard <= self.widgets.button('Test Left', on_click=lambda: self.trial('Left', 1000), style={'margin': '0 15px'})
        # self.dashboard <= self.widgets.button('Test Right', on_click=lambda: self.trial('Right', 1000), style={'margin': '0 15px'})
        self.dashboard <= self.widgets.button('Start run', on_click=self.start, style={'margin': '0 15px'})
        self.dashboard <= self.widgets.button('Stop run', on_click=self.stop, style={'margin': '0 15px'})
        
        
    # ----------------------------------------------------------------------
    def start(self):
        """"""
        if self.widgets.get_value('record'): 
            self.start_record()
        timer.set_timeout(self.run, 2000)
        
    # ----------------------------------------------------------------------
    def stop(self):
        """"""
        timer.clear_timeout(self.timer_cue)
        self.hint.html = ''
        if self.widgets.get_value('record'):
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
        timer.set_timeout(lambda: setattr(self.hint, 'style', {'display': 'none'}), duration)

    # ----------------------------------------------------------------------
    def run(self):
        repetitions = self.widgets.get_value('repetitions')
        self.duration = self.widgets.get_value('duration')
        self.pause = self.widgets.get_value('pause')
        cues = self.widgets.get_value('cues')

        self.hints = []
        for cue in cues:
            self.hints.extend([cue] * repetitions)
        
        self.total_hints = len(self.hints)
        random.shuffle(self.hints)

        self.show_hints()

    # ----------------------------------------------------------------------
    def show_hints(self):
        if self.hints:
            hint = self.hints.pop(0)
            
            self.set_progress(1 - len(self.hints)/self.total_hints)
            
            self.trial(hint, self.duration)
            pause = random.randint(*self.pause)
            self.timer_cue = timer.set_timeout(self.show_hints, self.duration + pause)
        else:
            self.stop()


if __name__ == '__main__':
    StimuliServer('FourClassMotorImagery')


