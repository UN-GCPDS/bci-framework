import os
import sys
import random
import logging
from string import ascii_lowercase

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QSpacerItem, QSizePolicy, QPushButton

from cycler import cycler
import matplotlib
from matplotlib import pyplot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np


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
    def __init__(self, height):
        """Constructor"""

        ui = os.path.realpath(os.path.join(
            os.environ['BCISTREAM_ROOT'], 'framework', 'qtgui', 'locktime_widget.ui'))
        self.widget = QUiLoader().load(ui)

        if height:
            self.widget.setMinimumHeight(height)

        self.canvas = Canvas()
        self.figure = self.canvas.figure
        self.widget.gridLayout.addWidget(self.canvas)

    # ----------------------------------------------------------------------
    def _add_spacers(self):
        """"""
        self.widget.leftLayout.addItem(QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.widget.rightLayout.addItem(QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.widget.topLayout.addItem(QSpacerItem(
            20, 40, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.widget.bottomLayout.addItem(QSpacerItem(
            20, 40, QSizePolicy.Expanding, QSizePolicy.Minimum))

    # ----------------------------------------------------------------------
    def add_button(self, label, on_click=None, area='top'):
        """"""
        button = QPushButton(label)
        if on_click:
            button.clicked.connect(on_click)
        getattr(self.widget, f'{area}Layout').addWidget(button)


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
    def add_widget(self, widget, row, column, rowSpan=1, columnSpan=1, height=1):
        """"""
        name = ''.join([random.choice(ascii_lowercase) for i in range(8)])
        setattr(self, name, widget(self.height * height))
        getattr(self, name)._add_spacers()
        self.widget.gridLayout.addWidget(
            getattr(self, name).widget, row, column, rowSpan, columnSpan)
