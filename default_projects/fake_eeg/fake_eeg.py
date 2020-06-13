import time
import logging

import numpy as np

from bci_framework.projects.figure import FigureStream
from bci_framework.projects import properties as prop
from bci_framework.projects.utils import loop, feed, loop_consumer

from scipy.signal import resample

import os
import json


########################################################################
class Stream(FigureStream):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """"""
        super().__init__(figsize=(16, 9), dpi=60)

        self.channels = len(prop.MONTAGE)

        self.axis = self.add_subplot(1, 1, 1)
        self.lines = [self.axis.plot(
            [0] * prop.SAMPLE_RATE, [0] * prop.SAMPLE_RATE, '-')[0] for i in range(self.channels)]
            
        

        # self.axis.set_xlim(-self.T, 0)
        # self.axis.set_ylim(0, self.channels)
        # self.axis.set_yticklabels(prop.MONTAGE.values())

        self.stream()

    # ----------------------------------------------------------------------
    @loop_consumer
    def stream(self, data):
        """"""
        self.T = 30

        data = data.value['data']
        data = data[:, ::30]

        N = data.shape[1]

        for i, line in enumerate(self.lines):
            y_data = line.get_ydata()
            y_data = np.roll(y_data, -N)
            y_data[-N:] = i + (data[i])
            line.set_ydata(y_data)
            line.set_xdata(np.linspace(-self.T, 0, y_data.shape[0]))

        self.axis.set_xlim(-self.T, 0)
        self.axis.set_ylim(0, self.channels)
        self.axis.set_yticklabels(prop.MONTAGE.values())



if __name__ == '__main__':
    Stream()
