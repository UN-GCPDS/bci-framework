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

    
        self.dashboard <= w.label('Synchronizer', 'headline4')
        self.dashboard <= w.button('Show synchronizer', on_click=self.show_synchronizer)
        self.dashboard <= w.button('Show synchronizer 2', on_click=lambda :self.show_synchronizer(size=70, position="upper right"))
        self.dashboard <= w.button('Hide synchronizer', on_click=self.hide_synchronizer)
        self.dashboard <= html.HR()
        
        self.dashboard <= w.label('Markers', 'headline4')
        self.dashboard <= w.button('Send marker (blink 100)', on_click=self.m100)
        self.dashboard <= w.button('Send marker (blink 700)', on_click=self.m700)
        self.dashboard <= html.HR()
        
        self.dashboard <= w.label('Annotations', 'headline4')
        self.dashboard <= w.button('Send annotation', on_click=self.annotation)
        self.dashboard <= html.HR()
    
        self.dashboard <= w.label('Fixation cross', 'headline4')
        self.dashboard <= w.button('Show cross', on_click=self.show_cross)
        self.dashboard <= w.button('Hide cross', on_click=self.hide_cross)
        self.dashboard <= html.HR()
        
        self.dashboard <= w.label('Records', 'headline4')
        self.dashboard <= w.button('Start record', on_click=self.start_record)
        self.dashboard <= w.button('Stop record', on_click=self.stop_record)


    # ----------------------------------------------------------------------
    def m100(self):
        self.send_marker('Marker1', blink=100)
        
    # ----------------------------------------------------------------------
    def m700(self):
        self.send_marker('Marker2', blink=700)
        
    # ----------------------------------------------------------------------
    def annotation(self):
        """"""
        self.send_annotation(description="Subject blink", duration=15)





if __name__ == '__main__':
    StimuliDelivery()


