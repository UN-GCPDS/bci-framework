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

        self.channels = 3

        self.T = 5

        self.axis = self.add_subplot(1, 1, 1)
        self.lines = [self.axis.plot(np.zeros(prop.SAMPLE_RATE * self.T), np.zeros(prop.SAMPLE_RATE * self.T), '-')[0] for i
                      in range(self.channels)]
                      
        self.axis.set_ylim(-30, 30)
        self.axis.set_xlim(-self.T, 0)

        self.stream()

    # ----------------------------------------------------------------------
    @loop_consumer
    # @fake_loop_consumer
    def stream(self, data, topic):
        """"""
        
        if topic == 'eeg':

            _, data = data.value['data']

            data = data[:, [data.mean(axis=0) != 0][0]]
            data = data[:, [np.sum(np.abs(data), axis=0) < 2][0]]

            N = data.shape[1]
        
            self.axis.set_ylim(-5, 5)

            for i, line in enumerate(self.lines):
                 y_data = line.get_ydata()
                 y_data = np.roll(y_data, -N)
                 y_data[-N:] = data[i]
                 line.set_ydata(y_data)
                 line.set_xdata(np.linspace(-self.T, 0, y_data.shape[0]))

            # self.axis.set_xlim(-self.T, 0)
            self.axis.set_ylim(-1.5, 1.5)
            self.axis.legend(['X', 'Y', 'Z'])
        
        
            # logging.warning(data.max())

            self.feed()


if __name__ == '__main__':
    Stream()
