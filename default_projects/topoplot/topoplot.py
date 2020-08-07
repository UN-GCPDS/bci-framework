from bci_framework.projects.figure import FigureStream
from bci_framework.projects import properties as prop
# from bci_framework.projects.figure import FigureStream, subprocess_this, thread_this
from bci_framework.projects.utils import loop_consumer

import mne

########################################################################
class Stream(FigureStream):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """"""
        super().__init__(figsize=(16, 9), dpi=60)
        self.axis = self.add_subplot(1, 1, 1)
        self.tight_layout()
        self.stream()

    #----------------------------------------------------------------------
    @loop_consumer
    def stream(self, data):
        """"""

        info = mne.create_info(list(prop.MONTAGE.values()), sfreq=prop.SAMPLE_RATE, ch_types="eeg", montage=prop.MONTAGE_NAME)
     

        data = data.value['data']
        data = data[:, ::30]

        self.axis.clear()
        im, c = mne.viz.plot_topomap(data.mean(axis=1), info, axes=self.axis, show=False, outlines='skirt')

        self.feed()


if __name__ == '__main__':
    Stream()
