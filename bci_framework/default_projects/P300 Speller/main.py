from bci_framework.extensions.stimuli_delivery import StimuliServer, StimuliAPI, DeliveryInstance
from bci_framework.extensions.stimuli_delivery.utils import Widgets, Tone

from browser import document, html, timer
import random


CHARACTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
ON = 1
OFF = 0.3



########################################################################
class P300Speller(StimuliAPI):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        self.add_stylesheet('styles.css')
        
        self.build_areas()
        self.add_run_progressbar()
        self.widgets = Widgets()
        self.tone = Tone()
        
        self.stimuli_area.style = {'background-color': 'black'}
        
        self.build_grid()
        
        self.dashboard <= self.widgets.label('P300 Speller <br><br>', 'headline4')
        
        self.dashboard <= self.widgets.slider(label='Trials:', min=1, max=20, value=15, step=1, discrete=True, marks=True, id='trials')
        self.dashboard <= self.widgets.slider(label='Flash duration:', min=100, max=500, value=125, step=5, unit='ms', id='duration')
        self.dashboard <= self.widgets.slider(label='Inter stimulus interval:', min=10, max=500, value=62.5, step=5, unit='ms', id='isi')
        
        self.dashboard <= self.widgets.switch('Record EEG', checked=False, on_change=None, id='record')
        
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
        self.trials = 0
        if hasattr(self, 't0'):
            timer.clear_timeout(self.t0)
        if hasattr(self, 't1'):
            timer.clear_timeout(self.t1)
        
        if self.widgets.get_value('record'):
            timer.set_timeout(self.stop_record, 2000)
        
    # ----------------------------------------------------------------------
    def run(self):
        """"""
        self.isi = self.widgets.get_value('isi')
        self.duration = self.widgets.get_value('duration')
        self.trials = self.widgets.get_value('trials')
        self.progress = 0

        self.trial(self.isi, self.duration, self.trials)
    
    # ----------------------------------------------------------------------
    def trial(self, isi, duration, trials):
        """"""
        self.stimuli_array = []
        for i in range(6):
            self.stimuli_array.extend([f'.col-{i}', f'.row-{i}'])
        random.shuffle(self.stimuli_array)    
    
        self.progress += 1
        self.set_progress(self.progress / (trials + 1))
        
        target = [random.randint(0, 5), random.randint(0, 5)]
        self.show_target(target)
        
        timer.set_timeout(lambda :self.show_trial(isi, duration, trials), 3000)
        
        
    # ----------------------------------------------------------------------
    @DeliveryInstance.both
    def show_target(self, target):
        """"""
        target = document.select_one(f'.col-{target[0]}.row-{target[1]}')
        target.style = {'color': '#00ff00', 'opacity': 0.5}
        self.send_marker(target.text) 
        self.tone("C#6", 200)
        target_off = lambda :setattr(target, 'style', {'color': '#ffffff', 'opacity': OFF})
        timer.set_timeout(target_off, 1000)
            
    # ----------------------------------------------------------------------
    @DeliveryInstance.both
    def show_trial(self, isi, duration, trials):
        """"""
        if self.stimuli_array:
            chars = self.stimuli_array.pop(0)            
            self.activate(chars, duration)
            self.t0 = timer.set_timeout(lambda :self.show_trial(isi, duration, trials), isi+duration)
            
        elif self.trials > 1:
            self.trials -= 1
            self.t1 = timer.set_timeout(lambda :self.trial(isi, duration, trials), 2000)
            
        else:
            timer.set_timeout(lambda :self.tone("C#6", 100), 1000)
            timer.set_timeout(lambda :self.tone("C#6", 100), 1150)
            timer.set_timeout(self.stop, 2000)
        
    # ----------------------------------------------------------------------
    @DeliveryInstance.both
    def activate(self, chars, duration=100):
        """"""    
        self.send_marker(chars[1:].upper()) 
        [setattr(element, 'style', {'opacity': ON}) for element in document.select(chars)]
        turn_off = lambda :[setattr(element, 'style', {'opacity': OFF}) for element in document.select(chars)]
        timer.set_timeout(turn_off, duration)
        
    # ----------------------------------------------------------------------
    def build_grid(self):
        """"""
        table = html.TABLE(CLass='p300')
        tr = html.TR()
        table <= tr
        
        for i, char in enumerate(CHARACTERS):
            col = i // 6
            row = i % 6
            tr <= html.TD(char, Class=f'p300-char col-{col} row-{row}')
            if i != 0 and not (i+1) % 6:
                tr = html.TR()
                table <= tr
        self.stimuli_area <= table
        
        
    if __name__ == '__main__':
        StimuliServer('P300Speller')


