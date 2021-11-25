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
        
        
        self.dashboard <= w.slider(
            label='Stimulus onset asynchronously',
            min=100,
            max=2000,
            value=750,
            step=50,
            unit='ms',
            id='soa',
        )
        
        self.dashboard <= w.slider(
            label='Stimulus duration',
            min=250,
            max=3000,
            value=1000,
            step=50,
            unit='ms',
            id='duration',
        )
        
        self.dashboard <= w.slider(
            label='Stimulus duration',
            min=250,
            max=3000,
            value=1000,
            step=50,
            unit='ms',
            id='duration',
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

        self.dashboard <= w.button('Target left', on_click=lambda: self.stimuli.show_target('left'))
        self.dashboard <= w.button('Target right', on_click=lambda: self.stimuli.show_target('right'))
        self.dashboard <= w.button('Goomba', on_click=self.stimuli.show_goomba)
        self.dashboard <= w.button('Coin', on_click=self.stimuli.show_coin)
        self.dashboard <= w.button('Remove coin', on_click=self.stimuli.remove_coin)
        self.dashboard <= w.toggle_button([('Start marker synchronization', self.start_marker_synchronization), ('Stop marker synchronization', self.start_marker_synchronization)], id='sync')



    # ----------------------------------------------------------------------
    def start(self) -> None:
        """Start the run.

        A run consist in a consecutive trials execution.
        """
        if w.get_value('record'):
            self.start_record()

        self.build_trials()
        timer.set_timeout(lambda: self.run_pipeline(
            self.pipeline_trial, self.trials, callback='stop_run'), 2000)
            
            
    # ----------------------------------------------------------------------
    def stop(self) -> None:
        """Stop pipeline execution."""
        self.stop_pipeline()


    # ----------------------------------------------------------------------
    def stop_run(self) -> None:
        """Stop pipeline execution."""
        self.soa()
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
        trials = ['Right', 'Left'] * 12
        random.shuffle(trials)
        
        goomba = [True] * 4 + [True]*8
        random.shuffle(goomba)
        
        self.trials = [{'cue': trial, 'goomba': g} for trial, g in zip(trials, goomba)]

        self.pipeline_trial = [
            ['soa', 'soa'], 
            ['target', 'get_delay()'],  
            ['abstention', 'duration'],  
        ]

    # ----------------------------------------------------------------------
    def soa(self, *args) -> None:
        """Stimulus onset asynchronously.

        This is a pipeline method, that explains the unused `*args` arguments.
        """
        logging.warning(f'DELAY: {self.delay}')
        self.stimuli.hide()
        
    # ----------------------------------------------------------------------
    def get_delay(self, *args) -> None:
        """"""
        logging.warning('-'*10)
        return self.delay
        
    # ---------------------------------------------------------------------- 
    def target(self, cue: Literal['Right', 'Left'], goomba: bool):
        """"""
        self.stimuli.show_target(cue)
        timer.set_timeout(self.stimuli.hide, 250)
        keypress(self.handle_response)
      
    # ----------------------------------------------------------------------
    def abstention(self, cue, goomba: bool) -> None:
        """Cue visualization.

        This is a pipeline method, that means it receives the respective trial
        as argument each time is called.
        """
        
        logging.warning(f'Goomba: {goomba} | Response: {self.response}')
        
        if goomba:
            if self.response is None:
                logging.warning(f'winner winner chicken dinner!!')
                self.stimuli.show_coin()
                
                # if self.delay > 250:
                    # self.delay -= 50
                    
            elif self.response in ['Right', 'Left']:
                logging.warning(f'Goomba!!')
                self.stimuli.show_goomba()
                
        self.response = None
                
    # ----------------------------------------------------------------------
    def handle_response(self, response: str) -> None:
        """Capture the subject keyboard response."""

        if response == 'q':
            self.response = 'Left'
            logging.warning('KEY: Left')
            
            # self.send_marker(f'Different', blink=None)
        elif response == 'p':
            self.response = 'Right'
            # print("IDENTICAL")
            # self.send_marker(f'Identical', blink=None)
            logging.warning('KEY: Right')
        else:
            self.response = None
            logging.warning('KEY: No-response')
            if self.delay < 750:
                self.delay += 50
            # self.send_marker(f'No-response', blink=None)
            
        logging.warning(f'Response: {self.response}')
            
            
        
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


