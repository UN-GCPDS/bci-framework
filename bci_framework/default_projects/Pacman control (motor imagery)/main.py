from bci_framework.extensions.stimuli_delivery import StimuliServer, StimuliAPI, DeliveryInstance
from bci_framework.extensions.stimuli_delivery.utils import Widgets
import logging
from pacman import create_pacman
from browser import document
from  browser import html, timer

import random


HINTS = [
    'Right',
    'Left',
    'Up',
    'Bottom',
]


########################################################################
class StimuliDelivery(StimuliAPI):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_stylesheet('styles.css')
        
        self.widgets = Widgets()

        self.build_areas()
        self.add_run_progressbar()
        self.add_cross()
    
        self.stimuli_area <= create_pacman()
        
        

        self.dashboard <= self.widgets.label('Pacman (motor imagery)<br>', 'headline4')
        
        self.dashboard <= self.widgets.checkbox('Cues', [[cue, True] for cue in HINTS], on_change=None, id='cues')

        self.dashboard <= self.widgets.slider(label='Repetitions by class:', min=1, max=40, value=10, step=1, discrete=True, marks=True, id='repetitions')
        # self.dashboard <= self.widgets.slider(label='Stimulus duration', min=1000, max=8000, value=4000, step=100, unit='ms', id='duration')
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
    def run(self):
        repetitions = self.widgets.get_value('repetitions')
        self.duration = 4010
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
            
            self.trial(hint)
            pause = random.randint(*self.pause)
            self.timer_cue = timer.set_timeout(self.show_hints, self.duration + pause)
        else:
            self.stop()
            
            
    # ----------------------------------------------------------------------
    @DeliveryInstance.both
    def trial(self, hint):

        self.send_marker(hint)

        self.to_center()  
        timer.set_timeout(getattr(self, f'on_{hint.lower()}'), 10)
        

    # ----------------------------------------------------------------------
    def on_right(self):
        pacman = document.select_one('.pacman')
        pacman.class_name += ' pacman-walk_right'
        
        for i in range(20):
            style = {
            'position': 'absolute',
            'top': 'calc(50% - 8px)',
            'left': f'calc(50% - 8px + 80px + {i*45}px)',
            'z-index': 50,
            }
            self.stimuli_area <= html.DIV(Class='food food__float', style=style)
                  
    
    # ----------------------------------------------------------------------
    def on_left(self):
        """"""
        pacman = document.select_one('.pacman')
        pacman.class_name += ' pacman-walk_left'
        
        for i in range(20):
            style = {
            'position': 'absolute',
            'top': 'calc(50% - 8px)',
            'left': f'calc(50% - 8px - 80px - {i*45}px)',
            'z-index': 50,
            }
            self.stimuli_area <= html.DIV(Class='food food__float', style=style)   
         
        
        
    # ----------------------------------------------------------------------
    def on_up(self):
        pacman = document.select_one('.pacman')
        pacman.class_name += ' pacman-walk_top'
        
        for i in range(20):
            style = {
            'position': 'absolute',
            'left': 'calc(50% - 8px)',
            'top': f'calc(50% - 8px - 80px - {i*45}px)',
            'z-index': 50,
            }
            self.stimuli_area <= html.DIV(Class='food food__float', style=style)        
                


    # ----------------------------------------------------------------------
    def on_bottom(self):
        """"""
        pacman = document.select_one('.pacman')
        pacman.class_name += ' pacman-walk_bottom'
        
        for i in range(20):
            style = {
            'position': 'absolute',
            'left': 'calc(50% - 8px)',
            'top': f'calc(50% - 8px + 80px + {i*45}px)',
            'z-index': 50,
            }
            self.stimuli_area <= html.DIV(Class='food food__float', style=style) 
     
        
    # ----------------------------------------------------------------------
    def to_center(self):
        pacman = document.select_one('.pacman')
        pacman.class_name = 'pacman'

        for element in document.select('.food__float'):
            element.remove()
        
    

        
        
if __name__ == '__main__':
    StimuliServer('StimuliDelivery')


