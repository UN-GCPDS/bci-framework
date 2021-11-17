from bci_framework.extensions.timelock_analysis import TimelockDashboard, TimelockWidget
from bci_framework.framework.dialogs import Dialogs
import numpy as np


########################################################################
class LoadDatabase(TimelockWidget):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, height=None):
        """Constructor"""
        super().__init__(height)

        self.ax1 = self.figure.add_subplot(111)

        # self.figure.subplots_adjust(
            # left=0.2, bottom=None, right=None, top=None, wspace=None, hspace=None)

        self.add_button('Load database', self.draw_plot, 'top')

    # ----------------------------------------------------------------------
    def draw_plot(self):
        """"""

        self.out = Dialogs.load_database()
        header = self.out.header
        eeg, timestamp = self.out.data()

        self.ax1.clear()
        
        self.ax1.grid(True)
        self.ax1.set_ylim(0, len(header['channels']) + 1)
        self.ax1.set_yticklabels(header['channels'].values())

        scale = 800
        for i, ch in enumerate(eeg):
            self.ax1.plot(timestamp[0], (ch - np.mean(ch)) + (scale * i))
        self.ax1.grid(True)

        self.ax1.set_ylim(0, 800 * 17)
        # self.ax1.legend(loc='center', ncol=2,
                        # labelcolor='k', bbox_to_anchor=(-0.2, 0))

        self.canvas.draw()

        self.out.close()


########################################################################
class AnalysisWidget(TimelockWidget):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, height=None):
        """Constructor"""
        super().__init__(height)

        self.ax1 = self.figure.add_subplot(111)
        self.add_button('Plot', self.draw_plot, 'right')

    # ----------------------------------------------------------------------
    def draw_plot(self):
        """"""
        self.ax1.clear()

        t = np.linspace(0, 1, 1000)
        y = np.sin(2 * np.pi * 10 * t)

        self.ax1.plot(t, y)
        self.ax1.grid(True)

        self.canvas.draw()


########################################################################
class Analysis(TimelockDashboard):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """Constructor"""
        super().__init__(*args, **kwargs)

        self.add_widget(LoadDatabase, 0, 0, 1, 2)
        self.add_widget(AnalysisWidget, 1, 0, 1, 1)
        self.add_widget(AnalysisWidget, 1, 1, 1, 1)


if __name__ == '__main__':
    Analysis()


