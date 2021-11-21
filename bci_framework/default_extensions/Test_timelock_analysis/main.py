from bci_framework.extensions.timelock_analysis import TimelockDashboard, TimelockWidget, TimelockSeries
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

    # ----------------------------------------------------------------------
    def load_database(self):
        """"""
        self.datafile = Dialogs.load_database()
        self.fit_propagate(self.datafile)

    # ----------------------------------------------------------------------
    def fit(self, datafile):
        """"""
        self.header = datafile.header
        eeg, timestamp = datafile.data()

        eeg = decimate(eeg, 15, axis=1)
        timestamp = np.linspace(
            0, timestamp[0][-1], eeg.shape[1], endpoint=True) / 1000

        eeg = eeg / 1000

        options = [self._get_seconds_from_human(
            w) for w in self.window_options]
        l = len([o for o in options if o < timestamp[-1]])
        self.combobox.addItems(self.window_options[:l])

        self.set_data(timestamp, eeg,
                      labels=list(self.header['channels'].values()),
                      ylabel='Millivolt [$mv$]',
                      xlabel='Time [$s$]')

        datafile.close()

    # ----------------------------------------------------------------------
    @property
    def output(self):
        """"""
        return self.datafile.data()

    # # ----------------------------------------------------------------------
    # def set_next_pipeline(self, fn):
        # """"""
        # self.next_pipeline = fn

    # # ----------------------------------------------------------------------
    # def propagate(self):
        # """"""
        # self.next_pipeline(self.output)


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
class TimelockFilters(TimelockWidget):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, height, *args, **kwargs):
        """Constructor"""
        super().__init__(height, *args, **kwargs)

        gs = self.figure.add_gridspec(1, 2)
        self.ax1 = gs.figure.add_subplot(gs[:, 0:-1])
        self.ax2 = gs.figure.add_subplot(gs[:, -1])
        # self.ax2.get_yaxis().set_visible(False)

        # self.ax1 = self.figure.add_subplot(111)

        self.figure.subplots_adjust(left=0.05,
                                    bottom=0.12,
                                    right=0.95,
                                    top=0.8,
                                    wspace=None,
                                    hspace=0.6)

        self.filters = {'Notch': 'none',
                        'Bandpass': 'none',
                        }

        self.notchs = ('none', '50 Hz', '60 Hz')
        self.bandpass = ('none', 'delta', 'theta', 'alpha', 'beta',
                         '5-45 Hz', '3-30 Hz', '4-40 Hz', '2-45 Hz', '1-50 Hz',
                         '7-13 Hz', '15-50 Hz', '1-100 Hz', '5-50 Hz')

        self.add_radios('Notch', self.notchs, callback=self.set_filters,
                        area='top', stretch=0)
        self.add_radios('Bandpass', self.bandpass, callback=self.set_filters,
                        area='top', stretch=1)

        # self.add_slider(callback=self.change_window)

        # self.set_window_width_options(['10 Hz'])
        # self.window_options = ['10 Hz',
                               # '100 Hz',
                               # '1000 Hz',
                               # ]

    # # ----------------------------------------------------------------------
    # def change_window(self, value):
        # """"""
        # self.ax1.set_xlim(0, value)
        # self.draw()

    # ----------------------------------------------------------------------
    def filter_data(self):
        """"""
        # self.data = data
        # self.input_data = data.data()
        self.fit_propagate(self.input_data)

    # ----------------------------------------------------------------------
    def fit(self, input_data):
        """"""
        self.input_data = input_data
        eeg, timestamp = input_data

        for f in self.filters:
            if self.filters[f] != 'none':
                eeg = self.filters[f](eeg, fs=1000, axis=1)

        self.ax1.clear()
        self.ax2.clear()

        # spectrum = np.abs(rfft(eeg, axis=1))
        # w = rfftfreq(spectrum.shape[1], 1 / 1000)

        # t = np.linspace(0, timestamp[0][-1] / 1000, eeg.shape[1])
        t = np.linspace(0, eeg.shape[1], eeg.shape[1], endpoint=True) / 1000

        threshold = max(eeg.max(axis=1) - eeg.min(axis=1)).round()
        for i, ch in enumerate(eeg):
            self.ax2.plot(t, ch + (threshold * i))

        self.ax1.set_xlabel('Frequency [$Hz$]')
        self.ax1.set_ylabel('Amplitude')
        self.ax2.set_xlabel('Time [$s$]')

        self.ax2.set_yticks([threshold * i for i in range(16)])
        self.ax2.set_yticklabels([f'ch{i}' for i in range(16)])

        # self.output_signal = eeg

        w, spectrum = welch(eeg, fs=1000, axis=1,
                            nperseg=1024, noverlap=256, average='median')

        # spectrum = decimate(spectrum, 15, axis=1)
        # w = np.linspace(0, w[-1], spectrum.shape[1])

        for i, ch in enumerate(spectrum):
            self.ax1.fill_between(w, 0, ch, alpha=0.2, color=f'C{i}')
            self.ax1.plot(w, ch, linewidth=2, color=f'C{i}')
            self.ax1.set_xscale('log')

        self.ax1.set_xlim(0, w[-1])
        self.ax2.set_xlim(0, t[-1])
        self.ax1.grid(True)
        self.ax2.grid(True)

        self.draw()

        # self.set_data(w, spectrum, labels=[f'ch{i}' for i in range(
            # 16)], ylabel='Millivolt [$mv$]', xlabel='Time [$s$]')

    # ----------------------------------------------------------------------
    def set_filters(self, group_name, filter_):
        """"""

        if filter_ == 'none':
            self.filters[group_name] = filter_
        else:
            if group_name == 'Notch':
                filter_ = getattr(flt, f'notch{filter_.replace(" Hz", "")}')
            elif group_name == 'Bandpass':
                if filter_ in self.bandpass[1:5]:
                    filter_ = getattr(flt, f'{filter_}')
                else:
                    filter_ = getattr(
                        flt, f'band{filter_.replace(" Hz", "").replace("-", "")}')
            self.filters[group_name] = filter_

        self.filter_data()

    # ----------------------------------------------------------------------
    @property
    def output(self):
        """"""
        return self.output_signal


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
class Analysis(TimelockDashboard):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """Constructor"""
        super().__init__(*args, **kwargs)

        self.add_widgets({'analyzer': LoadDatabase, 'row': 0, 'col': 0, 'row_span': 1, 'col_span': 2},
                         {'analyzer': TimelockFilters, 'row': 1,
                             'col': 0, 'row_span': 1, 'col_span': 2},
                         # {'analyzer': TimelockTime,    'row': 1, 'col': 1, 'row_span': 1, 'col_span': 1},
                         # {'analyzer': AnalysisWidget,  'row': 1, 'col': 0, 'row_span': 1, 'col_span': 1},
                         # {'analyzer': AnalysisWidget,  'row': 1, 'col': 1, 'row_span': 1, 'col_span': 1},
                         )


if __name__ == '__main__':
    Analysis()


