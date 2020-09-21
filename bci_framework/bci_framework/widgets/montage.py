import os
import json
from PySide2 import QtCore, QtGui, QtWidgets

from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QLabel, QComboBox, QTableWidgetItem, QLineEdit

import mne
import numpy as np
import time

import matplotlib
from matplotlib import cm, pyplot
from matplotlib.figure import Figure
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from scipy.spatial.distance import pdist, squareform, cdist

from openbci_stream.consumer import OpenBCIConsumer


from gcpds.utils.filters import GenericButterBand, notch60, FiltersChain

# from ..config_manager import ConfigManager
from ..projects import properties as prop
from ..projects.figure import thread_this, subprocess_this


########################################################################
class FigureTopo(FigureCanvas):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        super().__init__(Figure(figsize=(1, 1), dpi=90))
        self.resize_timer = QTimer()
        self.resize_timer.timeout.connect(self.do_resize_now)

    # ----------------------------------------------------------------------
    def resizeEvent(self, event):
        """"""
        self.lastEvent = (event.size().width(), event.size().height())
        self.resize_timer.stop()
        self.resize_timer.start(200)

    # ----------------------------------------------------------------------
    def do_resize_now(self):
        newsize = QtCore.QSize(*self.lastEvent)
        # create new event from the stored size
        event = QtGui.QResizeEvent(newsize, QtCore.QSize(1, 1))
        # print "Now I let you resize."
        # and propagate the event to let the canvas resize.
        super().resizeEvent(event)


########################################################################
class TopoplotMontage(FigureTopo):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        super().__init__()
        # self.connect_resize()
        self.ax = self.figure.add_subplot(111)
        self.reset_plot()

    # ----------------------------------------------------------------------
    def reset_plot(self):
        """"""
        # self.ax = self.figure.add_subplot(111)
        self.figure.subplots_adjust(
            left=0.03, bottom=0.08, right=0.97, top=0.97, wspace=0, hspace=0)

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
class TopoplotImpedances(FigureTopo):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """"""
        super().__init__()
        self.ax = self.figure.add_subplot(111)
        self.cax = self.figure.add_axes([0.1, 0.1, 0.8, 0.05])
        self.cmap = 'RdYlGn'

        f = GenericButterBand(27, 37, fs=250)
        self.impedance_filter = FiltersChain(notch60, f)
        self.reset_plot()

    # ----------------------------------------------------------------------
    def reset_plot(self):
        """"""
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

                if impedances[ch] == '??':
                    label = f'??\,\Omega'

                elif impedances[ch] < 100:

                    z1 = int(impedances[ch])
                    z2 = int(np.ceil((impedances[ch] % 1) * 10))
                    label = f'{z1}k{z2}\,\Omega'
                else:
                    label = f'\infty \,\Omega'

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

        index = [l.get_marker() for l in self.ax.axes.lines].index('')
        line = self.ax.axes.lines[index]

        # if self.ax.axes.lines[0].get_data()[0].shape[0] == len(impedances):
        channels = np.array(channels_names)[channels_mask]
        for i, (x, y) in enumerate(zip(*line.get_data())):
            try:
                if impedances[channels[i]] == '??':
                    color = q(0)
                else:
                    color = q(impedances[channels[i]] / 20)
                self.ax.plot([x], [y], marker='o', markerfacecolor=color,
                             markeredgecolor=color, markersize=35, linewidth=0)
                # self.draw()
            except IndexError:
                return
        # else:
            # self.reset_plot()
        self.draw()

    # ----------------------------------------------------------------------
    def add_colorbar(self):
        """"""
        # self.cax = self.figure.add_axes([0.1, 0.1, 0.8, 0.05])
        norm = matplotlib.colors.Normalize(vmin=0, vmax=15)

        sm = cm.ScalarMappable(cmap=self.cmap, norm=norm)
        cbr = pyplot.colorbar(sm, cax=self.cax, orientation="horizontal")
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
class Montage:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, core):
        """Constructor"""
        self.parent_frame = core.main
        self.core = core

        if os.getenv('PYSIDEMATERIAL_SECONDARYDARKCOLOR', ''):
            pyplot.rcParams['axes.facecolor'] = os.environ['PYSIDEMATERIAL_SECONDARYDARKCOLOR']
            pyplot.rcParams['figure.facecolor'] = os.environ['PYSIDEMATERIAL_SECONDARYDARKCOLOR']
            pyplot.rcParams['savefig.facecolor'] = os.environ['PYSIDEMATERIAL_SECONDARYDARKCOLOR']

        self.channels_names_widgets = []

        self.topoplot = TopoplotMontage()
        self.parent_frame.gridLayout_montage.addWidget(self.topoplot)

        self.parent_frame.comboBox_montages.addItems(
            mne.channels.get_builtin_montages())

        self.parent_frame.comboBox_montage_channels.addItems(
            [f"{i+1} channel{'s'[:i]}" for i in range(16)])

        self.set_saved_montages()
        self.update_environ()
        self.connect()

        self.topoplot_impedance = TopoplotImpedances()
        self.parent_frame.gridLayout_impedances.addWidget(
            self.topoplot_impedance)
        self.update_impedance()

        self.load_montage()

        QTimer().singleShot(10, self.set_spliter_position)

    # ----------------------------------------------------------------------
    def update_impedance(self, z=None):
        """"""
        electrodes = list(prop.CHANNELS.values())
        montage = self.get_mne_montage()

        if z is None:
            z = ['??'] * len(electrodes)

        impedances = {ch: z for ch, z in zip(electrodes, z)}
        self.topoplot_impedance.update_impedances(
            montage, electrodes, impedances)

    # ----------------------------------------------------------------------
    def set_spliter_position(self):
        """"""
        self.parent_frame.splitter_montage.moveSplitter(
            self.parent_frame.splitter_montage.getRange(1)[1] // 2, 1)

    # ----------------------------------------------------------------------
    def connect(self):
        """"""
        self.parent_frame.comboBox_montages.activated.connect(
            self.update_topoplot)
        # self.parent.comboBox_historical_montages.activated.connect(
        # lambda evt: self.load_montage(self.parent.comboBox_historical_montages.currentText()))
        # self.parent.comboBox_historical_montages.editTextChanged.connect(
        # lambda evt: self.parent.pushButton_save_montage.setEnabled(bool(self.parent.comboBox_historical_montages.currentText())))

        self.parent_frame.comboBox_montage_channels.activated.connect(
            self.update_topoplot)
        self.parent_frame.comboBox_montage_channels.activated.connect(
            self.update_topoplot)

        self.parent_frame.pushButton_save_montage.clicked.connect(
            self.save_montage)
        self.parent_frame.pushButton_remove_montage.clicked.connect(
            self.delete_montage)

        self.parent_frame.tableWidget_montages.itemDoubleClicked.connect(
            self.load_montage)

        self.parent_frame.checkBox_view_impedances.clicked.connect(
            self.change_plot)

    # ----------------------------------------------------------------------
    def change_plot(self):
        """"""
        if self.parent_frame.checkBox_view_impedances.isChecked():  # impedances
            self.parent_frame.stackedWidget_montage.setCurrentIndex(1)
            # self.topoplot_impedance.configure()
        else:  # montage
            self.parent_frame.stackedWidget_montage.setCurrentIndex(0)

        self.start_impedance_measurement()

    # # ----------------------------------------------------------------------
    # def update_montage(self):
        # """"""
        # self.montage_name = self.parent.comboBox_montages.currentText()
        # self.montage = mne.channels.make_standard_montage(self.montage_name)

    # ----------------------------------------------------------------------
    def get_mne_montage(self):
        """"""
        montage_name = self.parent_frame.comboBox_montages.currentText()
        montage = mne.channels.make_standard_montage(montage_name)
        return montage

    # ----------------------------------------------------------------------
    def update_topoplot(self):
        """"""
        # montage_name = self.parent.comboBox_montages.currentText()
        # self.montage = mne.channels.make_standard_montage(montage_name)
        montage = self.get_mne_montage()

        channels = self.parent_frame.comboBox_montage_channels.currentIndex() + 1

        self.generate_list_channels()
        electrodes = [ch.currentText() for ch in self.channels_names_widgets]

        self.topoplot.update_montage(
            montage, electrodes, channels)

        self.validate_channels()
        self.update_environ()

        self.topoplot_impedance.reset_plot()
        self.update_impedance()

    # ----------------------------------------------------------------------
    def generate_list_channels(self):
        """"""
        for layout in [self.parent_frame.gridLayout_list_channels_right, self.parent_frame.gridLayout_list_channels_left]:

            for i in reversed(range(layout.count())):
                if item := layout.takeAt(i):
                    item.widget().deleteLater()

            # layout.setColumnStretch(0, 1)
            layout.setColumnStretch(1, 1)

        if self.channels_names_widgets:
            previous_labels = [ch.currentText()
                               for ch in self.channels_names_widgets]
        else:
            previous_labels = []

        self.channels_names_widgets = []
        self.labels_names_widgets = []
        montage = self.get_mne_montage()
        # for i in range(self.parent.spinBox_montage_channels.value()):
        for i in range(self.parent_frame.comboBox_montage_channels.currentIndex() + 1):

            if i % 2:
                layout = self.parent_frame.gridLayout_list_channels_right
            else:
                layout = self.parent_frame.gridLayout_list_channels_left

            channel_label = QLabel(f'CH{i+1}')
            self.labels_names_widgets.append(channel_label)
            layout.addWidget(channel_label)

            channel_name = QComboBox()
            channel_name.addItems(['Off'] + montage.ch_names)

            if len(previous_labels) > i and previous_labels[i] in montage.ch_names:
                index = montage.ch_names.index(previous_labels[i])
            elif len(previous_labels) > i and previous_labels[i] == 'Off':
                index = -1
            else:
                index = i
            channel_name.setCurrentIndex(index + 1)
            channel_name.activated.connect(self.update_topoplot)
            self.channels_names_widgets.append(channel_name)

            layout.addWidget(channel_name)

    # # ----------------------------------------------------------------------
    # def generate_list_impedances(self):
        # """"""
        # for layout in [self.parent.gridLayout_list_impedances_right, self.parent.gridLayout_list_impedances_left]:

            # for i in reversed(range(layout.count())):
            # if item := layout.takeAt(i):
            # item.widget().deleteLater()

            # # layout.setColumnStretch(0, 1)
            # layout.setColumnStretch(1, 1)

        # # if self.channels_names_widgets:
            # # previous_labels = [ch.currentText()
            # # for ch in self.channels_names_widgets]
        # # else:
            # # previous_labels = []

        # self.impedance_names_widgets = []
        # self.labels_impedance_widgets = []
        # # montage = self.get_mne_montage()
        # # for i in range(self.parent.spinBox_montage_channels.value()):
        # for i in range(self.parent.comboBox_montage_channels.currentIndex() + 1):

            # if i % 2:
            # layout = self.parent.gridLayout_list_impedances_right
            # else:
            # layout = self.parent.gridLayout_list_impedances_left

            # channel_label = QLabel(f'CH{i+1}')
            # self.labels_impedance_widgets.append(channel_label)
            # layout.addWidget(channel_label)

            # channel_name = QLineEdit()
            # channel_name.setText('?? K \Omenga')

            # self.impedance_names_widgets.append(channel_name)

            # layout.addWidget(channel_name)

    # #----------------------------------------------------------------------
    # def update_montage_name(self):
        # """"""
        # channels_names = ','.join([ch.currentText() for ch in self.channels_names_widgets])
        # self.parent.comboBox_historical_montages.setCurrentText(f'{self.montage_name} [{len(self.channels_names_widgets)}CH] [{channels_names}]')

    # ----------------------------------------------------------------------

    def save_montage(self):
        """"""
        montage_name = self.parent_frame.comboBox_montages.currentText()
        channels_names = ','.join([ch.currentText()
                                   for ch in self.channels_names_widgets])

        # saved_montages = self.config['montages']
        for i in range(1, 17):
            if not self.core.config.has_option('montages', f'montage{i}'):
                self.core.config.set(
                    'montages', f'montage{i}', f"{montage_name}|{channels_names}")
                # self.parent.comboBox_historical_montages.addItem(name)
                self.core.config.save()
                self.set_saved_montages()
                return
    # ----------------------------------------------------------------------

    def delete_montage(self, event=None):
        """"""
        row = self.parent_frame.tableWidget_montages.currentRow()
        config_name = self.parent_frame.tableWidget_montages.item(
            row, 0).config_name
        self.core.config.remove_option('montages', config_name)
        self.core.config.save()
        self.set_saved_montages()

    # ----------------------------------------------------------------------
    def set_saved_montages(self):
        """"""
        self.parent_frame.tableWidget_montages.clear()

        self.parent_frame.tableWidget_montages.setRowCount(0)
        self.parent_frame.tableWidget_montages.setColumnCount(3)

        self.parent_frame.tableWidget_montages.setHorizontalHeaderLabels(
            ['Montage', 'Channels', 'Electrodes'])

        saved_montages = self.core.config['montages']

        i = 0
        for saved in saved_montages.keys():
            if not saved.startswith('montage'):
                continue
            montage, electrodes = saved_montages.get(saved).split('|')

            self.parent_frame.tableWidget_montages.insertRow(i)

            # try:
            item = QTableWidgetItem(montage)
            item.config_name = saved

            self.parent_frame.tableWidget_montages.setItem(
                i, 0, item)
            self.parent_frame.tableWidget_montages.setItem(
                i, 1, QTableWidgetItem(f"{len(electrodes.split(','))-electrodes.split(',').count('Off')} ch"))
            self.parent_frame.tableWidget_montages.setItem(
                i, 2, QTableWidgetItem(' '.join(electrodes.split(','))))

            i += 1

    # ----------------------------------------------------------------------
    def load_montage(self, event=None):
        """"""
        # saved_montages = self.core.config['montages']

        if event is None:
            montage_name, channels = self.core.config.get(
                'montages', 'last_montage').split('|')
            channels = channels.split(',')
        else:
            montage_name = self.parent_frame.tableWidget_montages.item(
                event.row(), 0).text()
            channels = self.parent_frame.tableWidget_montages.item(
                event.row(), 2).text()
            channels = channels.split(' ')
            self.core.config.set('montages', 'last_montage',
                                 f"{montage_name}|{','.join(channels)}")
            self.core.config.save()

        # self.montage_name = montage_name

        self.parent_frame.comboBox_montages.setCurrentText(montage_name)
        # self.montage = mne.channels.make_standard_montage(self.montage_name)
        # self.parent.spinBox_montage_channels.setMaximum(
        # len(self.montage.ch_names))
        # self.parent.spinBox_montage_channels.setValue(len(channels))
        self.parent_frame.comboBox_montage_channels.setCurrentIndex(
            len(channels) - 1)

        self.generate_list_channels()
        # self.generate_list_impedances()
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
                    "QLabel{color: #ff1744;}QLabel:disabled{color: rgba(255, 23, 68, 0.2)};")
            else:
                label.setStyleSheet(
                    f"QLabel{{color: {os.environ.get('PYSIDEMATERIAL_SECONDARYTEXTCOLOR', '')};}}"
                    f"QLabel:disabled{{color: rgba(255, 255, 255, 0.2) }}")

    # ----------------------------------------------------------------------
    def get_montage(self):
        """"""
        return {i + 1: ch.currentText() for i, ch in enumerate((self.channels_names_widgets)) if ch.currentText() != 'Off'}

    # ----------------------------------------------------------------------
    def update_environ(self):
        """"""
        os.environ['BCISTREAM_CHANNELS'] = json.dumps(self.get_montage())
        os.environ['BCISTREAM_MONTAGE_NAME'] = json.dumps(
            self.parent_frame.comboBox_montages.currentText())
        os.environ['BCISTREAM_DAISY'] = json.dumps(
            bool(list(filter(lambda x: x > 8, self.get_montage().keys()))))

    # ----------------------------------------------------------------------
    @thread_this
    def start_impedance_measurement(self):
        """"""
        if self.parent_frame.checkBox_view_impedances.isChecked():

            if not hasattr(self.core.connection, 'openbci'):
                self.core.connection.openbci_connect()

            # self.topoplot_impedance.configure_filters()

            openbci = self.core.connection.openbci
            openbci.stop_stream()

            # openbci.command(openbci.SAMPLE_RATE_250SPS)

            openbci.command(openbci.DEFAULT_CHANNELS_SETTINGS)
            openbci.leadoff_impedance(prop.CHANNELS,
                                      pchan=openbci.TEST_SIGNAL_NOT_APPLIED,
                                      nchan=openbci.TEST_SIGNAL_APPLIED)
            openbci.start_stream()

            self.measuring_impedance = True
            with OpenBCIConsumer(host=prop.HOST) as stream:
                for data in stream:
                    if data.topic == 'eeg':

                        z = self.get_impedance(data.value['data'][0])
                        self.update_impedance(z)

                        if not self.measuring_impedance:
                            openbci.stop_stream()
                            self.core.connection.session_settings()
                            # openbci.command(openbci.SAMPLE_RATE_250SPS)
                            openbci.start_stream()
                            break

        else:
            self.measuring_impedance = False

    # ----------------------------------------------------------------------
    def get_impedance(self, data):
        """"""
        data = self.topoplot_impedance.impedance_filter(data, axis=1)
        rms = (data.max(axis=1) - data.min(axis=1)) / (2 * np.sqrt(2))

        z = (rms * 1e-6 * np.sqrt(2) / 6e-9) - 2200
        z[z < 0] = 0

        return z / 1000
