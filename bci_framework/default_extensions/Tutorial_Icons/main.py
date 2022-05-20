from bci_framework.extensions.stimuli_delivery import StimuliAPI
from bci_framework.extensions.stimuli_delivery.utils import Widgets as w
from bci_framework.extensions.stimuli_delivery.utils import icons
import logging


########################################################################
class StimuliDelivery(StimuliAPI):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_stylesheet('styles.css')

        self.dashboard <= icons.fa('fa-arrow-right')
        self.dashboard  <= icons.bi('bi-arrow-right')
        self.dashboard  <= icons.mi('face', size=24)


            
            
if __name__ == '__main__':
    StimuliDelivery()


