import os
import json

import mne
import numpy as np

from PySide2.QtWidgets import QLabel, QComboBox
from ..config_manager import ConfigManager

from scipy.spatial.distance import pdist, squareform, cdist


import matplotlib
from matplotlib import pyplot
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


########################################################################
class Topoplot(FigureCanvas):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        super().__init__(Figure(figsize=(1, 1), dpi=90))

        self.ax = self.figure.add_subplot(111)
        self.figure.subplots_adjust(
            left=0.03, bottom=0.03, right=0.97, top=0.97, wspace=0, hspace=0)

    # ----------------------------------------------------------------------
    def update_montage(self, montage, electrodes, channels):
        """"""
        matplotlib.rcParams['text.color'] = "#ffffff"
        matplotlib.rcParams['font.size'] = 16

        self.ax.clear()

        # montage = mne.channels.make_standard_montage(montage_name)
        channels_names = montage.ch_names.copy()

        info = mne.create_info(channels_names, sfreq=1000, ch_types="eeg")
        info.set_montage(montage)

        info
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

                        # print(ch_i['ch_name'], ch_j['ch_name'])
                        channels_names.pop(channels_names.index(
                            ch_i['ch_name']))

        info = mne.create_info(channels_names, sfreq=1000, ch_types="eeg")
        info.set_montage(montage)

        channels_mask = np.array(
            [ch in electrodes for ch in channels_names])
        values = [0] * len(channels_mask)

        channels_labels = []
        for ch in channels_names:
            if ch in electrodes:
                i = electrodes.index(ch)
                channels_labels.append(
                    f'$\\mathsf{{{ch}}}$\n$\\mathsf{{ch{i+1}}}$')
            else:
                channels_labels.append(f'$\\mathsf{{{ch}}}$')

        colors = ['#3d7a84', '#3d7a84']
        cm = LinearSegmentedColormap.from_list('plane', colors, N=2)

        mne.viz.plot_topomap(values, info, vmin=-1, vmax=1, contours=0, cmap=cm, outlines='skirt', names=channels_labels, show_names=True, axes=self.ax, sensors=True, show=False,
                             mask_params=dict(marker='o', markerfacecolor='#263238',
                                              markeredgecolor='#4f5b62', linewidth=0, markersize=35),
                             mask=channels_mask,
                             )

        self.draw()


########################################################################
class Montage:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, core):
        """Constructor"""
        self.parent = core.main
        self.core = core

        if os.getenv('PYSIDEMATERIAL_SECONDARYDARKCOLOR', ''):
            pyplot.rcParams['axes.facecolor'] = os.environ['PYSIDEMATERIAL_SECONDARYDARKCOLOR']
            pyplot.rcParams['figure.facecolor'] = os.environ['PYSIDEMATERIAL_SECONDARYDARKCOLOR']
            pyplot.rcParams['savefig.facecolor'] = os.environ['PYSIDEMATERIAL_SECONDARYDARKCOLOR']

        self.channels_names_widgets = []

        self.topoplot = Topoplot()
        self.parent.gridLayout_montage.addWidget(self.topoplot)

        # self.config = ConfigManager()

        self.config = {

            'last_montage': self.parent.comboBox_historical_montages,
        }

        self.parent.comboBox_montages.addItems(
            mne.channels.get_builtin_montages())

        self.parent.comboBox_montage_channels.addItems(
            [f"{i+1} channel{'s'[:i]}" for i in range(16)])

        self.set_saved_montages()
        self.load_config()

        self.load_montage()
        self.update_environ()
        self.connect()
        self.core.config.connect_widgets(self.update_config, self.config)

    # ----------------------------------------------------------------------
    def load_config(self):
        """"""
        self.core.config.load_widgets('montages', self.config)

    # ----------------------------------------------------------------------
    def update_config(self, *args, **kwargs):
        """"""
        self.core.config.save_widgets('montages', self.config)

    # ----------------------------------------------------------------------
    def connect(self):
        """"""
        self.parent.comboBox_montages.activated.connect(self.update_topoplot)
        self.parent.comboBox_historical_montages.activated.connect(
            lambda evt: self.load_montage(self.parent.comboBox_historical_montages.currentText()))
        self.parent.comboBox_historical_montages.editTextChanged.connect(
            lambda evt: self.parent.pushButton_save_montage.setEnabled(bool(self.parent.comboBox_historical_montages.currentText())))

        self.parent.comboBox_montage_channels.activated.connect(
            self.update_topoplot)
        self.parent.comboBox_montage_channels.activated.connect(
            self.update_topoplot)

        self.parent.pushButton_save_montage.clicked.connect(self.save_montage)

    # # ----------------------------------------------------------------------
    # def update_montage(self):
        # """"""
        # self.montage_name = self.parent.comboBox_montages.currentText()
        # self.montage = mne.channels.make_standard_montage(self.montage_name)

    # ----------------------------------------------------------------------
    def update_topoplot(self):
        """"""
        montage_name = self.parent.comboBox_montages.currentText()
        self.montage = mne.channels.make_standard_montage(montage_name)

        channels = self.parent.comboBox_montage_channels.currentIndex() + 1

        self.generate_list_channels()
        electrodes = [ch.currentText() for ch in self.channels_names_widgets]

        self.topoplot.update_montage(
            self.montage, electrodes, channels)

        self.validate_channels()
        self.update_environ()

    # ----------------------------------------------------------------------
    def generate_list_channels(self):
        """"""
        for layout in [self.parent.gridLayout_list_channels_right, self.parent.gridLayout_list_channels_left]:

            for i in reversed(range(layout.count())):
                if item := layout.takeAt(i):
                    item.widget().deleteLater()

            layout.setColumnStretch(0, 1)
            layout.setColumnStretch(1, 1)

        if self.channels_names_widgets:
            previous_labels = [ch.currentText()
                               for ch in self.channels_names_widgets]
        else:
            previous_labels = []

        self.channels_names_widgets = []
        self.labels_names_widgets = []
        # for i in range(self.parent.spinBox_montage_channels.value()):
        for i in range(self.parent.comboBox_montage_channels.currentIndex() + 1):

            if i % 2:
                layout = self.parent.gridLayout_list_channels_right
            else:
                layout = self.parent.gridLayout_list_channels_left

            channel_label = QLabel(f'CH{i+1}')
            self.labels_names_widgets.append(channel_label)
            layout.addWidget(channel_label)

            channel_name = QComboBox()
            channel_name.addItems(['Off'] + self.montage.ch_names)

            if len(previous_labels) > i and previous_labels[i] in self.montage.ch_names:
                index = self.montage.ch_names.index(previous_labels[i])
            elif previous_labels and previous_labels[i] == 'Off':
                index = -1
            else:
                index = i
            channel_name.setCurrentIndex(index + 1)
            channel_name.activated.connect(self.update_topoplot)
            self.channels_names_widgets.append(channel_name)

            layout.addWidget(channel_name)

    # #----------------------------------------------------------------------
    # def update_montage_name(self):
        # """"""
        # channels_names = ','.join([ch.currentText() for ch in self.channels_names_widgets])
        # self.parent.comboBox_historical_montages.setCurrentText(f'{self.montage_name} [{len(self.channels_names_widgets)}CH] [{channels_names}]')

    # ----------------------------------------------------------------------
    def save_montage(self):
        """"""
        name = self.parent.comboBox_historical_montages.currentText()
        montage_name = self.montage_name
        channels_names = ','.join([ch.currentText()
                                   for ch in self.channels_names_widgets])

        # saved_montages = self.config['montages']
        for i in range(1, 17):
            if not self.core.config.has_option('montages', f'montage{i}'):
                self.core.config.set(
                    'montages', f'montage{i}', f"{name}|{montage_name}|{channels_names}")
                self.parent.comboBox_historical_montages.addItem(name)
                self.core.config.save()
                return

    # ----------------------------------------------------------------------
    def set_saved_montages(self):
        """"""
        saved_montages = self.core.config['montages']

        for saved in saved_montages.keys():
            if not saved.startswith('montage'):
                continue
            # if saved.endswith('name'):
            # m = saved.replace('_name', '')
            name, *_ = saved_montages.get(saved).split('|')
            # name = saved_montages.get(f"{m}_name")
            self.parent.comboBox_historical_montages.addItem(name)

        self.parent.comboBox_historical_montages.setCurrentText('')

    # ----------------------------------------------------------------------
    def load_montage(self, name=None):
        """"""
        saved_montages = self.core.config['montages']

        if name is None:
            name = self.core.config.get('montages', 'last_montage')
            self.parent.comboBox_historical_montages.setCurrentText(name)

        for saved in saved_montages.keys():
            if not saved.startswith('montage'):
                continue
            saved_name, montage, channels = saved_montages.get(
                saved).split('|')
            if name == saved_name:
                break

        channels = channels.split(',')

        self.montage_name = montage
        self.parent.comboBox_montages.setCurrentText(self.montage_name)
        self.montage = mne.channels.make_standard_montage(self.montage_name)
        # self.parent.spinBox_montage_channels.setMaximum(
            # len(self.montage.ch_names))
        # self.parent.spinBox_montage_channels.setValue(len(channels))
        self.parent.comboBox_montage_channels.setCurrentIndex(
            len(channels) - 1)

        self.generate_list_channels()
        [wg.setCurrentText(ch) for wg, ch in zip(
            self.channels_names_widgets, channels)]
        self.update_topoplot()

    # ----------------------------------------------------------------------
    def validate_channels(self):
        """"""
        channels = [ch.currentText() for ch in self.channels_names_widgets]
        for channel, label in zip(channels, self.labels_names_widgets):
            if channels.count(channel) > 1:
                label.setStyleSheet(
                    "QLabel{color: #ff1744;}QLabel:disabled{color: rgb(255, 23, 68, 0.2)};")
            else:
                label.setStyleSheet(
                    f"QLabel{{color: {os.environ.get('PYSIDEMATERIAL_SECONDARYTEXTCOLOR', '')};}}"
                    f"QLabel:disabled{{color: rgb(255, 255, 255, 0.2) }}")

    # ----------------------------------------------------------------------
    def get_montage(self):
        """"""
        return {i + 1: ch.currentText() for i, ch in enumerate((self.channels_names_widgets)) if ch.currentText() != 'Off'}

    # ----------------------------------------------------------------------
    def update_environ(self):
        """"""
        os.environ['BCISTREAM_CHANNELS'] = json.dumps(self.get_montage())
        os.environ['BCISTREAM_MONTAGE_NAME'] = json.dumps(self.montage_name)
        os.environ['BCISTREAM_DAISY'] = json.dumps(
            bool(list(filter(lambda x: x > 8, self.get_montage().keys()))))
