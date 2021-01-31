from bci_framework.extensions.stimuli_delivery import StimuliServer, StimuliAPI

from browser import document, html


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

    if __name__ == '__main__':
        StimuliServer('StimuliDelivery')


