"""
============
Raw topoplot
============
"""

from bci_framework.extensions.visualizations import EEGStream
from bci_framework.extensions.data_analysis import loop_consumer, fake_loop_consumer
from bci_framework.extensions import properties as prop
import mne


########################################################################
class Stream(EEGStream):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)

        self.axis = self.add_subplot(1, 1, 1)
        self.info = self.get_mne_info()

        self.stream()

    # ----------------------------------------------------------------------
    @fake_loop_consumer('eeg')
    def stream(self, data, frame):
        """"""
        if (frame % 5) == 0:
            eeg, _ = data
            self.axis.clear()
            mne.viz.plot_topomap(eeg.mean(axis=1) - eeg.mean(), 
                self.info, axes=self.axis, show=False, outlines='skirt', cmap='cool')

            self.feed()


if __name__ == '__main__':
    Stream()



