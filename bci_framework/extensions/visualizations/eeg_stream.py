import os
import sys
import logging

import numpy as np
import matplotlib
from matplotlib import pyplot
from cycler import cycler
from figurestream import FigureStream

from ...extensions import properties as prop

# Consigure matplotlib
if ('light' in sys.argv) or ('light' in os.environ.get('QTMATERIAL_THEME', '')):
    pass
else:
    pyplot.style.use('dark_background')

q = matplotlib.cm.get_cmap('rainbow')
matplotlib.rcParams['axes.prop_cycle'] = cycler(
    color=[q(m) for m in np.linspace(0, 1, 16)])

matplotlib.rcParams['figure.dpi'] = 60
matplotlib.rcParams['font.family'] = 'monospace'
matplotlib.rcParams['font.size'] = 15

# Set logger
logger = logging.getLogger("mne")
logger.setLevel(logging.CRITICAL)


########################################################################
class Transformers:
    """"""

    # ----------------------------------------------------------------------
    def resample(self, x, num):
        """"""
        ndim = x.shape[1] // num
        return np.mean(np.nan_to_num(x[:, :ndim * num].reshape(x.shape[0], num, ndim)), axis=-1)
        # return zoom(x, (1, num / x.shape[1]))
        # return np.nan_to_num(x[:, :ndim * num][:, ::ndim])

    # ----------------------------------------------------------------------
    def centralize(self, x, normalize=False, axis=0):
        """"""
        cent = np.nan_to_num(np.apply_along_axis(
            lambda x_: x_ - x_.mean(), 1, x))

        if normalize:
            if normalize == True:
                normalize = 1
            return np.nan_to_num(np.apply_along_axis(lambda x_: normalize * (x_ / (x_.max() - x_.min())), 1, cent))

        return cent


########################################################################
class MNEObjects:
    """"""

    # ----------------------------------------------------------------------
    def get_mne_info(self):
        """"""
        info = mne.create_info(
            list(prop.CHANNELS.values()),
            sfreq=prop.SAMPLE_RATE,
            ch_types="eeg",
        )
        info.set_montage(prop.MONTAGE_NAME)
        return info

    # ----------------------------------------------------------------------
    def get_mne_montage(self):
        """"""
        montage = mne.channels.make_standard_montage(prop.MONTAGE_NAME)
        return montage

    # ----------------------------------------------------------------------
    def get_mne_evoked(self):
        """"""
        comment = "bcistream"
        evoked = mne.EvokedArray(
            self.buffer_eeg, self.get_mne_info(), 0, comment=comment, nave=0
        )
        return evoked


########################################################################
class EEGStream(FigureStream, Transformers, MNEObjects):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, host='0.0.0.0', port='5000', endpoint='', *args, **kwargs):
        """"""
        super().__init__(host, port, endpoint, *args, **kwargs)

    # ----------------------------------------------------------------------
    def create_lines(self, mode='eeg', time=-15, window='auto', cmap='cool', fill=np.nan, subplot=[1, 1, 1],):
        """"""
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
            window = self.get_factor_near_to(prop.SAMPLE_RATE * np.abs(time),
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
    def create_buffer(self, seconds=30, aux_shape=3, fill=0):
        """"""
        chs = len(prop.CHANNELS)
        time = prop.SAMPLE_RATE * seconds

        self.buffer_eeg = np.empty((chs, time))
        self.buffer_eeg.fill(fill)

        self.buffer_eeg_split = []

        self.buffer_aux = np.empty((aux_shape, time))
        self.buffer_aux.fill(fill)

    # ----------------------------------------------------------------------
    def create_boundary(self, axis, min=0, max=17):
        """"""
        self.boundary = 0
        self.boundary_aux = 0

        self.boundary_line = axis.vlines(
            0, min, max, color='w', zorder=99)
        self.boundary_aux_line = axis.vlines(
            0, max, max, color='w', zorder=99)

    # ----------------------------------------------------------------------
    def plot_boundary(self, eeg=True, aux=False):
        """"""
        if eeg and hasattr(self, 'boundary_line'):
            segments = self.boundary_line.get_segments()
            segments[0][:, 0] = [self.boundary / prop.SAMPLE_RATE,
                                 self.boundary / prop.SAMPLE_RATE]
            self.boundary_line.set_segments(segments)
        elif aux and hasattr(self, 'boundary_aux_line'):
            segments = self.boundary_aux_line.get_segments()
            segments[0][:, 0] = [self.boundary_aux
                                 / prop.SAMPLE_RATE, self.boundary_aux / prop.SAMPLE_RATE]
            self.boundary_aux_line.set_segments(segments)

        else:
            logging.warning('No "boundary" to plot')

    # ----------------------------------------------------------------------
    def update_buffer(self, eeg, aux):
        """"""
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
    def get_factor_near_to(self, x, n=1000):
        a = np.array(
            [(x) / np.arange(max(1, (x // n) - 10), (x // n) + 10)])[0]
        a[a % 1 != 0] = 0
        return int(a[np.argmin(np.abs(a - n))])
