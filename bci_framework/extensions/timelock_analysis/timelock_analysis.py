import os
import sys
import random
import logging
import copy
from string import ascii_lowercase

from PySide2.QtUiTools import QUiLoader


from PySide2.QtCore import Qt
from PySide2 import QtWidgets
from PySide2.QtWidgets import QSpacerItem, QSizePolicy

from bci_framework.framework.dialogs import Dialogs


from cycler import cycler
import matplotlib
from matplotlib import pyplot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np
from scipy.signal import decimate, welch

from gcpds.filters import frequency as flt

from abc import ABCMeta, abstractmethod


# Set logger
logger = logging.getLogger("mne")
logger.setLevel(logging.CRITICAL)
logging.getLogger('matplotlib.font_manager').disabled = True
logging.getLogger().setLevel(logging.WARNING)
logging.root.name = "TimelockAnalysis"

########################################################################
class Canvas(FigureCanvasQTAgg):

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""

        # Consigure matplotlib
        if ('light' in sys.argv) or ('light' in os.environ.get('QTMATERIAL_THEME', '')):
            pass
        else:
            pyplot.style.use('dark_background')

        try:
            q = matplotlib.cm.get_cmap('cool')
            matplotlib.rcParams['axes.prop_cycle'] = cycler(
                color=[q(m) for m in np.linspace(0, 1, 16)])
            matplotlib.rcParams['figure.dpi'] = 60
            matplotlib.rcParams['font.family'] = 'monospace'
            matplotlib.rcParams['font.size'] = 15
            # matplotlib.rcParams['legend.facecolor'] = 'red'
        except:
            # 'rcParams' object does not support item assignment
            pass

        self.figure = Figure(*args, **kwargs)
        super().__init__(self.figure)

        # self.figure.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)


########################################################################
class TimelockWidget(metaclass=ABCMeta):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, height, *args, **kwargs):
        """Constructor"""
        # self.fill_opacity = 0.2
        # self.fill_color = os.environ.get('QTMATERIAL_PRIMARYCOLOR', '#ff0000')

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

        # self.widget.setProperty('class', 'bottom_border')

        if height:
            self.widget.setMinimumHeight(height)

        self.canvas = Canvas(*args, **kwargs)
        self.figure = self.canvas.figure
        self.widget.gridLayout.addWidget(self.canvas)

    # ----------------------------------------------------------------------
    def draw(self):
        """"""
        self.canvas.draw()

    # ----------------------------------------------------------------------
    def _add_spacers(self):
        """"""
        for i, s in enumerate(self.bottom_stretch):
            self.widget.bottomLayout.setStretch(i, s)

        for i, s in enumerate(self.top_stretch):
            self.widget.topLayout.setStretch(i, s)

        for i, s in enumerate(self.bottom2_stretch):
            self.widget.bottomLayout.setStretch(i, s)

        for i, s in enumerate(self.top2_stretch):
            self.widget.topLayout.setStretch(i, s)

        for i, s in enumerate(self.right_stretch):
            self.widget.rightLayout.setStretch(i, s)

        for i, s in enumerate(self.left_stretch):
            self.widget.leftLayout.setStretch(i, s)

    # ----------------------------------------------------------------------
    def add_spacer(self, area='top', fixed=None):
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

    # ----------------------------------------------------------------------
    def clear_layout(self, layout):
        """"""
        for i in range(layout.count()):
            b = layout.itemAt(i)

            if b is None:
                continue

            if w := b.widget():  # widget
                w.deleteLater()

            if b.spacerItem():  # spacer
                layout.removeItem(b)

            if l := b.layout():
                self.clear_layout(l)

            # layout.removeItem(layout.itemAt(i))

            # b = layout.takeAt(2)
                # buttons.pop(2)
                # b.widget().deleteLater()

    # ----------------------------------------------------------------------
    def clear_widgets(self):
        """"""
        for area in ['left', 'right', 'top', 'bottom', 'top2', 'bottom2']:
            layout = getattr(self.widget, f'{area}Layout')
            self.clear_layout(layout)

    # ----------------------------------------------------------------------
    def add_textarea(self, content='', area='top', stretch=0):
        """"""
        textarea = QtWidgets.QTextEdit(content)
        textarea.setProperty('class', 'clear')
        textarea.setMinimumWidth(500)
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
    def add_radios(self, group_name, radios, cols=None, callback=None, area='top', stretch=1):
        """"""
        group = QtWidgets.QGroupBox(group_name)
        vbox = QtWidgets.QVBoxLayout()
        group.setLayout(vbox)

        if cols is None:
            cols = len(radios)

        for i, radio in enumerate(radios):
            if (i % cols) == 0:
                hbox = QtWidgets.QHBoxLayout()
                vbox.addLayout(hbox)

            # group.setLayout(hbox)
            r = QtWidgets.QRadioButton()
            r.setText(radio)
            r.setChecked(i == 0)

            # ----------------------------------------------------------------------

            def dec(*args):
                # ----------------------------------------------------------------------
                def wrap(fn):

                    return callback(*args)

                return wrap

            if callback:
                r.clicked.connect(dec(group_name, radio))

            hbox.addWidget(r)

        getattr(self.widget, f'{area}Layout').addWidget(group)
        getattr(self, f'{area}_stretch').append(stretch)

    # ----------------------------------------------------------------------
    def add_checkbox(self, group_name, radios, ncol=None, callback=None, area='top', stretch=1):
        """"""
        group = QtWidgets.QGroupBox(group_name)
        vbox = QtWidgets.QVBoxLayout()
        group.setLayout(vbox)

        if ncol is None:
            ncol = len(radios)

        list_radios = []
        for i, radio in enumerate(radios):
            if (i % ncol) == 0:
                hbox = QtWidgets.QHBoxLayout()
                vbox.addLayout(hbox)

            # group.setLayout(hbox)
            r = QtWidgets.QCheckBox()
            r.setText(radio)
            r.setChecked(i == 0)
            list_radios.append(r)

           # ----------------------------------------------------------------------
            def dec(*args):
                # ----------------------------------------------------------------------
                def wrap(fn):
                    return callback(*args)
                return wrap

            if callback:
                r.clicked.connect(dec(group_name, radio))

            hbox.addWidget(r)

        getattr(self.widget, f'{area}Layout').addWidget(group)
        getattr(self, f'{area}_stretch').append(stretch)

        return list_radios

    # ----------------------------------------------------------------------
    def add_channels(self, group_name, radios, callback=None, area='top', stretch=1):
        """"""
        group = QtWidgets.QGroupBox(group_name)
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
        for radio in radios:

            r = QtWidgets.QCheckBox()
            r.setText(radio)
            r.setChecked(True)
            list_radios.append(r)

            if radio[-1].isnumeric() and int(radio[-1]) % 2 != 0:  # odd
                vbox_odd.addWidget(r)
            elif radio[-1].isnumeric() and int(radio[-1]) % 2 == 0:  # even
                vbox_even.addWidget(r)
            else:
                vbox_z.addWidget(r)

            def dec(*args):
                def wrap(fn):
                    return callback(*args)
                return wrap

            if callback:
                r.clicked.connect(dec(group_name, radio))

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
    def add_combobox(self, label, items, callback=None, area='top', stretch=0):
        """"""

        combo = QtWidgets.QComboBox()
        combo.addItems(items)
        combo.activated.connect(callback)

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


class TimelockDashboard:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, height):
        """Constructor"""
        self.height = height
        ui = os.path.realpath(os.path.join(
            os.environ['BCISTREAM_ROOT'], 'framework', 'qtgui', 'locktime_widget.ui'))
        self.widget = QUiLoader().load(ui)
        self.widget.setProperty('class', 'dashboard')
        self.widget.label_title.setText('')
        self.widget.gridLayout.setVerticalSpacing(30)
        self.widget.gridLayout.setContentsMargins(30, 30, 30, 30)

    # ----------------------------------------------------------------------
    def add_widgets(self, *widgets):
        """"""
        analyzers = []
        max_r = 0
        max_c = 0
        i = 0
        for analyzer, w in widgets:

            height = w.get('height', 1)

            name = ''.join([random.choice(ascii_lowercase)
                            for i in range(8)])
            setattr(self, name, analyzer(self.height * height))
            analyzer = getattr(self, name)
            analyzer.widget.label_title.setText(w.get('title', ''))
            analyzer.widget.setProperty('class', 'timelock')
            analyzer.widget.setContentsMargins(30, 30, 30, 30)
            analyzer._add_spacers()

            if analyzers:
                analyzer.previous_pipeline(analyzers[-1])
                analyzers[-1].next_pipeline(analyzer)

            self.widget.gridLayout.addWidget(
                analyzer.widget, w.get('row', i), w.get('col', 0), w.get('row_span', 1), w.get('col_span', 1))
            analyzers.append(analyzer)

            i += 1

        self.widget.gridLayout.setColumnStretch(0, 1)

        # for i in range(max_r):
            # self.widget.gridLayout.setRowStretch(i, 0)


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
    def set_data(self, timestamp, eeg, labels, ylabel='', xlabel=''):
        """"""
        self.ax1.clear()
        self.ax2.clear()

        for i, ch in enumerate(eeg):
            self.ax1.plot(timestamp, eeg[i], label=labels[i])
            self.ax2.plot(timestamp, eeg[i], alpha=0.5)

        self.ax1.grid(True)
        self.ax1.legend(loc='upper center', ncol=8,
                        labelcolor='k', bbox_to_anchor=(0.5, 1.4))
        self.ax1.set_xlim(0, self.window_value)

        self.ax2.grid(True)
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
                         '0.01-20 Hz',
                         '5-45 Hz', '3-30 Hz', '4-40 Hz', '2-45 Hz', '1-50 Hz',
                         '7-13 Hz', '15-50 Hz', '1-100 Hz', '5-50 Hz')

        self.add_radios('Notch', self.notchs, callback=self.set_filters,
                        area='top', stretch=0)
        self.add_radios('Bandpass', self.bandpass, callback=self.set_filters,
                        area='top', stretch=1)

        self.scale = self.add_spin('Scale', 150, suffix='uv', min_=0,
                                   max_=1000, step=50, callback=self.fit, area='top',
                                   stretch=0)

    # ----------------------------------------------------------------------
    def fit(self):
        """"""

        eeg = self.pipeline_input.eeg
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
        self.ax1.grid(True)
        self.ax2.grid(True)

        self.draw()

        self.pipeline_tunned = True
        self.pipeline_output = copy.deepcopy(self.pipeline_input)
        self.pipeline_output.eeg = eeg.copy()

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
