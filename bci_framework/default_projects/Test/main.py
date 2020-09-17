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

        self.L = 1000
        t = 30

        self.create_buffer(t, aux_shape=3, fill=0)

        self.axis, self.time, self.lines = self.create_lines(mode='eeg', time=-t, window=self.L, cmap='cool')

        self.axis.set_title('Raw EEG')
        self.axis.set_xlabel('Time [s]')
        self.axis.set_ylabel('Channel')

        self.axis.set_ylim(0, len(prop.CHANNELS)+1)
        self.axis.set_yticks(range(1, len(prop.CHANNELS) + 1))
        self.axis.set_yticklabels(prop.CHANNELS.values())
        
        self.stream()

    # ----------------------------------------------------------------------
    @fake_loop_consumer
    def stream(self, data, topic, frame):
        """"""

        if topic == "eeg":

            eeg = self.resample(self.buffer_eeg, self.L, axis=1)
            eeg = self.centralize(eeg)

            for i, line in enumerate(self.lines):
                line.set_data(self.time, eeg[i] + i + 1)
                
            self.feed()

        elif topic == "marker":
            data = data.value
            logging.warning(data)


if __name__ == '__main__':
    Stream()
