from bci_framework.extensions.stimuli_delivery import StimuliServer, StimuliAPI
from bci_framework.extensions.stimuli_delivery.utils import Widgets
from browser import document, html
import logging

########################################################################
class StimuliDelivery(StimuliAPI):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)

        self.build_areas()
        self.stimuli_area <= html.H3('Stimuli area')
        self.dashboard <= html.H3('Dashboard')

        self.add_cross()
        self.add_blink_area()
        
        widgets = Widgets()
        
        self.dashboard <= widgets.button('Button 2', on_click=self.on_button)

        
    # ----------------------------------------------------------------------
    def on_button(self):
        """"""
        logging.warning("Message")

    if __name__ == '__main__':
        StimuliServer('StimuliDelivery')


