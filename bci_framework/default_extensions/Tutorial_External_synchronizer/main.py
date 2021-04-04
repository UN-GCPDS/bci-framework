from bci_framework.extensions.stimuli_delivery import StimuliAPI
from bci_framework.extensions.stimuli_delivery.utils import Widgets as w


########################################################################
class StimuliDelivery(StimuliAPI):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_stylesheet('styles.css')

        self.show_synchronizer()

        self.dashboard <= w.button('Blink 100', on_click=self.b100)
        self.dashboard <= w.button('Blink 700', on_click=self.b700)

    # ----------------------------------------------------------------------
    def b100(self):
        self.send_marker('Marker1', blink=100)
        
    # ----------------------------------------------------------------------
    def b700(self):
        self.send_marker('Marker2', blink=700)


if __name__ == '__main__':
    StimuliDelivery()


