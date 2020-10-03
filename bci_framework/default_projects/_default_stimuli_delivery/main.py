from bci_framework.extensions.stimuli_delivery import StimuliServer, StimuliAPI
from bci_framework.extensions.stimuli_delivery.utils import Widgets
import logging


########################################################################
class StimuliDelivery(StimuliAPI):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        widgets = Widgets()

        self.build_areas()
        self.add_run_progressbar()
        self.add_cross()
        self.add_blink_area()
        
        self.dashboard <= widgets.button('Button', on_click=self.on_button)
        
    # ----------------------------------------------------------------------
    def on_button(self):
        logging.warning("Warning")
        self.set_progress(0.5)
        self.send_marker('MKR', blink=100)
        
        
if __name__ == '__main__':
    StimuliServer('StimuliDelivery')


