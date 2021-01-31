from bci_framework.projects.figure import FigureStream
from bci_framework.projects import properties as prop
from bci_framework.projects.utils import loop_consumer, fake_loop_consumer

import logging
import numpy as np
from scipy.signal import savgol_filter


########################################################################
class Stream(FigureStream):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """"""
        super().__init__()
        t = 10

        self.axis, self.time, self.lines = self.create_lines(mode='accel', time=t, cmap='summer')
        # self.time = np.linspace(-t, 0, self.lines[0].get_ydata().shape[0])
        
        self.raw_lines = np.zeros((len(self.lines), self.time.shape[0]))
        self.axis.set_xlim(-t, 0)

        self.axis.set_title('OpenBCI Accelerometer')
        self.axis.set_xlabel('Time [s]')
        self.axis.set_ylabel('G')

        self.stream()

    # ----------------------------------------------------------------------
    @loop_consumer
    def stream(self, data, topic, frame):
        """"""
        if topic == 'eeg':
            _, aux = data.value['data']
            aux = aux[:, np.argwhere(aux.sum(axis=0) != 0).T[0]]
            aux = aux[:, np.argwhere(aux.sum(axis=0) < 6).T[0]]

            N = aux.shape[1]

            if not N:
                return

            y = []
            for i, line in enumerate(self.lines):
                y_data = self.raw_lines[i]
                y_data = np.roll(y_data, -N)
                y_data[-N:] = aux[i]
                y.append(y_data)
                line.set_data(self.time, savgol_filter(y_data, 101, 4))
                self.raw_lines[i] = y_data
                
            self.feed()
            


if __name__ == '__main__':
    Stream()
