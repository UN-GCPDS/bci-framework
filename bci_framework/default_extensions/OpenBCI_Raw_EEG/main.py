"""
=======
Raw EEG
=======
"""

from bci_framework.extensions.visualizations import EEGStream
from bci_framework.extensions.data_analysis import loop_consumer, fake_loop_consumer
from bci_framework.extensions import properties as prop
import numpy as np


REVERSE_PLOT = True


########################################################################
class RawEEG(EEGStream):

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        DATAWIDTH = 1000
        BUFFER = 30

        if REVERSE_PLOT:
            axis, self.time, self.lines = self.create_lines(mode='eeg',
                time=BUFFER, window=DATAWIDTH)
        else:
            axis, self.time, self.lines = self.create_lines(
                time=-BUFFER, window=DATAWIDTH)
        axis.set_title('Raw EEG')
        axis.set_xlabel('Time')
        axis.set_ylabel('Channels')
        axis.grid(True)
        axis.set_ylim(0, len(prop.CHANNELS) + 1)
        axis.set_yticks(range(1, len(prop.CHANNELS) + 1))
        axis.set_yticklabels(prop.CHANNELS.values())

        self.create_buffer(BUFFER, aux_shape=3, resampling=DATAWIDTH, fill=0)
        if REVERSE_PLOT:
            self.reverse_buffer(axis)
        
        self.stream()
        
    # ----------------------------------------------------------------------
    def autoscale(self, data):
        """"""
        data = data - data.mean()
        data = data / (data.max() - data.min())
        return data
    
    # ----------------------------------------------------------------------
    @loop_consumer('eeg')
    def stream(self):
        eeg = self.buffer_eeg_resampled
        
        for i, line in enumerate(self.lines):
            line.set_data(self.time, self.autoscale(eeg[i])+1+i)
        
        self.feed()


if __name__ == '__main__':
    RawEEG()
