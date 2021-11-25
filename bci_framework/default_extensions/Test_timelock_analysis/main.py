from bci_framework.extensions.timelock_analysis import TimelockDashboard, TimelockWidget, TimelockSeries, TimelockFilters
from bci_framework.framework.dialogs import Dialogs
import numpy as np
from scipy.signal import decimate

from scipy.fftpack import rfft, rfftfreq
from scipy.signal import welch


from gcpds.filters import frequency as flt


########################################################################
class LoadDatabase(TimelockSeries):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, height=700, constrained_layout=True):
        """Constructor"""
        super().__init__(height)

        #  Create grid plot
        gs = self.figure.add_gridspec(4, 4)
        self.ax1 = gs.figure.add_subplot(gs[0:-1, :])
        self.ax2 = gs.figure.add_subplot(gs[-1, :])
        self.ax2.get_yaxis().set_visible(False)

        self.figure.subplots_adjust(left=0.05,
                                    bottom=0.12,
                                    right=0.95,
                                    top=0.8,
                                    wspace=None,
                                    hspace=0.6)

        self.add_button(
            'Load database', callback=self.load_database, area='bottom', stretch=0)
        self.set_window_width_options(['500 milliseconds'])

        self.window_options = ['500 milliseconds',
                               '1 second',
                               '5 second',
                               '15 second',
                               '30 second',
                               '1 minute',
                               '5 minute',
                               '10 minute',
                               '30 minute',
                               '1 hour']

        self.database_description = self.add_textarea(
            area='right', stretch=0)

    # ----------------------------------------------------------------------
    def load_database(self):
        """"""
        self.datafile = Dialogs.load_database()
        self.fit_propagate(self.datafile)

    # ----------------------------------------------------------------------
    def fit(self, datafile):
        """"""
        header = datafile.header
        eeg = datafile.eeg
        timestamp = datafile.timestamp

        self.database_description.setText(datafile.description)

        eeg = decimate(eeg, 15, axis=1)
        timestamp = np.linspace(
            0, timestamp[0][-1], eeg.shape[1], endpoint=True) / 1000

        eeg = eeg / 1000

        options = [self._get_seconds_from_human(
            w) for w in self.window_options]
        l = len([o for o in options if o < timestamp[-1]])
        self.combobox.addItems(self.window_options[:l])

        self.set_data(timestamp, eeg,
                      labels=list(header['channels'].values()),
                      ylabel='Millivolt [$mv$]',
                      xlabel='Time [$s$]')

        datafile.close()

    # ----------------------------------------------------------------------
    @property
    def output(self):
        """"""
        return self.datafile


########################################################################
class TimelockTime(TimelockWidget):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, height, *args, **kwargs):
        """Constructor"""
        super().__init__(height, *args, **kwargs)

        self.ax1 = self.figure.add_subplot(111)

    # ----------------------------------------------------------------------
    def fit(self, data):
        """"""

        self.ax1.clear()

        self.ax1.plot(data[0])

        self.draw()

########################################################################


class EpochsVisualization(TimelockWidget):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, height=700, constrained_layout=True):
        """Constructor"""
        super().__init__(height)

        #  Create grid plot
        # gs = self.figure.add_gridspec(4, 4)
        # self.ax1 = gs.figure.add_subplot(gs[0:-1, :])
        # self.ax2 = gs.figure.add_subplot(gs[-1, :])
        # self.ax2.get_yaxis().set_visible(False)

        self.ax1 = self.figure.subplots(111)

        # self.figure.subplots_adjust(left=0.05,
                                    # bottom=0.12,
                                    # right=0.95,
                                    # top=0.8,
                                    # wspace=None,
                                    # hspace=0.6)

        # self.add_button(
            # 'Load database', callback=self.load_database, area='bottom', stretch=0)
        # self.set_window_width_options(['500 milliseconds'])

        # self.window_options = ['500 milliseconds',
                               # '1 second',
                               # '5 second',
                               # '15 second',
                               # '30 second',
                               # '1 minute',
                               # '5 minute',
                               # '10 minute',
                               # '30 minute',
                               # '1 hour']

        # self.database_description = self.add_textarea(
            # area='right', stretch=0)


########################################################################
class Analysis(TimelockDashboard):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """Constructor"""
        super().__init__(*args, **kwargs)

        self.add_widgets({'analyzer': LoadDatabase, 'row': 0, 'col': 0, 'row_span': 1, 'col_span': 2},
                         {'analyzer': TimelockFilters, 'row': 1,
                             'col': 0, 'row_span': 1, 'col_span': 2},
                         # {'analyzer': EpochsVisualization, 'row': 2,
                             # 'col': 0, 'row_span': 1, 'col_span': 2},
                         # {'analyzer': AnalysisWidget,  'row': 1, 'col': 0, 'row_span': 1, 'col_span': 1},
                         # {'analyzer': AnalysisWidget,  'row': 1, 'col': 1, 'row_span': 1, 'col_span': 1},
                         )


if __name__ == '__main__':
    Analysis()


