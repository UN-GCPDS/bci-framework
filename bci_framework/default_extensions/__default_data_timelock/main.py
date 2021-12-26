from bci_framework.extensions.timelock_analysis import TimelockAnalysis
import logging
import sys

import matplotlib
matplotlib.use('Qt5Agg')

from matplotlib import pyplot as plt


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.widgets import Button


class Analysis(FigureCanvasQTAgg):

    def __init__(self, *args, **kwargs):
        """"""

        fig = Figure(*args, **kwargs)
        super().__init__(fig)

        self.axes1 = fig.add_subplot(121)

        self.axes2 = fig.add_subplot(122)


if __name__ == '__main__':
    Analysis()


plt.show()

