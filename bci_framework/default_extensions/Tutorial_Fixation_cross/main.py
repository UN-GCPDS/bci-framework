from bci_framework.extensions.stimuli_delivery import StimuliAPI
from bci_framework.extensions.stimuli_delivery.utils import Widgets as w


########################################################################
class StimuliDelivery(StimuliAPI):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_stylesheet('styles.css')

        self.dashboard <= w.button('Show fixation cross', on_click=self.show_fixation_cross)
        self.dashboard <= w.button('Hide fixation cross', on_click=self.hide_fixation_cross)

    # ----------------------------------------------------------------------
    def show_fixation_cross(self):
        self.show_cross()
        
    # ----------------------------------------------------------------------
    def hide_fixation_cross(self):
        self.hide_cross()

if __name__ == '__main__':
    StimuliDelivery()


