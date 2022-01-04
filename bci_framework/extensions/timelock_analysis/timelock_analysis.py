import os
import sys
import logging
import copy
import math
from abc import ABCMeta, abstractmethod

import mne
import numpy as np
# from scipy.fftpack import rfft, rfftfreq
from scipy.signal import welch, decimate
from scipy.signal import decimate, welch

from cycler import cycler
import matplotlib
from matplotlib import pyplot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from PySide6.QtCore import Qt
from PySide6 import QtWidgets
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QSpacerItem, QSizePolicy

from gcpds.filters import frequency as flt
from gcpds.filters import frequency as flt
from bci_framework.framework.dialogs import Dialogs

# from bci_framework.extensions.data_analysis.utils import thread_this, subprocess_this

from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt


# Set logger
logger = logging.getLogger("mne")
logger.setLevel(logging.CRITICAL)
logging.getLogger('matplotlib.font_manager').disabled = True
logging.getLogger().setLevel(logging.WARNING)
logging.root.name = "TimelockAnalysis"

if ('light' in sys.argv) or ('light' in os.environ.get('QTMATERIAL_THEME', '')):
    pass
else:
    pyplot.style.use('dark_background')

try:
    q = matplotlib.cm.get_cmap('cool')
    matplotlib.rcParams['axes.prop_cycle'] = cycler(
        color=[q(m) for m in np.linspace(0, 1, 16)])
    matplotlib.rcParams['figure.dpi'] = 70
    matplotlib.rcParams['font.family'] = 'monospace'
    matplotlib.rcParams['font.size'] = 15
    matplotlib.rcParams['axes.titlecolor'] = '#000000'
    matplotlib.rcParams['xtick.color'] = '#000000'
    matplotlib.rcParams['ytick.color'] = '#000000'
    # matplotlib.rcParams['legend.facecolor'] = 'red'
except:
    # 'rcParams' object does not support item assignment
    pass

LEGEND_KWARGS = {'labelcolor': '#000000',
                 'fontsize': 12,
                 }


# ----------------------------------------------------------------------
def wait_for_it(fn):
    """"""
    # ----------------------------------------------------------------------
    def wrap(*args, **kwargs):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        try:
            fn(*args, **kwargs)
        except Exception as e:
            logging.warning(e)
        QApplication.restoreOverrideCursor()

    return wrap


########################################################################
class Canvas(FigureCanvasQTAgg):

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""

        self.figure = Figure(*args, **kwargs)
        self.configure()

        super().__init__(self.figure)

        # self.figure.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)

    # ----------------------------------------------------------------------
    def configure(self):
        """"""
        # if ('light' in sys.argv) or ('light' in os.environ.get('QTMATERIAL_THEME', '')):
            # pass
        # else:
            # pyplot.style.use('dark_background')

        for ax in self.figure.axes:
            ax.tick_params(axis='x', labelsize=12)
            ax.tick_params(axis='y', labelsize=12)
            ax.xaxis.label.set_size(14)
            ax.yaxis.label.set_size(14)


########################################################################
class TimelockWidget(metaclass=ABCMeta):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, height, *args, **kwargs):
        """Constructor"""

        self.title = ''

        self.bottom_stretch = []
        self.bottom2_stretch = []
        self.top_stretch = []
        self.top2_stretch = []
        self.right_stretch = []
        self.left_stretch = []

        self._pipeline_output = None

        ui = os.path.realpath(os.path.join(
            os.environ['BCISTREAM_ROOT'], 'framework', 'qtgui', 'locktime_widget.ui'))
        self.widget = QUiLoader().load(ui)

        if height:
            self.widget.setMinimumHeight(height)

        self.canvas = Canvas(*args, **kwargs)
        self.figure = self.canvas.figure
        self.widget.gridLayout.addWidget(self.canvas)

    # ----------------------------------------------------------------------
    def draw(self):
        """"""
        self.canvas.configure()
        self.canvas.draw()

    # ----------------------------------------------------------------------
    def _add_spacers(self):
        """"""
        for i, s in enumerate(self.bottom_stretch):
            self.widget.bottomLayout.setStretch(i, s)

        for i, s in enumerate(self.top_stretch):
            self.widget.topLayout.setStretch(i, s)

        for i, s in enumerate(self.bottom2_stretch):
            self.widget.bottom2Layout.setStretch(i, s)

        for i, s in enumerate(self.top2_stretch):
            self.widget.top2Layout.setStretch(i, s)

        for i, s in enumerate(self.right_stretch):
            self.widget.rightLayout.setStretch(i, s)

        for i, s in enumerate(self.left_stretch):
            self.widget.leftLayout.setStretch(i, s)

    # ----------------------------------------------------------------------
    def add_spacer(self, area='top', fixed=None, stretch=0):
        """"""
        if fixed:
            if area in ['left', 'right']:
                getattr(self.widget, f'{area}Layout').addItem(QSpacerItem(
                    20, fixed, QSizePolicy.Minimum, QSizePolicy.Minimum))
            elif area in ['top', 'bottom', 'top2', 'bottom2']:
                getattr(self.widget, f'{area}Layout').addItem(QSpacerItem(
                    fixed, 20, QSizePolicy.Minimum, QSizePolicy.Minimum))
        else:
            if area in ['left', 'right']:
                getattr(self.widget, f'{area}Layout').addItem(QSpacerItem(
                    20, 20000, QSizePolicy.Minimum, QSizePolicy.Expanding))
            elif area in ['top', 'bottom', 'top2', 'bottom2']:
                getattr(self.widget, f'{area}Layout').addItem(QSpacerItem(
                    20000, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        if stretch:
            getattr(self, f'{area}_stretch').append(stretch)

    # ----------------------------------------------------------------------
    def clear_layout(self, layout):
        """"""
        i = -1
        for _ in range(layout.count()):
            i = i + 1
            b = layout.itemAt(i)

            if b is None:
                continue

            if w := b.widget():  # widget
                w.deleteLater()

            if b.spacerItem():  # spacer
                layout.removeItem(b)
                i = i - 1

            if l := b.layout():
                self.clear_layout(l)

            # layout.removeItem(layout.itemAt(i))

            # b = layout.takeAt(2)
                # buttons.pop(2)
                # b.widget().deleteLater()

    # ----------------------------------------------------------------------
    def clear_widgets(self, areas=['left', 'right', 'top', 'bottom', 'top2', 'bottom2']):
        """"""
        for area in areas:
            layout = getattr(self.widget, f'{area}Layout')
            self.clear_layout(layout)

    # ----------------------------------------------------------------------
    def add_textarea(self, content='', area='top', stretch=0):
        """"""
        textarea = QtWidgets.QTextEdit(content)
        textarea.setProperty('class', 'clear')
        textarea.setMinimumWidth(500)
        textarea.setReadOnly(True)
        # if callback:
            # button.clicked.connect(callback)
        getattr(self.widget, f'{area}Layout').addWidget(textarea)
        getattr(self, f'{area}_stretch').append(stretch)
        return textarea

    # ----------------------------------------------------------------------
    def add_button(self, label, callback=None, area='top', stretch=0):
        """"""
        button = QtWidgets.QPushButton(label)
        if callback:
            button.clicked.connect(callback)
        getattr(self.widget, f'{area}Layout').addWidget(button)

        getattr(self, f'{area}_stretch').append(stretch)
        return button

    # ----------------------------------------------------------------------
    def add_radios(self, group_name, radios, cols=None, rows=None, callback=None, area='top', stretch=1):
        """"""
        group = QtWidgets.QGroupBox(group_name)
        group.setProperty('class', 'fill_background')
        vbox = QtWidgets.QVBoxLayout()
        group.setLayout(vbox)

        if cols is None:
            cols = len(radios)

        if rows:
            cols = math.ceil(len(radios) / rows)

        for i, radio in enumerate(radios):
            if (i % cols) == 0:
                hbox = QtWidgets.QHBoxLayout()
                vbox.addLayout(hbox)

            # group.setLayout(hbox)
            r = QtWidgets.QRadioButton()
            r.setText(radio)
            r.setChecked(i == 0)

            def dec(*args):
                def wrap(fn):
                    return callback(*args)
                return wrap

            if callback:
                r.clicked.connect(dec(group_name, radio))

            hbox.addWidget(r)

        getattr(self.widget, f'{area}Layout').addWidget(group)
        getattr(self, f'{area}_stretch').append(stretch)

    # ----------------------------------------------------------------------
    def add_checkbox(self, group_name, checkboxes, cols=None, rows=None, callback=None, area='top', stretch=1):
        """"""
        group = QtWidgets.QGroupBox(group_name)
        group.setProperty('class', 'fill_background')
        vbox = QtWidgets.QVBoxLayout()
        group.setLayout(vbox)

        if cols is None:
            cols = len(checkboxes)

        if rows:
            cols = math.ceil(len(checkboxes) / rows)

        list_radios = []
        for i, checkbox in enumerate(checkboxes):
            if (i % cols) == 0:
                hbox = QtWidgets.QHBoxLayout()
                vbox.addLayout(hbox)

            # group.setLayout(hbox)
            r = QtWidgets.QCheckBox()
            r.setText(checkbox)
            r.setChecked(i == 0)
            list_radios.append(r)

            def dec(*args):
                def wrap(fn):
                    return callback(*args)
                return wrap

            if callback:
                r.clicked.connect(dec(group_name, checkbox))

            hbox.addWidget(r)

        getattr(self.widget, f'{area}Layout').addWidget(group)
        getattr(self, f'{area}_stretch').append(stretch)

        return list_radios

    # ----------------------------------------------------------------------
    def add_channels(self, group_name, channels, callback=None, area='top', stretch=1):
        """"""
        group = QtWidgets.QGroupBox(group_name)
        group.setProperty('class', 'fill_background')
        vbox = QtWidgets.QHBoxLayout()
        group.setLayout(vbox)

        # ncol = len(radios)

        vbox_odd = QtWidgets.QVBoxLayout()
        vbox_z = QtWidgets.QVBoxLayout()
        vbox_even = QtWidgets.QVBoxLayout()

        vbox.addLayout(vbox_even)
        vbox.addLayout(vbox_z)
        vbox.addLayout(vbox_odd)

        list_radios = []
        for channel in channels:

            r = QtWidgets.QCheckBox()
            r.setText(channel)
            r.setChecked(True)
            list_radios.append(r)

            if channel[-1].isnumeric() and int(channel[-1]) % 2 != 0:  # odd
                vbox_even.addWidget(r)
            elif channel[-1].isnumeric() and int(channel[-1]) % 2 == 0:  # even
                vbox_odd.addWidget(r)
            else:
                vbox_z.addWidget(r)

            def dec(*args):
                def wrap(fn):
                    return callback(*args)
                return wrap

            if callback:
                r.clicked.connect(dec(group_name, channel))

        getattr(self.widget, f'{area}Layout').addWidget(group)
        getattr(self, f'{area}_stretch').append(stretch)

        return list_radios

    # ----------------------------------------------------------------------
    def add_scroll(self, callback=None, area='bottom', stretch=0):
        """"""
        scroll = QtWidgets.QScrollBar()
        scroll.setOrientation(Qt.Horizontal)
        # scroll.setMaximum(255)
        scroll.sliderMoved.connect(callback)
        scroll.setProperty('class', 'big')
        # scroll.setPageStep(1000)

        getattr(self.widget, f'{area}Layout').addWidget(scroll)

        getattr(self, f'{area}_stretch').append(stretch)
        return scroll

    # ----------------------------------------------------------------------
    def add_slider(self, callback=None, area='bottom', stretch=0):
        """"""
        slider = QtWidgets.QSlider()
        slider.setOrientation(Qt.Horizontal)
        slider.setMaximum(0)
        slider.setMaximum(500)
        slider.setValue(500)

        slider.valueChanged.connect(callback)

        getattr(self.widget, f'{area}Layout').addWidget(slider)
        getattr(self, f'{area}_stretch').append(stretch)

        return slider

    # ----------------------------------------------------------------------
    def add_spin(self, label, value, decimals=1, step=0.1, prefix='', suffix='', min_=0, max_=999, callback=None, area='top', stretch=0):
        """"""
        spin = QtWidgets.QDoubleSpinBox()

        spin.setDecimals(decimals)
        spin.setSingleStep(step)
        spin.setMinimum(min_)
        spin.setMaximum(max_)
        spin.setValue(value)

        if callback:
            spin.valueChanged.connect(callback)

        if prefix:
            spin.setPrefix(f' {prefix}')
        if suffix:
            spin.setSuffix(f' {suffix}')

        layout = QtWidgets.QHBoxLayout()
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)

        if label:
            layout.addWidget(QtWidgets.QLabel(label))
        layout.addWidget(spin)

        getattr(self.widget, f'{area}Layout').addWidget(widget)
        getattr(self, f'{area}_stretch').append(stretch)

        layout.setStretch(0, 0)
        layout.setStretch(1, 1)

        return spin

    # ----------------------------------------------------------------------
    def add_combobox(self, label, items, editable=False, callback=None, area='top', stretch=0):
        """"""

        combo = QtWidgets.QComboBox()
        combo.addItems(items)
        combo.activated.connect(callback)
        combo.setEditable(editable)
        combo.setMinimumWidth(200)

        layout = QtWidgets.QHBoxLayout()
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        if label:
            layout.addWidget(QtWidgets.QLabel(label))
        layout.addWidget(combo)

        getattr(self.widget, f'{area}Layout').addWidget(widget)
        getattr(self, f'{area}_stretch').append(stretch)

        layout.setStretch(0, 0)
        layout.setStretch(1, 1)

        return combo

    # ----------------------------------------------------------------------
    # @abstractmethod
    @property
    def pipeline_input(self):
        """"""
        if hasattr(self, '_previous_pipeline'):
            return self._previous_pipeline.pipeline_output
        elif hasattr(self, '_pipeline_input'):
            return self._pipeline_input
        else:
            logging.warning("'pipeline_input' does not exist yet.")

    # ----------------------------------------------------------------------
    # @abstractmethod
    @pipeline_input.setter
    def pipeline_input(self, input_):
        """"""
        self._pipeline_input = input_

    # ----------------------------------------------------------------------
    # @abstractmethod
    @property
    def pipeline_output(self):
        """"""
        if hasattr(self, '_pipeline_output'):
            return self._pipeline_output

    # ----------------------------------------------------------------------
    # @abstractmethod
    @pipeline_output.setter
    def pipeline_output(self, output_):
        """"""
        self._pipeline_output = output_
        try:
            self.pipeline_output._original_markers = self.pipeline_output.markers
        except:
            pass
        self._pipeline_propagate()

    # ----------------------------------------------------------------------
    # @abstractmethod
    @property
    def pipeline_tunned(self):
        """"""
        return getattr(self, '_pipeline_tunned', False)

    # ----------------------------------------------------------------------
    # @abstractmethod
    @pipeline_tunned.setter
    def pipeline_tunned(self, value):
        """"""
        self._pipeline_tunned = value

    # ----------------------------------------------------------------------
    def next_pipeline(self, pipe):
        """"""
        self._next_pipeline = pipe
        # self._next_pipeline._pipeline_input = self._pipeline_output

    # ----------------------------------------------------------------------
    def previous_pipeline(self, pipe):
        """"""
        self._previous_pipeline = pipe

    # ----------------------------------------------------------------------
    def set_pipeline_input(self, in_):
        """"""
        self._pipeline_input = in_

    # ----------------------------------------------------------------------
    # @abstractmethod
    def _pipeline_propagate(self):
        """"""
        if hasattr(self, '_next_pipeline'):
            if not self._next_pipeline.pipeline_tunned:
                return

            if next_pipeline := getattr(self, '_next_pipeline', False):
                next_pipeline.fit()

    # ----------------------------------------------------------------------
    @abstractmethod
    def fit(self):
        """"""


########################################################################
class TimelockSeries(TimelockWidget):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, height, *args, **kwargs):
        """Constructor"""
        super().__init__(height, *args, **kwargs)

        self.fill_opacity = 0.2
        self.fill_color = os.environ.get(
            'QTMATERIAL_PRIMARYCOLOR', '#ff0000')

    # ----------------------------------------------------------------------
    def move_plot(self, value):
        """"""
        self.ax1.set_xlim(value / 1000, (value / 1000 + self.window_value))
        self.ax2.collections.clear()
        self.ax2.fill_between([value / 1000, (value / 1000 + self.window_value)],
                              *self.ax1.get_ylim(), color=self.fill_color, alpha=self.fill_opacity)
        self.draw()

    # ----------------------------------------------------------------------
    def change_window(self):
        """"""
        self.window_value = self._get_seconds_from_human(
            self.combobox.currentText())

        eeg = self.pipeline_output.eeg
        timestamp = self.pipeline_output.timestamp

        timestamp = np.linspace(
            0, timestamp[0][-1], eeg.shape[1], endpoint=True) / 1000

        self.scroll.setMaximum((timestamp[-1] - self.window_value) * 1000)
        self.scroll.setMinimum(0)
        self.scroll.setPageStep(self.window_value * 1000)

        self.ax1.set_xlim(self.scroll.value() / 1000,
                          (self.scroll.value() / 1000 + self.window_value))

        self.ax2.collections.clear()
        self.ax2.fill_between([self.scroll.value() / 1000, (self.scroll.value() + self.window_value) / 1000],
                              *self.ax1.get_ylim(),
                              color=self.fill_color,
                              alpha=self.fill_opacity)

        self.draw()

    # ----------------------------------------------------------------------
    def _get_seconds_from_human(self, human):
        """"""
        value = human.replace('milliseconds', '0.001')
        value = value.replace('second', '1')
        value = value.replace('minute', '60')
        value = value.replace('hour', '60 60')
        return np.prod(list(map(float, value.split())))

    # ----------------------------------------------------------------------
    def set_data(self, timestamp, eeg, labels, ylabel='', xlabel='', legend=True):
        """"""
        self.ax1.clear()
        self.ax2.clear()

        for i, ch in enumerate(eeg):
            self.ax1.plot(timestamp, eeg[i], label=labels[i])
            self.ax2.plot(timestamp, eeg[i], alpha=0.5)

        self.ax1.grid(True, axis='x')
        if legend:
            self.ax1.legend(loc='upper center', ncol=8,
                            bbox_to_anchor=(0.5, 1.4), **LEGEND_KWARGS)
        self.ax1.set_xlim(0, self.window_value)

        self.ax2.grid(True, axis='x')
        self.ax2.set_xlim(0, timestamp[-1])
        self.ax2.fill_between([0, self.window_value], *self.ax1.get_ylim(),
                              color=self.fill_color, alpha=self.fill_opacity)

        self.scroll.setMaximum((timestamp[-1] - self.window_value) * 1000)
        self.scroll.setMinimum(0)

        self.ax1.set_ylabel(ylabel)
        self.ax2.set_xlabel(xlabel)
        self.draw()

    # ----------------------------------------------------------------------
    def set_window_width_options(self, options):
        """"""
        self.scroll = self.add_scroll(
            callback=self.move_plot, area='bottom', stretch=1)
        self.combobox = self.add_combobox('', options,
                                          callback=self.change_window,
                                          area='bottom',
                                          stretch=0)
        self.window_value = self._get_seconds_from_human(options[0])


########################################################################
class Filters(TimelockWidget):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, height, *args, **kwargs):
        """Constructor"""
        super().__init__(height, *args, **kwargs)
        self.title = 'Filter EEG'

        gs = self.figure.add_gridspec(1, 2)
        self.ax1 = gs.figure.add_subplot(gs[:, 0:-1])
        self.ax2 = gs.figure.add_subplot(gs[:, -1])
        # self.ax2.get_yaxis().set_visible(False)

        # self.ax1 = self.figure.add_subplot(111)

        self.figure.subplots_adjust(left=0.05,
                                    bottom=0.12,
                                    right=0.95,
                                    top=0.95,
                                    wspace=None,
                                    hspace=0.6)

        self.filters = {'Notch': 'none',
                        'Bandpass': 'none',
                        }

        self.notchs = ('none', '50 Hz', '60 Hz')
        self.bandpass = ('none', 'delta', 'theta', 'alpha', 'beta',
                         '0.01-20 Hz',
                         '5-45 Hz', '3-30 Hz', '4-40 Hz', '2-45 Hz', '1-50 Hz',
                         '7-13 Hz', '15-50 Hz', '1-100 Hz', '5-50 Hz')

        self.add_radios('Notch', self.notchs, callback=self.set_filters,
                        area='top', stretch=0)
        self.add_radios('Bandpass', self.bandpass, callback=self.set_filters,
                        area='top', stretch=0)

        self.scale = self.add_spin('Scale', 150, suffix='uv', min_=0,
                                   max_=1000, step=50, callback=self.fit, area='top',
                                   stretch=0)

    # ----------------------------------------------------------------------
    @wait_for_it
    def fit(self):
        """"""

        eeg = self.pipeline_input.original_eeg
        timestamp = self.pipeline_input.timestamp

        for f in self.filters:
            if self.filters[f] != 'none':
                eeg = self.filters[f](eeg, fs=1000, axis=1)

        self.ax1.clear()
        self.ax2.clear()

        t = np.linspace(0, eeg.shape[1], eeg.shape[1], endpoint=True) / 1000

        channels = eeg.shape[0]

        # threshold = max(eeg.max(axis=1) - eeg.min(axis=1)).round()
        # threshold = max(eeg.std(axis=1)).round()
        threshold = self.scale.value()
        # eeg_d = decimate(eeg, 15, axis=1)
        # timestamp = np.linspace(
            # 0, t[-1], eeg_d.shape[1], endpoint=True)

        for i, ch in enumerate(eeg):
            self.ax2.plot(t, ch + (threshold * i))

        self.ax1.set_xlabel('Frequency [$Hz$]')
        self.ax1.set_ylabel('Amplitude')
        self.ax2.set_xlabel('Time [$s$]')

        self.ax2.set_yticks([threshold * i for i in range(channels)])
        self.ax2.set_yticklabels(
            self.pipeline_input.header['channels'].values())
        self.ax2.set_ylim(-threshold, threshold * channels)

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
        self.ax1.grid(True, axis='y')
        self.ax2.grid(True, axis='x')

        self.draw()

        self.pipeline_tunned = True
        self._pipeline_output = self.pipeline_input
        self._pipeline_output.eeg = eeg.copy()
        self._pipeline_propagate()

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
                        flt, f'band{filter_.replace(" Hz", "").replace("-", "").replace(".", "")}')
            self.filters[group_name] = filter_

        self.fit()

    # # ----------------------------------------------------------------------
    # @property
    # def output(self):
        # """"""
        # if hasattr(self, 'output_signal'):
            # return self.output_signal


########################################################################
class LoadDatabase(TimelockSeries):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, height=700, *args, **kwargs):
        """Constructor"""
        super().__init__(height, *args, **kwargs)

        self.title = 'Raw EEG signal'

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
    @wait_for_it
    def fit(self):
        """"""
        datafile = self.pipeline_input

        header = datafile.header
        eeg = datafile.eeg
        datafile.aux
        timestamp = datafile.timestamp

        self.database_description.setText(datafile.description)

        eeg = decimate(eeg, 15, axis=1)
        timestamp = np.linspace(
            0, timestamp[0][-1], eeg.shape[1], endpoint=True) / 1000

        eeg = eeg / 1000

        options = [self._get_seconds_from_human(
            w) for w in self.window_options]
        l = len([o for o in options if o < timestamp[-1]])
        self.combobox.clear()
        self.combobox.addItems(self.window_options[:l])

        self.set_data(timestamp, eeg,
                      labels=list(header['channels'].values()),
                      ylabel='Millivolt [$mv$]',
                      xlabel='Time [$s$]')

        datafile.close()

        self.pipeline_tunned = True
        self.pipeline_output = datafile


########################################################################
class EpochsVisualization(TimelockWidget):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, height=700, *args, **kwargs):
        """Constructor"""
        super().__init__(height, *args, **kwargs)
        self.title = 'Visualize epochs'

        self.ax1 = self.figure.add_subplot(111)
        self.pipeline_tunned = True

    # ----------------------------------------------------------------------
    def fit(self):
        """"""
        self.clear_widgets()
        markers = sorted(list(self.pipeline_input.markers.keys()))
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
            'Markers', markers, callback=self.get_epochs, area='bottom', stretch=1)
        self.add_spacer(area='bottom')

        self.channels = self.add_channels(
            'Channels', channels, callback=self.get_epochs, area='right', stretch=1)
        self.add_spacer(area='right')

    # ----------------------------------------------------------------------
    @wait_for_it
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

        self.pipeline_output = epochs


########################################################################
class AmplitudeAnalysis(TimelockWidget):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, height, *args, **kwargs):
        """Constructor"""
        super().__init__(height, *args, **kwargs)
        self.title = 'Amplitude analysis'

        self.ax1 = self.figure.add_subplot(111)
        self.pipeline_tunned = True

        self.figure.subplots_adjust(left=0.05,
                                    bottom=0.12,
                                    right=0.95,
                                    top=0.95)

    # ----------------------------------------------------------------------
    @wait_for_it
    def fit(self):
        """"""
        datafile = self.pipeline_input
        t = datafile.timestamp[0] / 1000 / 60

        eeg = datafile.eeg
        eeg = eeg - eeg.mean(axis=1)[:, np.newaxis]

        mx = eeg.max(axis=0)
        mn = eeg.min(axis=0)
        m = eeg.mean(axis=0)

        self.ax1.clear()

        # dc = int(self.decimate.currentText())
        dc = 1000
        mxd = decimate(mx, dc, n=2)
        mnd = decimate(mn, dc, n=2)
        md = decimate(m, dc, n=2)
        td = decimate(t, dc, n=2)

        self.ax1.fill_between(td, mnd, mxd, color='k',
                              alpha=0.3, linewidth=0)
        self.ax1.plot(td, md, color='C0')

        vpps = [100, 150, 200, 300, 500, 0]
        for i, vpp in enumerate(vpps):
            self.ax1.hlines(
                vpp / 2, 0, td[-1], linestyle='--', color=pyplot.cm.tab10(i))
            if vpp:
                self.ax1.hlines(-vpp / 2, 0,
                                td[-1], linestyle='--', color=pyplot.cm.tab10(i))

        self.ax1.set_xlim(0, td[-1])
        self.ax1.set_ylim(2 * mn.mean(), 2 * mx.mean())

        ticks = sorted(vpps + [-v for v in vpps])
        self.ax1.set_yticks([v / 2 for v in ticks])
        self.ax1.set_yticklabels([f'{abs(v)} vpp' for v in ticks])

        self.ax1.grid(True, axis='x')

        self.ax1.set_ylabel('Voltage [uv]')
        self.ax1.set_xlabel('Time [$s$]')

        self.draw()

        self.pipeline_output = self.pipeline_input


########################################################################
class AddMarkers(TimelockSeries):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, height, *args, **kwargs):
        """Constructor"""
        super().__init__(height, *args, **kwargs)
        self.title = 'Add new markers'

        #  Create grid plot
        gs = self.figure.add_gridspec(4, 1)
        self.ax1 = gs.figure.add_subplot(gs[0:-1, :])
        self.ax2 = gs.figure.add_subplot(gs[-1, :])
        self.ax2.get_yaxis().set_visible(False)

        self.figure.subplots_adjust(left=0.05,
                                    bottom=0.12,
                                    right=0.95,
                                    top=0.95,
                                    wspace=None,
                                    hspace=0.6)

        self.set_window_width_options(
            ['500 milliseconds',
             '1 second',
             '5 second',
             '15 second',
             '30 second',
             '1 minute',
             '5 minute',
             '10 minute',
             '30 minute',
             '1 hour'])

        self.markers = self.add_combobox('Marker', [], callback=None, editable=True,
                                         area='bottom2', stretch=3)
        self.add_button('Add marker', callback=self.add_marker,
                        area='bottom2', stretch=0)
        self.add_spacer(area='bottom2', stretch=10)

        # self.database_description = self.add_textarea(
            # area='right', stretch=0)

        self.pipeline_tunned = True

    # ----------------------------------------------------------------------
    def add_marker(self):
        """"""
        q = np.mean(self.ax1.get_xlim())

        self.ax1.vlines(q, * self.ax1.get_ylim(),
                        linestyle='--', color='red', linewidth=5, zorder=99)
        self.ax2.vlines(q, * self.ax2.get_ylim(),
                        linestyle='--', color='red', linewidth=3, zorder=99)

        markers = self._pipeline_output.markers
        markers.setdefault(self.markers.currentText(), []).append(q)
        self._pipeline_output.markers = markers
        self._pipeline_propagate()

        self.draw()

    # ----------------------------------------------------------------------
    @wait_for_it
    def fit(self):
        """"""
        datafile = self.pipeline_input

        markers = ['BAD', 'BLINK']
        markers += sorted(list(datafile.markers.keys()))

        self.markers.clear()
        self.markers.addItems(markers)

        header = datafile.header
        eeg = datafile.eeg
        timestamp = datafile.timestamp

        eeg = decimate(eeg, 15, axis=1)
        timestamp = np.linspace(
            0, timestamp[0][-1], eeg.shape[1], endpoint=True) / 1000

        # eeg = eeg / 1000

        self.threshold = 150
        channels = eeg.shape[0]

        self.set_data(timestamp, eeg,
                      labels=list(header['channels'].values()),
                      ylabel='Millivolt [$mv$]',
                      xlabel='Time [$s$]',
                      legend=False,
                      )

        self.ax1.set_yticks([self.threshold * i for i in range(channels)])
        self.ax1.set_yticklabels(
            self.pipeline_input.header['channels'].values())
        self.ax1.set_ylim(-self.threshold, self.threshold * channels)
        self.ax2.set_ylim(-self.threshold, self.threshold * channels)

        self.vlines = self.ax1.vlines(np.mean(self.ax1.get_xlim()),
                                      * self.ax1.get_ylim(), linestyle='--', color='red', linewidth=2, zorder=99)

        self.draw()

        datafile.close()

        self.pipeline_tunned = True
        self.pipeline_output = self.pipeline_input

    # ----------------------------------------------------------------------
    def set_data(self, timestamp, eeg, labels, ylabel='', xlabel='', legend=True):
        """"""
        self.ax1.clear()
        self.ax2.clear()

        for i, ch in enumerate(eeg):
            self.ax1.plot(timestamp, ch + self.threshold *
                          i, label=labels[i])
            self.ax2.plot(timestamp, ch + self.threshold * i, alpha=0.5)

        self.ax1.grid(True, axis='x')
        if legend:
            self.ax1.legend(loc='upper center', ncol=8,
                            bbox_to_anchor=(0.5, 1.4), **LEGEND_KWARGS)
        self.ax1.set_xlim(0, self.window_value)

        self.ax2.grid(True, axis='x')
        self.ax2.set_xlim(0, timestamp[-1])

        self.ax2.fill_between([0, self.window_value], *self.ax1.get_ylim(),
                              color=self.fill_color, alpha=self.fill_opacity, label='AREA')

        self.scroll.setMaximum((timestamp[-1] - self.window_value) * 1000)
        self.scroll.setMinimum(0)

        self.ax1.set_ylabel(ylabel)
        self.ax2.set_xlabel(xlabel)

    # ----------------------------------------------------------------------
    def move_plot(self, value):
        """"""
        self.ax1.set_xlim(value / 1000, (value / 1000 + self.window_value))

        for area in [i for i, c in enumerate(self.ax2.collections) if c.get_label() == 'AREA'][::-1]:
            self.ax2.collections.pop(area)

        self.ax2.fill_between([value / 1000, (value / 1000 + self.window_value)],
                              * self.ax1.get_ylim(), color=self.fill_color,
                              alpha=self.fill_opacity, label='AREA')

        segments = self.vlines.get_segments()
        segments[0][:, 0] = [np.mean(self.ax1.get_xlim())] * 2
        self.vlines.set_segments(segments)

        self.draw()

    # ----------------------------------------------------------------------
    def change_window(self):
        """"""
        self.window_value = self._get_seconds_from_human(
            self.combobox.currentText())

        eeg = self.pipeline_output.eeg
        timestamp = self.pipeline_output.timestamp

        timestamp = np.linspace(
            0, timestamp[0][-1], eeg.shape[1], endpoint=True) / 1000

        self.scroll.setMaximum((timestamp[-1] - self.window_value) * 1000)
        self.scroll.setMinimum(0)
        self.scroll.setPageStep(self.window_value * 1000)

        self.ax1.set_xlim(self.scroll.value() / 1000,
                          (self.scroll.value() / 1000 + self.window_value))

        self.draw()


# ########################################################################
# class ConditionalCreateMarkers(ta.TimelockWidget):
    # """"""

    # # ----------------------------------------------------------------------
    # def __init__(self, height, *args, **kwargs):
        # """Constructor"""
        # super().__init__(height=0, *args, **kwargs)
        # self.title = 'Create markers conditionally'

        # self.layout = QtWidgets.QVBoxLayout()
        # widget = QtWidgets.QWidget()
        # widget.setLayout(self.layout)

        # getattr(self.widget, 'topLayout').addWidget(widget)
        # getattr(self, 'top_stretch').append(1)

        # self.add_button('Add row', callback=self.add_row,
                        # area='bottom', stretch=0)
        # self.add_spacer(area='bottom', fixed=None, stretch=1)

        # self.new_markers = {}

    # # ----------------------------------------------------------------------
    # @wait_for_it
    # def fit(self):
        # """"""

    # # ----------------------------------------------------------------------
    # def add_new_markers(self, n):
        # """"""
        # for k in self.new_markers:
            # c1, c2, tx = self.new_markers[k]
            # print(f'{c1()}, {c2()}, {tx()}')

        # print('#' * 10)

    # # ----------------------------------------------------------------------
    # def add_row(self):
        # """"""
        # layout = QtWidgets.QHBoxLayout()
        # widget = QtWidgets.QWidget()
        # widget.setLayout(layout)

        # layout.addWidget(QtWidgets.QLabel(
            # 'Create new markers in the position of'))

        # combo1 = QtWidgets.QComboBox()
        # combo1.addItems(self.pipeline_input.markers.keys())
        # layout.addWidget(combo1)

        # layout.addWidget(QtWidgets.QLabel('that have a closest'))

        # combo2 = QtWidgets.QComboBox()
        # combo2.addItems(self.pipeline_input.markers.keys())
        # layout.addWidget(combo2)

        # layout.addWidget(QtWidgets.QLabel('as'))

        # edit = QtWidgets.QLineEdit()
        # self.new_markers[edit] = (
            # combo1.currentText, combo2.currentText, edit.text)
        # edit.textChanged.connect(self.add_new_markers)
        # layout.addWidget(edit)

        # layout.setStretch(0, 0)
        # layout.setStretch(1, 0)
        # layout.setStretch(2, 0)
        # layout.setStretch(3, 0)
        # layout.setStretch(4, 0)
        # layout.setStretch(5, 1)

        # self.layout.addWidget(widget)


########################################################################
class MarkersSynchronization(TimelockWidget):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, height, *args, **kwargs):
        """Constructor"""
        super().__init__(height, *args, **kwargs)
        self.title = 'Markers synchronization'

        # self.add_radios('Markers', self.notchs, callback=self.set_filters,
                        # area='top', stretch=0)

        self.sync_channel = self.add_combobox('Channel', [], editable=False, callback=self.update_plot,
                                              area='top2', stretch=0)
        self.add_spacer(area='top2', fixed=None, stretch=1)

        self.upper = self.add_spin('Upper', 500, suffix='vpp', min_=0, max_=2000,
                                   step=10, callback=self.update_plot, area='right', stretch=0)
        self.lower = self.add_spin('Lower', 200, suffix='vpp', min_=0, max_=2000,
                                   step=10, callback=self.update_plot, area='right', stretch=0)

        self.pipeline_tunned = True

        gs = self.figure.add_gridspec(1, 3)
        self.ax1 = gs.figure.add_subplot(gs[:, 0:-1])
        self.ax2 = gs.figure.add_subplot(gs[:, -1])

        self.figure.subplots_adjust(left=0.05,
                                    bottom=0.12,
                                    right=0.95,
                                    top=0.8)

    # ----------------------------------------------------------------------
    @wait_for_it
    def fit(self):
        """"""
        self.sync_channel.clear()
        self.sync_channel.addItems(
            f'AUX{c}' for c in range(self.pipeline_input.aux.shape[0]))

        self.clear_widgets(areas=['left'])
        self.marker_sync = self.add_checkbox('Markers', self.pipeline_input.markers.keys(), callback=self.update_plot,
                                             area='left', stretch=0, cols=1)
        self.add_spacer(stretch=1, area='left')

    # ----------------------------------------------------------------------
    def update_plot(self, *args, **kwargs):
        """"""
        self.ax1.clear()
        self.ax2.clear()

        lower_val = self.lower.value()
        upper_val = self.upper.value()

        aux = self.pipeline_input.aux[self.sync_channel.currentIndex()]
        markers = self.pipeline_input.markers

        t = self.pipeline_input.aux_timestamp[0]
        rises = self.pipeline_input.get_rises(
            aux, t, lower=lower_val, upper=upper_val)

        mks = []
        target_markers = [ch.text()
                          for ch in self.marker_sync if ch.isChecked()]
        for k in target_markers:
            mks.extend(markers[k])

        for i in mks:
            shape = aux[i - 2000:i + 2000]
            ts = np.linspace(-2000, 2000, shape.shape[0])
            self.ax1.plot(ts, shape, color=pyplot.cm.tab10(7),
                          alpha=0.5, linewidth=1)

            sh = shape.copy()
            if sh.size:
                sh = sh / (sh.max() - sh.min())
                sh = sh - sh.min()
                sh[sh > 0.5] = 1
                sh[sh <= 0.5] = 0
                a = abs(np.diff(sh, prepend=0))
                if r := np.argwhere(a == 1)[0][0]:
                    self.ax1.vlines(ts[r], 200, 800,
                                    linestyle='--', color=pyplot.cm.tab10(3), alpha=0.5)

        self.ax1.grid(True)

        for rise in rises:
            i = np.argmin(abs(t - rise))
            shape = aux[i - 50:i + 300]
            ts = np.linspace(-50, 300, shape.shape[0])
            self.ax2.plot(ts, shape, color=pyplot.cm.tab10(7),
                          alpha=0.1, linewidth=1)

        target = 100 * len(mks) / len(rises)
        self.ax2.plot(ts, shape, color=pyplot.cm.tab10(7),
                      alpha=0.1, linewidth=1, label=f'{target:.2f}% of markers synchronized')

        self.ax2.grid(True)
        self.ax2.vlines(0, lower_val, upper_val,
                        linestyle='--', color=pyplot.cm.tab10(3))

        self.ax1.set_title('Original analog rises')
        self.ax2.set_title('Syncronized rises')

        self.ax1.set_xlabel('Time [s]')
        self.ax2.set_xlabel('Time [s]')
        self.ax1.set_ylabel('Amplitude [mV]')
        # self.ax1.legend(ncol=2, loc='upper center')
        if 90 < target < 110:
            self.ax2.legend(loc='lower right', facecolor=pyplot.cm.tab10(
                0), framealpha=0.5, **LEGEND_KWARGS)
        else:
            self.ax2.legend(loc='lower right', facecolor=pyplot.cm.tab10(
                3), framealpha=0.5, **LEGEND_KWARGS)
        self.ax1.set_ylim(lower_val, upper_val)
        self.ax2.set_ylim(lower_val, upper_val)
        # self.ax2.set_xlim(0, 20)

        self.pipeline_input.reset_markers()

        if target_markers:
            self.pipeline_input.fix_markers(
                target_markers, rises, range_=2000)

        # self.pipeline_tunned = True
        self.pipeline_output = self.pipeline_input

        self.draw()


########################################################################
class ScriptProcess(TimelockWidget):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, height, *args, **kwargs):
        """Constructor"""
        super().__init__(0, *args, **kwargs)
        self.title = 'Script process'
        self.pipeline_tunned = True

    # # ----------------------------------------------------------------------
    # def fit(self):
        # """"""
        # self.pipeline_output = self.process(self.pipeline_input)

    # # ----------------------------------------------------------------------
    # def process(self, *args, **kwargs):
        # """"""
        # logging.warning('ERROR')


