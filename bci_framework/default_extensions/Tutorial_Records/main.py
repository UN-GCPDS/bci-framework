from bci_framework.extensions.stimuli_delivery import StimuliAPI
from bci_framework.extensions.stimuli_delivery.utils import Widgets as w


########################################################################
class StimuliDelivery(StimuliAPI):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.dashboard <= w.button('Start record', on_click=self.on_start_record)
        self.dashboard <= w.button('Stop record', on_click=self.on_stop_record)
        
    # ----------------------------------------------------------------------
    def on_start_record(self):
        """"""
        print("Record started")
        self.start_record()

    # ----------------------------------------------------------------------
    def on_stop_record(self):
        """"""
        print("Record stoped")
        self.stop_record()


if __name__ == '__main__':
    StimuliDelivery()


