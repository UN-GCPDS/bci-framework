from bci_framework.projects.figure import FigureStream
from bci_framework.projects import properties as prop
from bci_framework.projects.utils import loop_consumer, fake_loop_consumer
import numpy as np
import mne
from matplotlib import cm

from scipy.spatial.distance import pdist, squareform
from matplotlib.colors import LinearSegmentedColormap

from matplotlib import pyplot

import matplotlib

import logging


matplotlib.rcParams['text.color'] = "#ffffff"
matplotlib.rcParams['font.size'] = 16


########################################################################
class Stream(FigureStream):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """"""
        super().__init__()

        self.size = 8, 8

        # self.create_buffer(5)

        self.axis = self.add_subplot(1, 1, 1)
        # self.tight_layout()
        self.cmap = 'RdYlGn'

        self.add_colorbar()
        self.stream()

    # ----------------------------------------------------------------------

    @fake_loop_consumer
    def stream(self, data, topic, frame):
        """"""
        if topic != 'eeg':
            return

        data, _ = data.value['data']
        z = data.mean(axis=1) * 15

        electrodes = list(prop.CHANNELS.values())

        impedances = {ch: z for ch, z in zip(electrodes, z)}

        montage = self.get_mne_montage()
        # info = self.get_info()

        info = mne.create_info(montage.ch_names, sfreq=1000, ch_types="eeg")
        info.set_montage(prop.MONTAGE_NAME)

        channel_names = montage.ch_names.copy()
        channels_names = self.remove_overlaping(info, channel_names)
        info = mne.create_info(channels_names, sfreq=1000, ch_types="eeg")
        info.set_montage(montage)

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
                             cmap=cmap_, outlines='skirt', axes=self.axis,
                             names=channels_labels, show_names=True,
                             sensors=True, show=False,
                             mask_params={'marker': ''},
                             mask=channels_mask,
                             )

        q = matplotlib.cm.get_cmap(self.cmap)
        line = self.axis.axes.lines[0]

        channels = np.array(channels_names)[channels_mask]
        for i, (x, y) in enumerate(zip(*line.get_data())):
            color = q(impedances[channels[i]] / 20)
            self.axis.plot([x], [y], marker='o', markerfacecolor=color,
                           markeredgecolor=color, markersize=35, linewidth=0)

        self.feed()

        logging.warning('feed')

    # ----------------------------------------------------------------------
    def add_colorbar(self):
        """"""
        cax = self.add_axes([0.1, 0.1, 0.8, 0.05])
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


if __name__ == '__main__':
    Stream()
