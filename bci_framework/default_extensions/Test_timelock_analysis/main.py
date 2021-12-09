from bci_framework.extensions.timelock_analysis import TimelockDashboard, TimelockWidget, TimelockSeries, TimelockFilters
from bci_framework.framework.dialogs import Dialogs
import numpy as np
from scipy.signal import decimate

from scipy.fftpack import rfft, rfftfreq
from scipy.signal import welch
import mne

from gcpds.filters import frequency as flt


########################################################################
class LoadDatabase(TimelockSeries):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, height=700, *args, **kwargs):
        """Constructor"""
        super().__init__(height, *args, **kwargs)

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

        self.add_button('Load database',
                        callback=self.load_database, area='top', stretch=0)
        self.add_spacer(area='top')

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

        # Set input manually
        self.pipeline_input = self.datafile

        flt.compile_filters(
            FS=self.pipeline_input.header['sample_rate'], N=2, Q=3)

        self.fit()

    # ----------------------------------------------------------------------
    def fit(self):
        """"""
        datafile = self.pipeline_input

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

        self.pipeline_tunned = True
        self.pipeline_output = datafile


########################################################################
class TimelockTime(TimelockWidget):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, height, *args, **kwargs):
        """Constructor"""
        super().__init__(height, *args, **kwargs)

        self.ax1 = self.figure.add_subplot(111)

    # ----------------------------------------------------------------------
    def fit(self):
        """"""

        epochs = self.pipeline_input.epochs()

        self.ax1.clear()
        self.ax1.plot(data[0])
        self.draw()


########################################################################
class EpochsVisualization(TimelockWidget):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, height=700, *args, **kwargs):
        """Constructor"""
        super().__init__(height, *args, **kwargs)

        self.ax1 = self.figure.add_subplot(111)
        self.pipeline_tunned = True

    # ----------------------------------------------------------------------
    def fit(self):
        """"""
        self.clear_widgets()
        markers = list(self.pipeline_input.file.markers.keys())
        channels = list(self.pipeline_input.header['channels'].values())

        self.tmin = self.add_spin('tmin', 0, suffix='s', min_=-99,
                                  max_=99, callback=self.get_epochs, area='top', stretch=0)
        self.tmax = self.add_spin(
            'tmax', 1, suffix='s', min_=-99, max_=99, callback=self.get_epochs, area='top', stretch=0)
        self.method = self.add_combobox(label='Method', items=[
                                        'mean', 'median'], callback=self.get_epochs, area='top', stretch=0)

        self.add_spacer(area='top', fixed=50)

        self.reject = self.add_spin('Reject', 200, suffix='vpp', min_=0,
                                    max_=500, step=10, callback=self.get_epochs, area='top', stretch=0)
        self.flat = self.add_spin('Flat', 10, suffix='vpp', min_=0, max_=500,
                                  step=10, callback=self.get_epochs, area='top', stretch=0)

        self.add_spacer(area='top')

        self.checkbox = self.add_checkbox(
            'Markers', markers, callback=self.get_epochs, area='left', ncol=1, stretch=1)
        self.add_spacer(area='left')

        self.channels = self.add_channels(
            'Channels', channels, callback=self.get_epochs, area='right', stretch=1)
        self.add_spacer(area='right')

    # ----------------------------------------------------------------------

    def get_epochs(self, *args, **kwargs):
        """"""
        self.figure.clear()
        self.ax1 = self.figure.add_subplot(111)

        markers = sorted([ch.text()
                          for ch in self.checkbox if ch.isChecked()])
        channels = sorted([ch.text()
                           for ch in self.channels if ch.isChecked()])

        if not markers:
            return

        if not channels:
            return

        if self.reject.value() < self.flat.value():
            return

        epochs = self.pipeline_input.epochs(
            tmin=self.tmin.value(), tmax=self.tmax.value(), markers=markers)

        reject = {'eeg': self.reject.value()}
        flat = {'eeg': self.flat.value()}
        epochs.drop_bad(reject, flat)

        evokeds = {}
        for mk in markers:
            erp = epochs[mk].average(
                method=self.method.currentText(), picks=channels)
            evokeds[mk] = erp

        try:
            mne.viz.plot_compare_evokeds(evokeds, axes=self.ax1, cmap=(
                'Class', 'cool'), show=False, show_sensors=False, invert_y=True, styles={}, split_legend=False, legend='upper center')
        except:
            pass

        self.draw()


########################################################################
class Analysis(TimelockDashboard):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """Constructor"""
        super().__init__(*args, **kwargs)

        self.add_widgets((LoadDatabase, {'height': 1.5, 'title': 'Raw EEG signal'}),
                         (TimelockFilters, {
                          'height': 1.5, 'title': 'Filter EEG'}),
                         (EpochsVisualization, {
                          'height': 1.7, 'title': 'Visualize epochs'}),
                         # {'analyzer': AnalysisWidget,  'row': 1, 'col': 0, 'row_span': 1, 'col_span': 1},
                         # {'analyzer': AnalysisWidget,  'row': 1, 'col': 1, 'row_span': 1, 'col_span': 1},
                         )


if __name__ == '__main__':
    Analysis()


