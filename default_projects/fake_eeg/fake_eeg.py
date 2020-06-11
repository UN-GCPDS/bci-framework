import time
import logging

import numpy as np

from bci_framework.projects.figure import FigureStream, subprocess_this, thread_this
from bci_framework.projects import properties as prop

#from openbci_stream.consumer import OpenBCIConsumer

from scipy.signal import resample

import os


########################################################################
class Stream():
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """"""

        self.fig = FigureStream(figsize=(16, 9), dpi=60)

        self.axis = self.fig.add_subplot(1, 1, 1)

        self.lines = [self.axis.plot([0]*prop.SAMPLE_RATE, [0]*prop.SAMPLE_RATE, '-')[0] for i in range(16)]
        #self.axis.set_ylim(0, 16)
        # return self.fig.canvas, lines

        self.stream()

    # ----------------------------------------------------------------------
    # @thread_this
    #@subprocess_this
    def stream(self):
        """"""

        T = 30

        while True:

            data = np.random.random(size=(16, 1000))*2
            data = data[:, ::30]

            N = data.shape[1]

            for i, line in enumerate(self.lines):
                y_data = line.get_ydata()
                y_data = np.roll(y_data, -N)
                y_data[-N:] = i + (data[i])
                line.set_ydata(y_data)
                line.set_xdata(np.linspace(-T, 0, y_data.shape[0]))

            # self.output.truncate(0)
            # self.output.seek(0)


            self.axis.set_xlim(-T, 0)
            self.axis.set_ylim(0, 16)
            self.axis.set_yticklabels(prop.MONTAGE.values())



            t0 = time.time()
            self.fig.feed()

            logging.warning('FPS: {:.3f}, Clients: {}, Buffer size: {}'.format(
                1 / (time.time() - t0), self.fig.clients(), self.fig.buffer_size()))


            logging.warning(prop.HOST)




            # fig.print_figure(self.output, format='jpeg')
            # return self.output.getvalue()


if __name__ == '__main__':
    Stream()


# Stream()
