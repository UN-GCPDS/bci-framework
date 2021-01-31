from bci_framework.projects.figure import FigureStream
from bci_framework.projects import properties as prop
from bci_framework.projects.utils import loop_consumer, fake_loop_consumer

import logging
import numpy as np


########################################################################
class Stream(FigureStream):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """"""
        super().__init__()

        t = 30

        self.axis, self.time, self.lines = self.create_lines(mode='eeg', time=t, window='auto', cmap='cool')
        
        self.create_buffer(t, aux_shape=3, fill=np.nan)
        self.create_boundary(self.axis, 0, len(prop.CHANNELS) + 1)
        
        self.axis.set_title('Raw EEG')
        self.axis.set_xlabel('Time [s]')
        self.axis.set_ylabel('Channel')

        self.axis.set_ylim(0, len(prop.CHANNELS)+1)
        self.axis.set_xlim(0, t)
        self.axis.set_yticks(range(1, len(prop.CHANNELS) + 1))
        self.axis.set_yticklabels(prop.CHANNELS.values())
        
        self.stream()

    # ----------------------------------------------------------------------
    @loop_consumer
    def stream(self, data, topic, frame):
        """"""

        if topic == "eeg":

            eeg = self.resample(self.buffer_eeg, self.time.shape[0])
            eeg = self.centralize(eeg, normalize=True)
            
            self.plot_boundary()

            for i, line in enumerate(self.lines):
                line.set_data(self.time, eeg[i] + i + 1)
                
            self.feed()

        elif topic == "marker":
            data = data.value
            logging.warning(data)


if __name__ == '__main__':
    Stream()
