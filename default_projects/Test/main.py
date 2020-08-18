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

        self.subsample = 32
        t = 30

        self.axis = self.add_subplot(1, 1, 1)
        self.tight_layout(rect=[0.03, 0.03, 1, 0.95])

        lines = [self.axis.plot(np.zeros(100), np.zeros(100), '-')[0]
                 for i in range(5)]
        self.axis.set_xlim(-t, 0)

        self.axis.legend()

        self.axis.set_title('External inputs')
        self.axis.set_xlabel('Time [s]')
        self.axis.set_ylabel('Amplitude')

        self.axis.grid(True)

        # self.axis.set_aspect('auto')

        self.stream()

    # ----------------------------------------------------------------------
    @fake_loop_consumer
    def stream(self, data, topic):
        """"""

        self.feed()


if __name__ == '__main__':
    Stream()


