import os
import sys
import random
import logging
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
from scipy.signal import decimate


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
class TimelockWidget:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, height, *args, **kwargs):
        """Constructor"""
        # self.fill_opacity = 0.2
        # self.fill_color = os.environ.get('QTMATERIAL_PRIMARYCOLOR', '#ff0000')

        self.bottom_stretch = []
        self.bottom2_stretch = []
        self.top_stretch = []
        self.right_stretch = []
        self.left_stretch = []

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
    def _add_spacers(self):
        """"""
        for i, s in enumerate(self.bottom_stretch):
            self.widget.bottomLayout.setStretch(i, s)

        for i, s in enumerate(self.top_stretch):
            self.widget.topLayout.setStretch(i, s)

        for i, s in enumerate(self.right_stretch):
            self.widget.rightLayout.setStretch(i, s)

        for i, s in enumerate(self.left_stretch):
            self.widget.leftLayout.setStretch(i, s)

    # ----------------------------------------------------------------------
    def add_spacer(self, area='top', stretch=0):
        """"""
        if area in ['left', 'right']:
            getattr(self.widget, f'{area}Layout').addItem(QSpacerItem(
                20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        elif area in ['top', 'bottom']:
            getattr(self.widget, f'{area}Layout').addItem(QSpacerItem(
                20, 40, QSizePolicy.Expanding, QSizePolicy.Minimum))

    # ----------------------------------------------------------------------
    def add_button(self, label, callback=None, area='top', stretch=0):
        """"""
        button = QtWidgets.QPushButton(label)
        if callback:
            button.clicked.connect(callback)
        getattr(self.widget, f'{area}Layout').addWidget(button)

        getattr(self, f'{area}_stretch').append(stretch)

    # ----------------------------------------------------------------------
    def add_radios(self, group_name, radios, cols=None, callback=None, area='top', stretch=0):
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

            group.setLayout(hbox)
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
    def add_combobox(self, label, items, callback=None, area='top', stretch=0):
        """"""

        combo = QtWidgets.QComboBox()
        combo.addItems(items)
        combo.activated.connect(callback)

        if label:
            getattr(self.widget, f'{area}Layout').addWidget(
                QtWidgets.QLabel(label))

        getattr(self.widget, f'{area}Layout').addWidget(combo)

        getattr(self, f'{area}_stretch').append(stretch)
        getattr(self, f'{area}_stretch').append(stretch)

        return combo

    # ----------------------------------------------------------------------
    def set_next_pipeline(self, fn):
        """"""
        self.next_pipeline = fn

    # ----------------------------------------------------------------------
    def propagate(self):
        """"""
        if next_pipeline := getattr(self, 'next_pipeline', False):
            next_pipeline(self.output)

    # ----------------------------------------------------------------------
    def fit_propagate(self, datafile):
        """"""
        self.fit(datafile)
        self.propagate()

    # ----------------------------------------------------------------------
    def draw(self):
        """"""
        self.canvas.draw()


########################################################################
class TimelockDashboard:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, height=0):
        """Constructor"""
        self.height = height
        ui = os.path.realpath(os.path.join(
            os.environ['BCISTREAM_ROOT'], 'framework', 'qtgui', 'locktime_widget.ui'))
        self.widget = QUiLoader().load(ui)

    # ----------------------------------------------------------------------
    def add_widgets(self, *widgets):
        """"""

        analyzers = []
        max_r = 0
        max_c = 0
        for i, w in enumerate(widgets):

            height = 1

            name = ''.join([random.choice(ascii_lowercase)
                            for i in range(8)])
            setattr(self, name, w['analyzer'](self.height * height))
            analyzer = getattr(self, name)
            analyzer._add_spacers()

            if analyzers:
                analyzers[-1].set_next_pipeline(analyzer.fit_propagate)

            self.widget.gridLayout.addWidget(
                analyzer.widget, w['row'], w['col'], w['row_span'], w['col_span'])

            # self.widget.gridLayout.setColumnStretch(
                # w['col'], w.get('stretch', 1))

            analyzers.append(analyzer)

        self.widget.gridLayout.setColumnStretch(0, 1)
        self.widget.gridLayout.setColumnStretch(1, 1)

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

        eeg, timestamp = self.output

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

