from bci_framework.extensions.visualizations import EEGStream
from bci_framework.extensions.data_analysis import fake_loop_consumer
from bci_framework.extensions import properties as prop

import numpy as np

class Stream(EEGStream):
    
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        DATAWIDTH = 1000

        self.axis, self.time, self.lines = self.create_lines(time=30, window=DATAWIDTH)
        self.axis.set_title('Raw EEG')
        self.axis.set_xlabel('Time')
        self.axis.set_ylabel('Channels')
        self.axis.grid(True)
        self.axis.set_ylim(0, len(prop.CHANNELS) + 1)
        self.axis.set_yticks(range(1, len(prop.CHANNELS) + 1))
        self.axis.set_yticklabels(prop.CHANNELS.values())

        self.create_buffer(30, resampling=DATAWIDTH, fill=np.nan)
        self.reverse_buffer(self.axis)
        self.stream()

    @fake_loop_consumer('eeg')
    def stream(self):
        eeg = self.buffer_eeg_resampled
        for i, line in enumerate(self.lines):
            line.set_data(self.time, eeg[i] + 1 + i)
        self.feed()

if __name__ == '__main__':
    Stream()