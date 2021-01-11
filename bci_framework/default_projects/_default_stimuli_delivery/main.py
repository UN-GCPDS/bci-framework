from bci_framework.extensions.stimuli_delivery import StimuliServer, StimuliAPI, DeliveryInstance
from bci_framework.extensions.stimuli_delivery.utils import Widgets, Tone


########################################################################
class StimuliDelivery(StimuliAPI):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        
        self.add_stylesheet('styles.css')

        self.stimuli_area
        self.dashboard

        self.widgets = Widgets()
        # self.tone = Tone()

        self.add_cross()
        # self.add_run_progressbar()
        # self.add_blink_area()

        self.build_dashboard()

    # ----------------------------------------------------------------------

    def build_dashboard(self):
        """"""
        self.dashboard <= self.widgets.title('Stimuli Delivery', 'headline3', style={'margin-bottom': '15px', 'display': 'flex', })
        self.dashboard <= html.BR()

    if __name__ == '__main__':
        StimuliServer('StimuliDelivery')


