import os

import matplotlib
from matplotlib import cm
from matplotlib import pyplot
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import mne
import numpy as np
from scipy.spatial.distance import pdist, squareform

from PySide2.QtCore import QTimer
from openbci_stream.consumer import OpenBCIConsumer

from bci_framework.projects import properties as prop
from bci_framework.projects.figure import thread_this, subprocess_this


########################################################################
class Topoplot(FigureCanvas):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """"""
        super().__init__(Figure(figsize=(1, 1), dpi=90))

        self.cmap = 'RdYlGn'

        self.ax = self.figure.add_subplot(111)
        self.figure.subplots_adjust(
            left=0.03, bottom=0.08, right=0.97, top=0.97, wspace=0, hspace=0)

        self.add_colorbar()

    # ----------------------------------------------------------------------
    def update_impedances(self, montage, electrodes, impedances):
        """"""
        matplotlib.rcParams['text.color'] = "#000000"
        matplotlib.rcParams['font.size'] = 16

        self.ax.clear()

        channels_names = montage.ch_names.copy()
        info = mne.create_info(montage.ch_names, sfreq=1000, ch_types="eeg")
        info.set_montage(montage)

        channels_names = self.remove_overlaping(info, channels_names)
        info = mne.create_info(channels_names, sfreq=1000, ch_types="eeg")
        info.set_montage(montage)

        # cmap = 'RdYlGn'

        channels_mask = np.array(
            [ch in electrodes for ch in channels_names])
        values = [0] * len(channels_mask)

        channels_labels = []
        for ch in channels_names:
            if ch in electrodes:
                label = f'{impedances[ch]:.0f}\,k\Omega'
                channels_labels.append(
                    f'$\\mathsf{{{ch}}}$\n$\\mathsf{{{label}}}$')
            else:
                channels_labels.append(f'$\\mathsf{{{ch}}}$')

        colors = ['#3d7a84', '#3d7a84']
        cmap_ = LinearSegmentedColormap.from_list('plane', colors, N=2)

        mne.viz.plot_topomap(values, info, vmin=-1, vmax=1, contours=0,
                             cmap=cmap_, outlines='skirt', axes=self.ax,
                             names=channels_labels, show_names=True,
                             sensors=True, show=False,
                             mask_params={'marker': ''},
                             mask=channels_mask,
                             )

        q = matplotlib.cm.get_cmap(self.cmap)

        line = self.ax.axes.lines[0]

        channels = np.array(channels_names)[channels_mask]
        for i, (x, y) in enumerate(zip(*line.get_data())):
            color = q(impedances[channels[i]] / 20)
            self.ax.plot([x], [y], marker='o', markerfacecolor=color,
                         markeredgecolor=color, markersize=35, linewidth=0)

        self.draw()

    # ----------------------------------------------------------------------
    def add_colorbar(self):
        """"""
        cax = self.figure.add_axes([0.1, 0.1, 0.8, 0.05])
        norm = matplotlib.colors.Normalize(vmin=0, vmax=15)

        sm = cm.ScalarMappable(cmap=self.cmap, norm=norm)
        cbr = pyplot.colorbar(sm, cax=cax, orientation="horizontal")
        pyplot.setp(pyplot.getp(cbr.ax.axes, 'xticklabels'),
                    color='#ffffff', size=10)
        ticks = [0, 5, 10, 15]
        cbr.set_ticks(ticks)
        cbr.set_ticklabels([f'{i} k$\Omega$' for i in ticks])

    # ----------------------------------------------------------------------

    def remove_overlaping(self, info, channels_names):
        """"""
        locs3d = [ch['loc'][:3] for ch in info['chs']]
        dist = pdist(locs3d)
        problematic_electrodes = []
        if len(locs3d) > 1 and np.min(dist) < 1e-10:
            problematic_electrodes = [
                info['chs'][elec_i]
                for elec_i in squareform(dist < 1e-10).any(axis=0).nonzero()[0]
            ]

        issued = []
        for ch_i in problematic_electrodes:
            for ch_j in problematic_electrodes:
                if ch_i['ch_name'] == ch_j['ch_name']:
                    continue
                if ch_i['ch_name'] in issued and ch_j['ch_name'] in issued:
                    continue
                if pdist([ch_i['loc'][:3], ch_j['loc'][:3]])[0] < 1e-10:
                    issued.extend([ch_i['ch_name'], ch_j['ch_name']])
                    if ch_i['ch_name'] in channels_names:

                        channels_names.pop(channels_names.index(
                            ch_i['ch_name']))

        return channels_names


########################################################################
class Impedances:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, parent, core):
        """Constructor"""

        self.parent = parent
        self.core = core

        if os.getenv('PYSIDEMATERIAL_SECONDARYDARKCOLOR', ''):
            pyplot.rcParams['axes.facecolor'] = os.environ['PYSIDEMATERIAL_SECONDARYDARKCOLOR']
            pyplot.rcParams['figure.facecolor'] = os.environ['PYSIDEMATERIAL_SECONDARYDARKCOLOR']
            pyplot.rcParams['savefig.facecolor'] = os.environ['PYSIDEMATERIAL_SECONDARYDARKCOLOR']

        self.topoplot = Topoplot()
        self.parent.gridLayout_impedances.addWidget(self.topoplot)

        self.update_impedance([0] * len(prop.CHANNELS))

        self.timer = QTimer()

        self.connect()

    # ----------------------------------------------------------------------
    def update_impedance(self, z):
        """"""
        electrodes = list(prop.CHANNELS.values())
        montage = self.core.montage.montage
        impedances = {ch: z for ch, z in zip(electrodes, z)}
        self.topoplot.update_impedances(montage, electrodes, impedances)

    # ----------------------------------------------------------------------
    def connect(self):
        """"""
        self.parent.pushButton_start_impedance_measurement.clicked.connect(
            self.start_impedance_measurement)

    # ----------------------------------------------------------------------
    @thread_this
    def start_impedance_measurement(self):
        """"""
        with OpenBCIConsumer(host=prop.HOST) as stream:
            for data in stream:
                if data.topic == 'eeg':

                    z = self.get_impedance(data.value['data'][0])
                    self.update_impedance(z)

    # ----------------------------------------------------------------------
    def get_impedance(self, data):
        """"""
        return data.mean(axis=1) * 15
