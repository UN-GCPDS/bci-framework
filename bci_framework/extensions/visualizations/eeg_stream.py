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
import logging

import mne
import numpy as np
import matplotlib
from matplotlib import pyplot
from cycler import cycler
from figurestream import FigureStream
from typing import Optional, Tuple, Literal

from ...extensions import properties as prop

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


########################################################################
class Transformers:
    """Used to preprocess EEG streams."""

    # ----------------------------------------------------------------------
    def resample(self, x: np.ndarray, num: int) -> np.array:
        """Fast resample.

        Parameters
        ----------
        x
            Input array of shape (`channels, time`).
        num
            Desired time samples.

        Returns
        -------
        array
            Resampled array (`channels, num`).
        """

        ndim = x.shape[1] // num
        return np.mean(np.nan_to_num(x[:, :ndim * num].reshape(x.shape[0], num, ndim)), axis=-1)
        # return zoom(x, (1, num / x.shape[1]))
        # return np.nan_to_num(x[:, :ndim * num][:, ::ndim])

    # ----------------------------------------------------------------------
    def centralize(self, x: np.array, normalize: bool = False, axis: int = 0) -> np.array:
        """Crentralize array.

        Remove the mean to all axis.

        Parameters
        ----------
        x
            Input array of shape (`channels, time`).
        normalize
            Return array with maximun amplitude equal to 1.
        axis
            Axis to centralize.

        Returns
        -------
        array
            Centralized array.
        """

        cent = np.nan_to_num(np.apply_along_axis(
            lambda x_: x_ - x_.mean(), 1, x))

        if normalize:
            if normalize == True:
                normalize = 1
            return np.nan_to_num(np.apply_along_axis(lambda x_: normalize * (x_ / (x_.max() - x_.min())), 1, cent))

        return cent


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
            self.buffer_eeg, self.get_mne_info(), 0, comment=comment, nave=0
        )
        return evoked


########################################################################
class EEGStream(FigureStream, Transformers, MNEObjects):
    """Matplotlib figure re-implementation.

    This class define some usefull methods to use for simplificate the data
    manipulation.
    """

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        port = 5000
        super().__init__(host='0.0.0.0', port=port, endpoint='', *args, **kwargs)

    # ----------------------------------------------------------------------
    def create_lines(self, mode: Literal['eeg', 'accel', 'analog', 'digital'] = 'eeg',
                     time: Optional[int] = -15,
                     window: Optional[str] = 'auto',
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
            ylim = 0, 255
        elif mode == 'analog' and prop.CONNECTION == 'wifi':
            channels = 2
            labels = ['A5(D11)', 'A6(D12)']
            ylim = 0, 255
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

        if window == 'auto':
            window = self._get_factor_near_to(prop.SAMPLE_RATE * np.abs(time),
                                              n=1000)

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

        if time > 0:
            axis.set_xlim(0, time)
            time = np.linspace(0, time, window)
        else:
            axis.set_xlim(time, 0)
            time = np.linspace(time, 0, window)
        axis.set_ylim(*ylim)

        if mode != 'eeg':
            axis.legend()

        axis.grid(True, color='#ffffff', alpha=0.25, zorder=0)
        lines = np.array(lines)

        return axis, time, lines

    # ----------------------------------------------------------------------
    def create_buffer(self, seconds: Optional[int] = [30], aux_shape: Optional[int] = 3, fill: Optional[int] = 0):
        """Create a buffer with fixed time length.

        Since the `loop_consumer` iteraror only return the last data package, the
        object `buffer_eeg` and `buffer_aux` will retain a longer (in time) data.

        Parameters
        ----------
        seconds
            How many seconds will content the buffer.
        aux_shape
            Define the shape of aux array.
        fill
            Initialize buffet with this value
        """

        chs = len(prop.CHANNELS)
        time = prop.SAMPLE_RATE * seconds

        self.buffer_eeg = np.empty((chs, time))
        self.buffer_eeg.fill(fill)

        self.buffer_eeg_split = []

        self.buffer_aux = np.empty((aux_shape, time))
        self.buffer_aux.fill(fill)

    # ----------------------------------------------------------------------
    def create_boundary(self, axis: matplotlib.axes.Axes, min: Optional[int] = 0, max: Optional[int] = 17):
        """Add the boundary line to some visualizations."""

        self.boundary = 0
        self.boundary_aux = 0

        self.boundary_line = axis.vlines(0, min, max, color='w', zorder=99)
        self.boundary_aux_line = axis.vlines(0, max, max, color='w', zorder=99)

    # ----------------------------------------------------------------------
    def plot_boundary(self, eeg: Optional[bool] = True, aux: Optional[bool] = False):
        """Update the position of the boundary line."""

        if eeg and hasattr(self, 'boundary_line'):
            segments = self.boundary_line.get_segments()
            segments[0][:, 0] = [self.boundary / prop.SAMPLE_RATE,
                                 self.boundary / prop.SAMPLE_RATE]
            self.boundary_line.set_segments(segments)
        elif aux and hasattr(self, 'boundary_aux_line'):
            segments = self.boundary_aux_line.get_segments()
            segments[0][:, 0] = [self.boundary_aux /
                                 prop.SAMPLE_RATE, self.boundary_aux / prop.SAMPLE_RATE]
            self.boundary_aux_line.set_segments(segments)

        else:
            logging.warning('No "boundary" to plot')

    # ----------------------------------------------------------------------
    def update_buffer(self, eeg: np.ndarray, aux: np.ndarray):
        """Uppdate the buffers.

        Parameters
        ----------
        eeg
            The new EEG array
        aux
            The new AUX array
        """

        if self.boundary is False:
            c = eeg.shape[1]
            self.buffer_eeg = np.roll(self.buffer_eeg, -c, axis=1)
            self.buffer_eeg[:, -c:] = eeg

            self.buffer_eeg_split.append(c)

            if sum(self.buffer_eeg_split) > self.buffer_eeg.shape[1]:
                self.buffer_eeg_split.pop(0)

            if not aux is None:
                d = aux.shape[1]
                self.buffer_aux = np.roll(self.buffer_aux, -d, axis=1)
                self.buffer_aux[:, -d:] = aux

        else:
            c = eeg.shape[1]

            roll = 0
            if self.boundary + c >= self.buffer_eeg.shape[1]:
                roll = self.buffer_eeg.shape[1] - (self.boundary + c)
                self.buffer_eeg = np.roll(self.buffer_eeg, -roll, axis=1)
                self.buffer_eeg[:, -eeg.shape[1]:] = eeg
                self.buffer_eeg = np.roll(self.buffer_eeg, roll, axis=1)

            else:
                self.buffer_eeg[:, self.boundary:self.boundary + c] = eeg

            self.boundary += c
            self.boundary = self.boundary % self.buffer_eeg.shape[1]

            if not aux is None:
                d = aux.shape[1]

                roll = 0
                if self.boundary_aux + d >= self.buffer_aux.shape[1]:
                    roll = self.boundary_aux + d

                if roll:
                    self.buffer_aux = np.roll(self.buffer_aux, -roll, axis=1)

                if (self.buffer_aux[:, self.boundary_aux:self.boundary_aux + d]).shape != aux.shape:
                    l = self.buffer_aux[:,
                                        self.boundary_aux:self.boundary_aux + d].shape[1]
                    logging.warning([l, aux.shape[1]])

                    self.buffer_aux[:,
                                    self.boundary_aux:self.boundary_aux + d] = aux[:, :l]
                else:
                    self.buffer_aux[:,
                                    self.boundary_aux:self.boundary_aux + d] = aux

                if roll:
                    self.buffer_aux = np.roll(self.buffer_aux, roll, axis=1)

                self.boundary_aux += d
                self.boundary_aux = self.boundary_aux % self.buffer_aux.shape[1]

    # ----------------------------------------------------------------------
    def _get_factor_near_to(self, x: int, n: Optional[int] = 1000) -> int:
        """Get the integer number factor of `x` nearest to `n`.

        This factor is used to fast resampling.

        Parameters
        ----------
        x
            Samples.
        n
            Near factor

        Returns
        -------
        int
            Factor.
        """
        a = np.array([(x) / np.arange(max(1, (x // n) - 10), (x // n) + 10)])[0]
        a[a % 1 != 0] = 0
        return int(a[np.argmin(np.abs(a - n))])
