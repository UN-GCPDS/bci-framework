from bci_framework.extensions.stimuli_delivery import StimuliAPI
from bci_framework.extensions.stimuli_delivery.utils import Widgets as w
import logging

from browser import html

########################################################################
class StimuliDelivery(StimuliAPI):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_stylesheet('styles.css')

        self.show_cross()
        self.show_synchronizer()


        self.dashboard <= w.subject_information()
        
        
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

        self.dashboard <= w.button('Send marker', on_click=self.on_button)
        self.dashboard <= w.toggle_button([('Start marker synchronization', self.start_marker_synchronization), ('Stop marker synchronization', self.start_marker_synchronization)], id='sync')


    # ----------------------------------------------------------------------
    def on_button(self):
        logging.warning("Marker")
        self.send_marker('Marker', blink=100)
        
        
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


