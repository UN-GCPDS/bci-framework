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
        super().__init__(figsize=(16, 9), dpi=60)

        t = 30
        self.subsample = 32

        self.axis, self.lines = self.create_lines(mode='eeg', time=t, cmap='cool')
        self.time = np.linspace(-t, 0, self.lines[0].get_ydata().shape[0])

        self.axis.set_title('Raw EEG')
        self.axis.set_xlabel('Time [s]')   
        self.axis.set_ylabel('Channel')    

        self.stream()

    # ----------------------------------------------------------------------
    @loop_consumer
    # @fake_loop_consumer
    def stream(self, data, topic):
        """"""
        if topic == "eeg":

             data, aux = data.value['data']
             N = data.shape[1]

             for i, line in enumerate(self.lines):
                 y_data = line.get_ydata()
                 y_data = np.roll(y_data, -N)
                 y_data[-N:] = i + data[i] - data[i].mean() + 1
                 line.set_data(self.time, y_data)

             self.axis.set_ylim(0, len(prop.CHANNELS)+1)
             self.axis.set_yticks(range(1, 17))
             self.axis.set_yticklabels(prop.CHANNELS.values())

             self.feed()

        elif topic == "marker":

            data = data.value
            logging.warning(data)


if __name__ == '__main__':
    Stream()
