"""
=================
Analysis Produser
=================
"""

from bci_framework.extensions.data_analysis import DataAnalysis, loop_consumer
from bci_framework.extensions import properties as prop
from scipy.fftpack import fft, fftfreq


########################################################################
class AnalysisProduser(DataAnalysis):
    """Analysis Produser"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        self.create_buffer(seconds=30, resampling=1000)
        self.stream()

    # ----------------------------------------------------------------------
    @loop_consumer('eeg')
    def stream(self):
        """"""
        EEG = fft(self.buffer_eeg, axis=0)
        W = fftfreq(EEG.shape[1], d=1 / prop.SAMPLE_RATE)

        data = {'amplitude': EEG,
                'frequency': W,
                }
        self.generic_produser('spectrum', data)


if __name__ == '__main__':
    AnalysisProduser(enable_produser=True)
