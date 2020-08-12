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

        self.channels = len(prop.MONTAGE)

        self.axis = self.add_subplot(1, 1, 1)
        self.lines = [self.axis.plot(np.zeros(prop.SAMPLE_RATE), np.zeros(prop.SAMPLE_RATE), '-')[0] for i
                      in range(self.channels)]

        self.stream()

    # ----------------------------------------------------------------------
    @loop_consumer
    # @fake_loop_consumer
    def stream(self, data, topic):
        """"""
        self.T = 30
        
        if topic == "eeg":

             data, aux = data.value['data']
             data = data[:, ::30] * 0.2

             N = data.shape[1]

             for i, line in enumerate(self.lines):
                 y_data = line.get_ydata()
                 y_data = np.roll(y_data, -N)
                 y_data[-N:] = i + data[i]
                 line.set_ydata(y_data)
                 line.set_xdata(np.linspace(-self.T, 0, y_data.shape[0]))

             self.axis.set_xlim(-self.T, 0)
             self.axis.set_ylim(0, self.channels)
             self.axis.set_yticklabels(prop.MONTAGE.values())
             
             self.feed()
             
        elif topic == "marker":
         
            data = data.value
            logging.warning(data)




if __name__ == '__main__':
    Stream()
