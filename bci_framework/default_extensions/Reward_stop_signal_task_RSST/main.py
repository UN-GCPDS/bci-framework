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
        
        self.stimuli = Stimuli()
        
        self.stimuli_area <= self.stimuli.canvas
        self.stimuli_area <= self.stimuli.score
        
        self.response = None
        self.delay = 250

        self.show_cross()
        self.show_synchronizer()
        
        self.dashboard <= w.label('Reward stop signal task - RSST', 'headline4')
        self.dashboard <= html.BR()
          
        self.dashboard <= w.range_slider(
            label='Inter stimulus interval',
            min=1000,
            max=3000,
            value_lower=2000,
            value_upper=3000,
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
            label='Trials',
            min=10,
            max=60,
            value=10,
            step=1,
            unit='',
            id='trials',
        )
        
        self.dashboard <= w.slider(
            label='Probability for inhibition',
            min=0.1,
            max=1,
            value=0.3,
            step=0.1,
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
        
        self.dashboard <= w.toggle_button([('Start run', self.start), ('Stop run', self.stop)], id='run')
        
        self.dashboard <= html.BR()

        self.dashboard <= w.button('Target left', on_click=lambda: self.stimuli.show_target('left', w.get_value('stimuli_duration')))
        self.dashboard <= w.button('Target right', on_click=lambda: self.stimuli.show_target('right', w.get_value('stimuli_duration')))
        self.dashboard <= w.button('Fail', on_click=lambda: self.stimuli.show_fail(w.get_value('stimuli_duration')))
        self.dashboard <= w.button('Coin', on_click=lambda: self.stimuli.show_coin(w.get_value('stimuli_duration')))
        self.dashboard <= w.button('Remove coin', on_click=self.stimuli.remove_coin)
        self.dashboard <= w.toggle_button([('Start marker synchronization', self.start_marker_synchronization), ('Stop marker synchronization', self.start_marker_synchronization)], id='sync')



    # ----------------------------------------------------------------------
    def start(self) -> None:
        """Start the run.

        A run consist in a consecutive trials execution.
        """
        if w.get_value('record'):
            self.start_record()
            
        
        self.trials_count = w.get_value('trials')
        timer.set_timeout(self.run_trials, 2000)
        
        
        logging.warning(f'Probability to see an inhibition event: {w.get_value("p")}')
        
            
    # ----------------------------------------------------------------------        
    def run_trials(self) -> None:
        """"""
        self.build_trial(self.get_delay())
        
        logging.warning('#'*32)
        logging.warning(f'Trial: {w.get_value("trials") - self.trials_count}')
        
        if self.trials_count>1:
            self.run_pipeline(self.pipeline_trial, self.trials, callback='run_trials')
        else:
            self.run_pipeline(self.pipeline_trial, self.trials, callback='stop_run')
            
        self.trials_count -= 1
            
            
    # ----------------------------------------------------------------------
    def stop(self) -> None:
        """Stop pipeline execution."""
        self.stop_pipeline()


    # ----------------------------------------------------------------------
    def stop_run(self) -> None:
        """Stop pipeline execution."""
        self.isi()
        if w.get_value('record'):
            timer.set_timeout(self.stop_record, 2000)


    # ----------------------------------------------------------------------
    def build_trial(self, delay=250) -> None:
        """Define the `trials` and `pipeline trials`.

        The `trials` consist (in this case) in a list of cues.
        The `pipeline trials` is a set of couples `(callable, duration)` that
        define a single trial, this list of functions are executed asynchronously
        and repeated for each trial.
        """
        trial = random.choice(['Right', 'Left'])
        goomba = random.choices([True, False], (w.get_value('p'), 1-w.get_value('p')))
        
        self.trials = [{'cue': trial, 'goomba': goomba[0]}]

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
    def target(self, cue: Literal['Right', 'Left'], goomba: bool):
        """"""
        logging.warning(f'Delay: {self.delay}')
        self.previous_response = self.response
        self.response = None
        keypress(self.handle_response, self.get_delay())
        self.stimuli.show_target(cue, w.get_value('stimuli_duration'))
        timer.set_timeout(self.stimuli.hide, 250)
      
    # ----------------------------------------------------------------------
    def inhibition(self, cue, goomba: bool) -> None:
        """Cue visualization.

        This is a pipeline method, that means it receives the respective trial
        as argument each time is called.
        """
        
        logging.warning(f'Inhibition: {goomba} | Response: {self.response}')
        
        if goomba:
            if self.response is None:
                
                if self.delay < 950 and self.previous_response:
                    self.stimuli.show_coin(w.get_value('stimuli_duration'))
                    self.delay += 50
                    logging.warning(f'Coin!')
                else:
                    logging.warning(f'Fail because no previous response')
                    
            elif self.response in ['Right', 'Left']:
                logging.warning(f'Fail!!')
                self.stimuli.show_fail(w.get_value('stimuli_duration'))
                
                if self.delay > 250:
                    self.delay -= 50
                
    # ----------------------------------------------------------------------
    def handle_response(self, response: str) -> None:
        """Capture the subject keyboard response."""

        if response == 'q':
            self.response = 'Left'
            # self.send_marker(f'Different', blink=None)
        elif response == 'p':
            self.response = 'Right'
            # self.send_marker(f'Identical', blink=None)
        else:
            self.response = None
            if self.delay < 750:
                self.delay += 50
            # self.send_marker(f'No-response', blink=None)
            
        logging.warning(f'Response: {self.response}')
        logging.warning(f'Previous Response: {self.previous_response}')
            
            
        
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
            self.show_synchronizer(size=60, type='square', position='upper left')
        else:
            self.hide_synchronizer()
            
            
if __name__ == '__main__':
    StimuliDelivery()


