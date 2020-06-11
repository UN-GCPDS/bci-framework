import os
import json

import mne
import numpy as np

from PySide2.QtWidgets import QLabel, QComboBox
from ..config_manager import ConfigManager


from cycler import cycler
import matplotlib
from matplotlib import pyplot
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

matplotlib.use('Qt5Agg')
pyplot.style.use('dark_background')
q = matplotlib.cm.get_cmap('tab20')
matplotlib.rcParams['axes.prop_cycle'] = cycler(color=[q(m) for m in np.linspace(0, 1, 16)])
# matplotlib.rcParams['figure.dpi'] = 90




########################################################################
class Topoplot(FigureCanvas):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        super().__init__(Figure(figsize=(1, 1), dpi=90))

        self.ax = self.figure.add_subplot(111)
        self.figure.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)



########################################################################
class Montage:
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""

        self.channels_names_widgets = []

        self.parent = parent

        self.topoplot = Topoplot()
        self.parent.gridLayout_montage.addWidget(self.topoplot)

        self.config = ConfigManager()

        self.parent.comboBox_montages.addItems(mne.channels.get_builtin_montages())

        self.set_saved_montages()
        self.load_montage()
        self.update_environ()

        self.connect()


    #----------------------------------------------------------------------
    def connect(self):
        """"""

        self.parent.comboBox_montages.activated.connect(self.update_montage)
        self.parent.comboBox_historical_montages.activated.connect(lambda evt: self.load_montage(self.parent.comboBox_historical_montages.currentText()))
        self.parent.comboBox_historical_montages.editTextChanged.connect(lambda evt: self.parent.pushButton_save_montage.setEnabled(bool(self.parent.comboBox_historical_montages.currentText())))

        self.parent.spinBox_montage_channels.valueChanged.connect(self.generate_list_channels)
        self.parent.spinBox_montage_channels.valueChanged.connect(self.update_topoplot)

        self.parent.pushButton_save_montage.clicked.connect(self.save_montage)


    #----------------------------------------------------------------------
    def update_montage(self):
        """"""

        self.montage_name = self.parent.comboBox_montages.currentText()
        self.montage = mne.channels.make_standard_montage(self.montage_name)
        self.parent.spinBox_montage_channels.setMaximum(len(self.montage.ch_names))

        # self.generate_list_channels()
        # self.update_topoplot()




    #----------------------------------------------------------------------
    def update_topoplot(self):
        """"""

        matplotlib.rcParams['text.color'] = "#ffffff"
        matplotlib.rcParams['font.size'] = 16

        self.topoplot.ax.clear()

        electrodes = [ch.currentText() for ch in self.channels_names_widgets]
        # info = mne.create_info(channels_names, sfreq=1000, ch_types="eeg", montage=self.montage)


        channels_names = self.montage.ch_names.copy()
        info = mne.create_info(channels_names, sfreq=1000, ch_types="eeg", montage=self.montage)
        for i in range(len(self.montage.ch_names)):
            for j in range(len(self.montage.ch_names)):
                if i < j:
                    if (info['chs'][i]['loc'][:3] == info['chs'][j]['loc'][:3]).all():
                        print(self.montage.ch_names[i], self.montage.ch_names[j])
                        channels_names.pop(channels_names.index(self.montage.ch_names[i]))
        info = mne.create_info(channels_names, sfreq=1000, ch_types="eeg", montage=self.montage)


        channels_mask = np.array([ch in electrodes for ch in channels_names])
        values = [0] * len(channels_mask)
        # channels_labels = [f'$\\mathsf{{\\frac{{{ch}}}{{ch{i+1}}}}}$' for i, ch in enumerate(channels_names)]

        channels_labels = []
        # i = 0
        for ch in channels_names:
            if ch in electrodes:
                i = electrodes.index(ch)
                channels_labels.append(f'$\\mathsf{{\\frac{{{ch}}}{{ch{i+1}}}}}$')
                # i += 1
            else:
                channels_labels.append(f'$\\mathsf{{{ch}}}$')




        colors = ['#009faf', '#009faf']
        cm = LinearSegmentedColormap.from_list('plane', colors, N=2)


        mne.viz.plot_topomap(values, info, vmin=-1, vmax=1, contours=0, cmap=cm, outlines='skirt', names=channels_labels, show_names=True, axes=self.topoplot.ax, sensors=True, show=False,
                               mask_params=dict(marker='o', markerfacecolor='#263238', markeredgecolor='#4f5b62', linewidth=0, markersize=30),
                               mask=channels_mask,
                               )
        self.topoplot.draw()
        # self.update_montage_name()
        self.validate_channels()




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
            previous_labels = [ch.currentText() for ch in self.channels_names_widgets]
        else:
            previous_labels = []

        self.channels_names_widgets = []
        self.labels_names_widgets = []
        for i in range(self.parent.spinBox_montage_channels.value()):

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
            else:
                index = i
            channel_name.setCurrentIndex(index+1)
            channel_name.activated.connect(self.update_topoplot)
            self.channels_names_widgets.append(channel_name)

            layout.addWidget(channel_name)


    # #----------------------------------------------------------------------
    # def update_montage_name(self):
        # """"""
        # channels_names = ','.join([ch.currentText() for ch in self.channels_names_widgets])
        # self.parent.comboBox_historical_montages.setCurrentText(f'{self.montage_name} [{len(self.channels_names_widgets)}CH] [{channels_names}]')


    #----------------------------------------------------------------------
    def save_montage(self):
        """"""
        name = self.parent.comboBox_historical_montages.currentText()
        montage_name = self.montage_name
        channels_names = ','.join([ch.currentText() for ch in self.channels_names_widgets])

        # saved_montages = self.config['montages']
        for i in range(1, 17):
            if not self.config.has_option('montages', f'montage{i}'):
                self.config.set('montages', f'montage{i}', f"{name}|{montage_name}|{channels_names}")
                self.parent.comboBox_historical_montages.addItem(name)
                self.config.save()
                return


    #----------------------------------------------------------------------
    def set_saved_montages(self):
        """"""
        saved_montages = self.config['montages']

        for saved in saved_montages.keys():
            # if saved.endswith('name'):
            # m = saved.replace('_name', '')
            name, *_ = saved_montages.get(saved).split('|')
            # name = saved_montages.get(f"{m}_name")
            self.parent.comboBox_historical_montages.addItem(name)

        self.parent.comboBox_historical_montages.setCurrentText('')



    #----------------------------------------------------------------------
    def load_montage(self, name=None):
        """"""
        saved_montages = self.config['montages']

        if name is None:
            name = list(saved_montages.items())[0][1].split('|')[0]
            self.parent.comboBox_historical_montages.setCurrentText(name)

        for saved in saved_montages.keys():
            saved_name, montage, channels = saved_montages.get(saved).split('|')
            if name == saved_name:
                break

        channels = channels.split(',')

        self.montage_name = montage
        self.parent.comboBox_montages.setCurrentText(self.montage_name)
        self.montage = mne.channels.make_standard_montage(self.montage_name)
        self.parent.spinBox_montage_channels.setMaximum(len(self.montage.ch_names))
        self.parent.spinBox_montage_channels.setValue(len(channels))

        self.generate_list_channels()
        [wg.setCurrentText(ch) for wg,ch in zip(self.channels_names_widgets, channels)]
        self.update_topoplot()


    #----------------------------------------------------------------------
    def validate_channels(self):
        """"""
        channels = [ch.currentText() for ch in self.channels_names_widgets]
        for channel, label in zip(channels, self.labels_names_widgets):
            if channels.count(channel) > 1:
                label.setStyleSheet("*{color: #ff1744;}")
            else:
                label.setStyleSheet("*{color: white;}")


    #----------------------------------------------------------------------
    def get_montage(self):
        """"""
        return {i: ch.currentText() for i, ch in enumerate((self.channels_names_widgets)) if ch.currentText() != 'Off'}



    #----------------------------------------------------------------------
    def update_environ(self):
        """"""
        os.environ['BCISTREAM_MONTAGE'] = json.dumps(self.get_montage())
