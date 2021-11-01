from bci_framework.extensions.stimuli_delivery import StimuliAPI
from bci_framework.extensions.stimuli_delivery.utils import Widgets as w
import logging


########################################################################
class StimuliDelivery(StimuliAPI):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_stylesheet('styles.css')

        self.show_cross()
        self.show_synchronizer()

        self.dashboard <= w.button('Button', on_click=self.on_button)

    # ----------------------------------------------------------------------
    def on_button(self):
        logging.warning("Warning")
        self.send_marker('Marker', blink=100)


if __name__ == '__main__':
    StimuliDelivery()


