from bci_framework.projects.figure import FigureStream
from bci_framework.projects import properties as prop
from bci_framework.projects.utils import loop_consumer, fake_loop_consumer
import numpy as np
import mne


########################################################################
class Stream(FigureStream):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """"""
        super().__init__()

        self.axis = self.add_subplot(1, 1, 1)
        self.tight_layout()
        self.info = self.get_mne_info()

        self.stream()

    # ----------------------------------------------------------------------
    @loop_consumer
    def stream(self, data, topic, frame):
        """"""

        if topic == 'eeg':

            eeg, _ = data.value['data']

            self.axis.clear()
            mne.viz.plot_topomap(eeg.mean(axis=1) - eeg.mean(), self.info, axes=self.axis, show=False, outlines='skirt', cmap='coolwarm')

            self.feed()


if __name__ == '__main__':
    Stream()
