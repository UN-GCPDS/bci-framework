"""
==========
EEG Stream
==========

Reimplementation of `Matplotlib-FigureStream
<https://figurestream.readthedocs.io/en/latest/>`_ with some renames and a
preconfigured server.
"""

import os
import sys
import json
import pickle
import logging
import time

import mne
import numpy as np
import matplotlib
from matplotlib import pyplot
from cycler import cycler
from kafka import KafkaProducer
from figurestream import FigureStream
from typing import Optional, Tuple, Literal, Callable

from ...extensions import properties as prop
from ... extensions.data_analysis import DataAnalysis

# Consigure matplotlib
if ('light' in sys.argv) or ('light' in os.environ.get('QTMATERIAL_THEME', '')):
    pass
else:
    pyplot.style.use('dark_background')

try:
    q = matplotlib.cm.get_cmap('rainbow')
    matplotlib.rcParams['axes.prop_cycle'] = cycler(
        color=[q(m) for m in np.linspace(0, 1, 16)])
    matplotlib.rcParams['figure.dpi'] = 60
    matplotlib.rcParams['font.family'] = 'monospace'
    matplotlib.rcParams['font.size'] = 15
except:
    # 'rcParams' object does not support item assignment
    pass

# Set logger
logger = logging.getLogger("mne")
logger.setLevel(logging.CRITICAL)
logging.root.name = "Visualizations"


########################################################################
class MNEObjects:
    """Creat MNE handlers using the framework GUI information."""

    # ----------------------------------------------------------------------
    def get_mne_info(self) -> mne.Info:
        """Create the `Info` object to use with mne handlers.

        The information is acquired automatically from GUI interface.
        """

        info = mne.create_info(
            list(prop.CHANNELS.values()),
            sfreq=prop.SAMPLE_RATE,
            ch_types="eeg",
        )
        info.set_montage(prop.MONTAGE_NAME)
        return info

    # ----------------------------------------------------------------------
    def get_mne_montage(self) -> mne.channels.DigMontage:
        """Create the `Montage` object to use with mne handlers.

        The information is acquired automatically from GUI interface.
        """

        montage = mne.channels.make_standard_montage(prop.MONTAGE_NAME)
        return montage

    # ----------------------------------------------------------------------
    def get_mne_evoked(self) -> mne.EvokedArray:
        """Create the `Evoked` object to use with mne handlers.

        The information is acquired automatically from GUI interface.
        """

        comment = "bcistream"
        evoked = mne.EvokedArray(
            self.buffer_eeg_, self.get_mne_info(), 0, comment=comment, nave=0
        )
        return evoked


########################################################################
class EEGStream(FigureStream, DataAnalysis, MNEObjects):
    """Matplotlib figure re-implementation.

    This class define some usefull methods to use for simplificate the data
    manipulation.
    """

    # ----------------------------------------------------------------------
    def __init__(self, enable_produser=False, *args, **kwargs):
        """"""
        port = 5000
        super().__init__(host='0.0.0.0', port=port, endpoint='', *args, **kwargs)

        self._pivot = None
        if enable_produser:
            self._enable_commands()

        self.transformers_ = {}
        self.transformers_aux_ = {}
        self.widget_value = {}
        self.wait_for_interact()

    # ----------------------------------------------------------------------
    def create_lines(self, mode: Literal['eeg', 'accel', 'analog', 'digital'] = 'eeg',
                     time: Optional[int] = -15,
                     window: Optional[int] = 1000,
                     cmap: Optional[str] = 'cool',
                     fill: Optional[np.ndarray] = np.nan,
                     subplot: Optional[list] = [1, 1, 1],) -> Tuple[matplotlib.axes.Axes, np.ndarray, list[matplotlib.lines]]:
        """Create plot automatically.

        Create and configure a subplot to display figures.

        Parameters
        ----------
        mode
            Used for select the axis labels.
        time
            The time window, can be negative.
        window
            The number of samples used to draw the figure.
        cmap
            The matplolib `cmap` to use.
        fill
            Start signals array with this value.
        subplot
            The matplolib subplot.

        Returns
        -------
        axis
            The subplot created.
        time
            The time array.
        lines
            The matplotlib `lines` object created for each channel.
        """

        mode = mode.lower()
        sr = prop.SAMPLE_RATE

        if mode == 'eeg':
            channels = len(prop.CHANNELS)
            labels = None
            ylim = 0, 16
        elif mode == 'accel' or mode == 'default':
            channels = 3
            labels = ['X', 'Y', 'Z']
            ylim = -6, 6
            sr = sr / 10
        elif mode == 'analog' and not prop.CONNECTION == 'wifi':
            channels = 3
            labels = ['A5(D11)', 'A6(D12)', 'A7(D13)']
            ylim = 0, 2 ** 10
        elif mode == 'analog' and prop.CONNECTION == 'wifi':
            channels = 2
            labels = ['A5(D11)', 'A6(D12)']
            ylim = 0, 2 ** 10
        elif mode == 'digital' and not prop.CONNECTION == 'wifi':
            channels = 5
            labels = ['D11', 'D12', 'D13', 'D17', 'D18']
            ylim = 0, 1.2
        elif mode == 'digital' and prop.CONNECTION == 'wifi':
            channels = 3
            labels = ['D11', 'D12', 'D17']
            ylim = 0, 1.2

        q = matplotlib.cm.get_cmap(cmap)
        matplotlib.rcParams['axes.prop_cycle'] = cycler(
            color=[q(m) for m in np.linspace(0, 1, channels)]
        )

        axis = self.add_subplot(*subplot)

        window = self._get_factor_near_to(
            prop.SAMPLE_RATE * np.abs(time), n=window)
        # self._create_resampled_buffer(
            # prop.SAMPLE_RATE * np.abs(time), n=1000)

        a = np.empty(window)
        a.fill(fill)

        lines = [
            axis.plot(
                a.copy(),
                a.copy(),
                '-',
                label=(labels[i] if labels else None),
            )[0]
            for i in range(channels)
        ]

        if labels:
            axis.legend()

        if time > 0:
            axis.set_xlim(0, time)
            time = np.linspace(0, time, window)
        else:
            axis.set_xlim(time, 0)
            time = np.linspace(time, 0, window)
        axis.set_ylim(*ylim)

        # if mode != 'eeg':
            # axis.legend()

        axis.grid(True, color=os.environ.get(
            'QTMATERIAL_SECONDARYLIGHTCOLOR', '#ff0000'), zorder=0)
        lines = np.array(lines)

        return axis, time, lines

    # # ----------------------------------------------------------------------
    # def reverse_buffer(self, axis: matplotlib.axes.Axes, min: Optional[int] = 0, max: Optional[int] = 17, color: Optional[str] = 'k'):
        # """Add the boundary line to some visualizations."""

        # if hasattr(self, 'boundary_line'):
            # self.boundary_line.remove()
            # start = self._pivot / prop.SAMPLE_RATE
        # else:
            # self._pivot = 0
            # self._pivot_aux = 0
            # start = 0

        # self.boundary_line = axis.vlines(
            # start, min, max, color=color, zorder=99)

    # # ----------------------------------------------------------------------
    # def plot_pivot(self):
        # """Update the position of the boundary line."""

        # if hasattr(self, 'boundary_line'):
            # segments = self.boundary_line.get_segments()
            # segments[0][:, 0] = [self._pivot / prop.SAMPLE_RATE,
                                 # self._pivot / prop.SAMPLE_RATE]
            # self.boundary_line.set_segments(segments)

        # else:
            # logging.warning('No "boundary" to plot')

    # # ----------------------------------------------------------------------
    # def feed(self):
        # """"""
        # super().feed()

    # ----------------------------------------------------------------------
    def wait_for_interact(self):
        """"""
        if os.path.exists(os.path.join(sys.path[0], 'interact')):
            with open(os.path.join(sys.path[0], 'interact'), 'r') as file:
                for line in file.readlines():
                    l = json.loads(line)
                    if l[0] == '#':
                        ll, v = l[1], l[4]
                    else:
                        ll, v = l[0], l[3]
                    self.widget_value[ll] = v
