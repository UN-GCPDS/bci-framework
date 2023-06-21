"""
=======
Montage
=======
"""

import os
import json
import logging
from typing import List, TypeVar, Dict, Optional

from PySide6.QtGui import QCursor
from PySide6.QtCore import QTimer, QSize, Qt
from PySide6.QtWidgets import (
    QLabel,
    QComboBox,
    QTableWidgetItem,
    QApplication,
    QCheckBox,
    QHeaderView,
)
from PySide6.QtGui import QResizeEvent

import mne
import numpy as np
from scipy.spatial.distance import pdist, squareform, euclidean
import matplotlib
from matplotlib import cm, pyplot
from matplotlib.figure import Figure
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
)

from openbci_stream.acquisition import OpenBCIConsumer
from gcpds.filters import frequency as filters

from ...extensions import properties as prop
from ...extensions.data_analysis.utils import thread_this


from mne.channels.layout import _find_topomap_coords

try:
    matplotlib.rcParams['axes.edgecolor'] = 'k'
except:
    # 'rcParams' object does not support item assignment
    pass

VOLTS = TypeVar('Volts')
IMPEDANCE = TypeVar('Impedance')


########################################################################
class TopoplotBase(FigureCanvas):
    """The figure will try to resize so fast that freezes the main window."""

    # ----------------------------------------------------------------------
    def __init__(self):
        """"""
        super().__init__(Figure(figsize=(1, 1), dpi=90))
        self.resize_timer = QTimer()
        self.resize_timer.timeout.connect(self.do_resize_now)

    # ----------------------------------------------------------------------
    def resizeEvent(self, event) -> None:
        """Slow down the resize event."""
        self.figure.set_visible(False)
        self.draw()
        self.lastEvent = (event.size().width(), event.size().height())
        self.resize_timer.stop()
        self.resize_timer.start(50)

    # ----------------------------------------------------------------------
    def do_resize_now(self) -> None:
        """Resize plot."""
        self.resize_timer.stop()
        newsize = QSize(*self.lastEvent)
        event = QResizeEvent(newsize, QSize(1, 1))
        super().resizeEvent(event)
        self.figure.set_visible(True)
        self.redraw()

    # ----------------------------------------------------------------------
    def redraw(self):
        """"""
        if args := getattr(self, 'args_update', False):
            if hasattr(self, 'update_montage'):
                self.update_montage(*args)
            else:
                self.update_impedances(*args)
        else:
            self.draw()


########################################################################
class DragAndDropMontage:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.mpl_connect('button_press_event', self.on_press)
        self.mpl_connect('button_release_event', self.on_release)
        self.mpl_connect('motion_notify_event', self.on_motion)

    # ----------------------------------------------------------------------
    def on_press(self, event):
        """"""
        self.dragging = True

        markers = [l.get_marker() for l in self.ax.axes.lines]
        if not 'o' in markers:
            return
        line = self.ax.axes.lines[0]

        distance = 1e99
        mk = None
        b = None

        pos = _find_topomap_coords(
            self.info_, picks=self.channels_labels_, sphere=0.1
        )

        for i, (x, y) in enumerate(pos):
            # for i, (x, y) in enumerate(zip(*line.get_data())):

            d = euclidean((event.xdata, event.ydata), (x, y))
            if distance > d:
                distance = d
                mk = i
                b = [x], [y]

        self.figure.axes[0].plot(
            *b, 'o', color='w', alpha=0.7, markersize=self.markersize
        )[0]

        self.target_start = mk

    # ----------------------------------------------------------------------
    def on_release(self, event):
        """"""
        self.dragging = False
        try:
            print(f'CH{self.target_start} -> {self.target_end}')
            self.set_channel(self.target_start, self.target_end)
        except:
            pass

        del self.marker_placeholder
        del self.text_placeholder

    # ----------------------------------------------------------------------
    def on_motion(self, event):
        """"""
        if not self.dragging:
            return

        if event.xdata == None and event.ydata == None:
            return

        distance = 1e99
        mk = None
        b = None
        t = None

        pos = _find_topomap_coords(
            self.info_, picks=self.channels_names_, sphere=0.1
        )

        for i, (x, y) in enumerate(pos):
            xe, ye = event.xdata, event.ydata
            d = euclidean((xe, ye), (x, y))

            if distance > d:
                distance = d
                mk = i
                b = [x], [y]
                t = [x, y]

        if not hasattr(self, 'marker_placeholder'):
            self.marker_placeholder = self.figure.axes[0].plot(
                *b, 'o', color='k', alpha=0.5, markersize=self.markersize
            )[0]

            self.text_placeholder = self.figure.axes[0].text(
                *b,
                self.channels_names_[mk],
                color='w',
                fontsize=self.font_size,
                va='center',
                ha='center',
                fontdict={},
            )

        self.marker_placeholder.set_data(*b)
        self.text_placeholder.set_position(t)
        self.text_placeholder.set_text(self.channels_names_[mk])

        self.draw()

        if mk != None:
            self.target_end = self.channels_names_[mk]


########################################################################
class TopoplotMontage(TopoplotBase, DragAndDropMontage):
    """Topoplot with electrodes positions."""

    # ----------------------------------------------------------------------
    def __init__(self):
        """"""
        TopoplotBase.__init__(self)
        DragAndDropMontage.__init__(self)

        self.ax = self.figure.add_subplot(111)
        self.reset_plot()
        self.dragging = False

        # self.mpl_connect('button_press_event', self.on_press)
        # self.mpl_connect('button_release_event', self.on_release)
        # self.mpl_connect('motion_notify_event', self.on_motion)

    # ----------------------------------------------------------------------
    def reset_plot(self) -> None:
        """Ajust figure positions."""
        self.figure.subplots_adjust(
            left=0.03, bottom=0.08, right=0.97, top=0.97, wspace=0, hspace=0
        )

    # ----------------------------------------------------------------------
    def update_montage(
        self,
        montage: mne.channels.DigMontage,
        electrodes: List[str],
        montage_name: str = None,
    ) -> None:
        """Redraw electrodes positions."""

        self.args_update = (montage, electrodes, montage_name)
        self.montage_ = montage

        # ----------------------------------------------------------------------
        def map_(x, in_min, in_max, out_min, out_max):
            return (x - in_min) * (out_max - out_min) / (
                in_max - in_min
            ) + out_min

        matplotlib.rcParams['text.color'] = "#ffffff"
        if hasattr(self, 'lastEvent'):
            factor = map_(len(electrodes), 1, 32, 1.2, 0.6)
            self.font_size = int(min(self.lastEvent) / 25) * factor
            self.markersize = int(min(self.lastEvent) / 10) * factor
        else:
            self.font_size = 13
            self.markersize = 35
        matplotlib.rcParams['font.size'] = self.font_size

        self.ax.clear()
        self.channels_names = montage.ch_names.copy()

        info = mne.create_info(
            self.channels_names, sfreq=1000, ch_types="eeg"
        )
        info.set_montage(montage)

        self.channels_names_ = self.channels_names.copy()
        if montage_name in ['standard_1020', 'standard_1005']:
            for ch in ['T3', 'T5', 'T4', 'T6']:
                self.channels_names.pop(self.channels_names.index(ch))

        info = mne.create_info(
            self.channels_names, sfreq=1000, ch_types="eeg"
        )
        info.set_montage(montage)

        self.info_ = info.copy()

        channels_mask = np.array(
            [ch in electrodes for ch in self.channels_names]
        )
        values = [0] * len(channels_mask)

        channels_labels = []
        self.channels_labels_ = electrodes.copy()
        for ch in self.channels_names:
            if ch in electrodes:
                i = electrodes.index(ch)
                channels_labels.append(
                    f'$\\mathsf{{{ch}}}$\n$\\mathsf{{ch{i+1}}}$'
                )
            else:
                channels_labels.append(f'$\\mathsf{{{ch}}}$')

        # colors = ['#3d7a84', '#3d7a84']
        colors = [
            os.environ.get('QTMATERIAL_PRIMARYCOLOR', '#ffffff'),
            os.environ.get('QTMATERIAL_PRIMARYCOLOR', '#ffffff'),
        ]
        cm = LinearSegmentedColormap.from_list('plane', colors, N=2)

        # pos = np.stack([k['r'] for k in self.info_['dig'][3:]])
        # radius = np.abs(pos[[2, 3], 0]).mean()

        # x = pos[0, 0]
        # y = pos[-1, 1]
        # z = pos[:, -1].mean()
        # [x, y, z, radius]

        mne.viz.plot_topomap(
            values,
            info,
            vmin=-1,
            vmax=1,
            contours=0,
            cmap=cm,
            outlines='skirt',
            names=channels_labels,
            show_names=True,
            axes=self.ax,
            sensors=True,
            show=False,
            mask_params=dict(
                marker='o',
                markerfacecolor='#263238',
                markeredgecolor='#4f5b62',
                linewidth=0,
                markersize=self.markersize,
            ),
            mask=channels_mask,
            # sphere=[0, 0, 0, 0.1],
        )

        self.draw()


########################################################################
class TopoplotImpedances(TopoplotBase):
    """Topoplot with electrodes impedances."""

    # ----------------------------------------------------------------------
    def __init__(self):
        """"""
        super().__init__()
        self.ax = self.figure.add_subplot(111)
        self.cax = self.figure.add_axes([0.1, 0.1, 0.8, 0.05])
        self.cmap = matplotlib.cm.get_cmap('YlGn')
        self.cmap = self.truncate_colormap(self.cmap, minval=0, maxal=0.66)

        self.band_2737 = filters.GenericButterBand(27, 37, fs=250)
        self.reset_plot()

    # ----------------------------------------------------------------------
    def raw_to_z(self, v: VOLTS) -> IMPEDANCE:
        """Convert voltage to impedance."""
        v = filters.notch60(v, fs=250)
        v = self.band_2737(v, fs=250)

        rms = np.std(v)
        z = (1e-6 * rms * np.sqrt(2) / 6e-9) - 2200
        if z < 0:
            return 0
        return z

    # ----------------------------------------------------------------------
    def reset_plot(self) -> None:
        """Ajust figure positions."""
        self.figure.subplots_adjust(
            left=0.03, bottom=0.08, right=0.97, top=0.97, wspace=0, hspace=0
        )
        self.add_colorbar()

    # ----------------------------------------------------------------------
    def truncate_colormap(self, cmap, minval=0, maxal=1, n=100):
        """"""
        new_cmap = LinearSegmentedColormap.from_list(
            f'trunc({cmap.name}, {minval:.2f}, {maxal:.2f})',
            cmap(np.linspace(minval, maxal, n)),
        )
        return new_cmap

    # ----------------------------------------------------------------------
    def update_impedances(
        self,
        montage: mne.channels.DigMontage,
        electrodes: List[str],
        impedances: Dict[str, float],
        montage_name: str = None,
    ) -> None:
        """Redraw electrodes with background colors."""

        self.args_update = (montage, electrodes, impedances, montage_name)

        # ----------------------------------------------------------------------
        def map_(x, in_min, in_max, out_min, out_max):
            return (x - in_min) * (out_max - out_min) / (
                in_max - in_min
            ) + out_min

        matplotlib.rcParams['text.color'] = "#000000"
        if hasattr(self, 'lastEvent'):
            factor = map_(len(electrodes), 1, 32, 1.2, 0.6)

            matplotlib.rcParams['font.size'] = (
                int(min(self.lastEvent) / 25) * factor
            )
            markersize = int(min(self.lastEvent) / 10) * factor
        else:
            matplotlib.rcParams['font.size'] = 13
            markersize = 35

        channels_names = montage.ch_names.copy()
        info = mne.create_info(montage.ch_names, sfreq=1000, ch_types="eeg")
        info.set_montage(montage)

        # channels_names = self.remove_overlaping(info, channels_names)
        if montage_name in ['standard_1020', 'standard_1005', None]:
            for ch in ['T3', 'T5', 'T4', 'T6']:
                try:
                    channels_names.pop(channels_names.index(ch))
                except:
                    pass

        info = mne.create_info(channels_names, sfreq=1000, ch_types="eeg")
        info.set_montage(montage)

        channels_mask = np.array([ch in electrodes for ch in channels_names])
        values = [0] * len(channels_mask)

        channels_labels = []
        for ch in channels_names:
            if ch in electrodes:

                if impedances[ch] == '??':
                    label = f'??\,\Omega'

                elif impedances[ch] < 1000:

                    z1 = int(impedances[ch])
                    z2 = int(np.ceil((impedances[ch] % 1) * 10))
                    label = f'{z1}k{z2}\,\Omega'
                else:
                    label = f'\infty \,\Omega'

                i = electrodes.index(ch)
                channels_labels.append(
                    f'$\\mathsf{{{ch}|ch{i+1}}}$\n$\\mathsf{{{label}}}$'
                )
            else:
                channels_labels.append(f'$\\mathsf{{{ch}}}$')

        colors = [
            os.environ.get('QTMATERIAL_PRIMARYCOLOR', '#ffffff'),
            os.environ.get('QTMATERIAL_PRIMARYCOLOR', '#ffffff'),
        ]
        cmap_ = LinearSegmentedColormap.from_list('plane', colors, N=2)

        self.ax.clear()
        mne.viz.plot_topomap(
            values,
            info,
            vmin=-1,
            vmax=1,
            contours=0,
            cmap=cmap_,
            outlines='skirt',
            axes=self.ax,
            names=channels_labels,
            show_names=True,
            sensors=True,
            show=False,
            mask_params={'marker': ''},
            mask=channels_mask,
        )
        q = self.cmap

        markers = [l.get_marker() for l in self.ax.axes.lines]
        if not '' in markers:
            return
        line = self.ax.axes.lines[markers.index('')]

        channels = np.array(channels_names)[channels_mask]
        for i, (x, y) in enumerate(zip(*line.get_data())):
            try:
                if impedances[channels[i]] == '??':
                    color = '#da4453'
                elif impedances[channels[i]] >= 15:
                    color = '#da4453'
                elif impedances[channels[i]] <= 0.1:
                    color = '#da4453'
                else:
                    color = q(impedances[channels[i]] / 20)
                self.ax.plot(
                    [x],
                    [y],
                    marker='o',
                    markerfacecolor=color,
                    markeredgecolor=color,
                    markersize=markersize,
                    linewidth=0,
                )
            except IndexError:
                return
        self.draw()

    # ----------------------------------------------------------------------
    def add_colorbar(self) -> None:
        """Draw color bar to indicate the impedance value."""
        # self.cax = self.figure.add_axes([0.1, 0.1, 0.8, 0.05])
        norm = matplotlib.colors.Normalize(vmin=0, vmax=15)

        sm = cm.ScalarMappable(cmap=self.cmap, norm=norm)
        cbr = pyplot.colorbar(sm, cax=self.cax, orientation="horizontal")
        pyplot.setp(
            pyplot.getp(cbr.ax.axes, 'xticklabels'),
            color=os.environ.get('QTMATERIAL_SECONDARYTEXTCOLOR', '#000000'),
            size=10,
        )
        ticks = [0, 5, 10, 15]
        cbr.set_ticks(ticks)
        cbr.set_ticklabels([f'{i} k$\Omega$' for i in ticks])

    # ----------------------------------------------------------------------
    def remove_overlaping(self, info, channels_names) -> None:
        """Remove channels that overlap positions."""
        locs3d = [ch['loc'][:3] for ch in info['chs']]
        dist = pdist(locs3d)
        problematic_electrodes = []
        if len(locs3d) > 1 and np.min(dist) < 1e-10:
            problematic_electrodes = [
                info['chs'][elec_i]
                for elec_i in squareform(dist < 1e-10)
                .any(axis=0)
                .nonzero()[0]
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

                        channels_names.pop(
                            channels_names.index(ch_i['ch_name'])
                        )

        return channels_names


########################################################################
class Montage:
    """Widget that handle the montage, electrodes channels, and impedances."""

    # ----------------------------------------------------------------------
    def __init__(self, core):
        """"""
        self.parent_frame = core.main
        self.core = core

        if color := os.getenv('QTMATERIAL_SECONDARYDARKCOLOR', False):
            pyplot.rcParams['axes.facecolor'] = color
            pyplot.rcParams['figure.facecolor'] = color
            pyplot.rcParams['savefig.facecolor'] = color

        self.channels_names_widgets = []
        self.channels_bipolar_widgets = []

        self.topoplot = TopoplotMontage()
        self.topoplot.set_channel = self.set_channel
        self.parent_frame.gridLayout_montage.addWidget(self.topoplot)

        self.parent_frame.comboBox_montages.addItems(
            mne.channels.get_builtin_montages()
        )

        # self.parent_frame.comboBox_montage_channels.addItems(
        # [f"{i+1} channel{'s'[:i]}" for i in range(128)])

        self.set_saved_montages()
        self.update_environ()
        self.connect()

        self.topoplot_impedance = TopoplotImpedances()
        self.parent_frame.gridLayout_impedances.addWidget(
            self.topoplot_impedance
        )
        # self.update_impedance()

        self.load_montage()

        QTimer().singleShot(10, self.set_spliter_position)

    # ----------------------------------------------------------------------
    def update_impedance(self, z: Optional[List[float]] = None) -> None:
        """Send the impedance values to the drawer."""
        electrodes = list(prop.CHANNELS.values())
        montage = self.get_mne_montage()

        if z is None:
            z = ['??'] * len(electrodes)

        impedances = {ch: z for ch, z in zip(electrodes, z)}
        self.topoplot_impedance.update_impedances(
            montage, electrodes, impedances
        )

    # ----------------------------------------------------------------------
    def set_spliter_position(self) -> None:
        """Delay method to redraw the figure."""
        self.parent_frame.splitter_montage.moveSplitter(
            self.parent_frame.splitter_montage.getRange(1)[1] // 2, 1
        )

    # ----------------------------------------------------------------------
    def connect(self) -> None:
        """Connect events."""
        self.parent_frame.comboBox_montages.activated.connect(
            self.update_topoplot
        )

        self.parent_frame.spinBox_montage_channels.valueChanged.connect(
            self.update_topoplot
        )
        # self.parent_frame.spinBox_montage_channels.activated.connect(
        # self.update_topoplot)

        self.parent_frame.pushButton_save_montage.clicked.connect(
            self.save_montage
        )
        self.parent_frame.pushButton_remove_montage.clicked.connect(
            self.delete_montage
        )

        self.parent_frame.tableWidget_montages.itemClicked.connect(
            self.load_montage
        )

        self.parent_frame.checkBox_view_impedances.clicked.connect(
            self.change_plot
        )

        self.parent_frame.radioButton_noneeg.clicked.connect(
            self.set_channels_mode
        )
        self.parent_frame.spinBox_montage_channels_noneeg.valueChanged.connect(
            self.set_non_eeg_montage
        )

        self.parent_frame.tableWidget_noneeg.itemChanged.connect(
            self.update_noneeg_channels_montage
        )

    # ----------------------------------------------------------------------
    def set_channels_mode(self, non_eeg):
        """"""
        if non_eeg:
            self.parent_frame.stackedWidget_noneeg.setCurrentIndex(1)
            self.set_non_eeg_montage()
        else:
            self.parent_frame.stackedWidget_noneeg.setCurrentIndex(0)

    # ----------------------------------------------------------------------
    def set_non_eeg_montage(self):
        """"""
        rows = self.parent_frame.spinBox_montage_channels_noneeg.value()
        # self.parent_frame.tableWidget_noneeg.clear()
        self.parent_frame.tableWidget_noneeg.setRowCount(rows)

        header = self.parent_frame.tableWidget_noneeg.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)

        self.noneeg_channels = []
        self.noneeg_channels_type = []

        for r in range(rows):
            item = QTableWidgetItem('Bipolar')
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item.setCheckState(Qt.Unchecked)
            self.parent_frame.tableWidget_noneeg.setItem(r, 1, item)
            self.noneeg_channels_type.append(item)

            item = QTableWidgetItem('Hola')
            self.parent_frame.tableWidget_noneeg.setItem(r, 0, item)
            self.noneeg_channels.append(item)

            item = QTableWidgetItem(f'channel {r+1}  ')
            self.parent_frame.tableWidget_noneeg.setVerticalHeaderItem(
                r, item
            )

    # ----------------------------------------------------------------------
    def update_noneeg_channels_montage(self):
        """"""
        rows = self.parent_frame.spinBox_montage_channels_noneeg.value()
        if len(self.noneeg_channels) != rows:
            return

        montage = {
            i + 1: item.text() for i, item in enumerate(self.noneeg_channels)
        }
        types = [
            int(i.checkState() == Qt.CheckState.Unchecked)
            for i in self.noneeg_channels_type
        ]

        os.environ['BCISTREAM_CHANNELS'] = json.dumps(montage)
        os.environ['BCISTREAM_MONTAGE_TYPE'] = json.dumps(types)
        os.environ['BCISTREAM_MONTAGE_NAME'] = json.dumps('NON-EEG')

    # ----------------------------------------------------------------------
    def change_plot(self) -> None:
        """Switch between Montage and Impedance."""
        if (
            self.parent_frame.checkBox_view_impedances.isChecked()
        ):  # impedances
            self.parent_frame.stackedWidget_montage.setCurrentIndex(1)
        else:  # montage
            self.parent_frame.stackedWidget_montage.setCurrentIndex(0)

        self.start_impedance_measurement()

    # ----------------------------------------------------------------------
    def get_mne_montage(self) -> mne.channels.DigMontage:
        """Create montage from GUI options."""
        montage_name = self.parent_frame.comboBox_montages.currentText()
        montage = mne.channels.make_standard_montage(montage_name)
        return montage

    # ----------------------------------------------------------------------
    def update_topoplot(self) -> None:
        """Redraw topoplot."""
        montage = self.get_mne_montage()
        montage_name = self.parent_frame.comboBox_montages.currentText()
        self.generate_list_channels()
        electrodes = [ch.currentText() for ch in self.channels_names_widgets]
        self.topoplot.update_montage(
            montage, electrodes, montage_name=montage_name
        )
        self.validate_channels()
        self.update_environ()
        self.topoplot_impedance.reset_plot()
        self.update_impedance()

    # ----------------------------------------------------------------------
    def generate_list_channels(self) -> None:
        """Update the widgets to set the channel to the electrode."""
        for layout in [
            self.parent_frame.gridLayout_list_channels_right,
            self.parent_frame.gridLayout_list_channels_left,
        ]:

            for i in reversed(range(layout.count())):
                if item := layout.takeAt(i):
                    item.widget().deleteLater()
            # layout.setColumnStretch(1, 1)

            layout.setColumnStretch(0, 0)
            layout.setColumnStretch(1, 1)
            layout.setColumnStretch(2, 1)

        if self.channels_names_widgets:
            previous_labels = [
                ch.currentText() for ch in self.channels_names_widgets
            ]
        else:
            previous_labels = []

        self.channels_names_widgets = []
        self.channels_bipolar_widgets = []
        self.labels_names_widgets = []
        montage = self.get_mne_montage()
        for i in range(self.parent_frame.spinBox_montage_channels.value()):

            j = i
            if i % 2:
                layout = self.parent_frame.gridLayout_list_channels_right
                j = j - 1
            else:
                layout = self.parent_frame.gridLayout_list_channels_left

            channel_label = QLabel(f'CH{i+1}')
            self.labels_names_widgets.append(channel_label)
            layout.addWidget(channel_label, j, 0)

            channel_name = QComboBox()
            channel_name.addItems(['Off'] + montage.ch_names)

            if (
                len(previous_labels) > i
                and previous_labels[i] in montage.ch_names
            ):
                index = montage.ch_names.index(previous_labels[i])
            elif len(previous_labels) > i and previous_labels[i] == 'Off':
                index = -1
            else:
                index = i
            channel_name.setCurrentIndex(index + 1)
            channel_name.activated.connect(self.update_topoplot)
            self.channels_names_widgets.append(channel_name)

            layout.addWidget(channel_name, j, 1)

            channel_bipolar = QCheckBox('Bipolar')
            # channel_bipolar = QComboBox()
            # channel_bipolar.addItems(['Monopolar', 'Bipolar'])
            self.channels_bipolar_widgets.append(channel_bipolar)

            layout.addWidget(channel_bipolar, j, 2)

    # ----------------------------------------------------------------------
    def set_channel(self, channel, name):
        """"""
        self.channels_names_widgets[channel].setCurrentText(name)
        self.update_topoplot()

    # ----------------------------------------------------------------------
    def save_montage(self) -> None:
        """Save current montage."""
        montage_name = self.parent_frame.comboBox_montages.currentText()
        channels_names = ','.join(
            [ch.currentText() for ch in self.channels_names_widgets]
        )
        # channels_bipolar = ','.join([str(int(ch.currentText() == 'Monopolar'))
        # for ch in self.channels_bipolar_widgets])

        channels_bipolar = ','.join(
            [str(int(w.isChecked())) for w in self.channels_bipolar_widgets]
        )

        channels_bipolar = [
            int(w.isChecked()) for w in self.channels_bipolar_widgets
        ]

        # saved_montages = self.config['montages']
        for i in range(1, 999):
            if self.core.config.has_option('montages', f'montage{i}'):
                if (
                    self.core.config.get('montages', f'montage{i}')
                    == f"{montage_name}|{channels_names}"
                ):
                    return  # Duplicated montage
            else:
                self.core.config.set(
                    'montages',
                    f'montage{i}',
                    f"{montage_name}|{channels_names}",
                )
                self.core.config.set(
                    'montages', f'type{i}', f"{channels_bipolar}"
                )
                # self.parent.comboBox_historical_montages.addItem(name)
                self.core.config.save()
                self.set_saved_montages()
                return

    # ----------------------------------------------------------------------
    def delete_montage(self, *args, **kwargs) -> None:
        """Remove montage."""
        row = self.parent_frame.tableWidget_montages.currentRow()
        config_name = self.parent_frame.tableWidget_montages.item(
            row, 0
        ).config_name
        self.core.config.remove_option('montages', config_name)
        self.core.config.save()
        self.set_saved_montages()

    # ----------------------------------------------------------------------
    def set_saved_montages(self) -> None:
        """Load saved montages."""
        self.parent_frame.tableWidget_montages.clear()
        self.parent_frame.tableWidget_montages.setRowCount(0)
        self.parent_frame.tableWidget_montages.setColumnCount(3)
        self.parent_frame.tableWidget_montages.verticalHeader().setVisible(
            True
        )
        self.parent_frame.tableWidget_montages.setHorizontalHeaderLabels(
            ['Montage', 'Channels', 'Electrodes']
        )
        saved_montages = self.core.config['montages']

        montages = filter(
            lambda m: m.startswith('montage'), saved_montages.keys()
        )
        for i, saved in enumerate(montages):
            montage, electrodes = saved_montages.get(saved).split('|')
            self.parent_frame.tableWidget_montages.insertRow(i)

            item = QTableWidgetItem(montage)
            item.config_name = saved

            itemh = QTableWidgetItem(montage)
            itemh.setText(f'#{i+1}')
            self.parent_frame.tableWidget_montages.setVerticalHeaderItem(
                i, itemh
            )

            self.parent_frame.tableWidget_montages.setItem(i, 0, item)
            self.parent_frame.tableWidget_montages.setItem(
                i,
                1,
                QTableWidgetItem(
                    f"{len(electrodes.split(','))-electrodes.split(',').count('Off')} ch"
                ),
            )
            self.parent_frame.tableWidget_montages.setItem(
                i, 2, QTableWidgetItem(' '.join(electrodes.split(',')))
            )

            i += 1

    # ----------------------------------------------------------------------
    def load_montage(self, event=None) -> None:
        """Load the selected montage."""
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        if event is None:
            montage_name, channels = self.core.config.get(
                'montages', 'last_montage'
            ).split('|')
            channels = channels.split(',')

            # montage_name, channels = self.core.config.get(
            # 'montages', 'last_montage').split('|')
            # channels = channels.split(',')

        else:
            montage_name = self.parent_frame.tableWidget_montages.item(
                event.row(), 0
            ).text()
            channels = self.parent_frame.tableWidget_montages.item(
                event.row(), 2
            ).text()
            channels = channels.split(' ')
            self.core.config.set(
                'montages',
                'last_montage',
                f"{montage_name}|{','.join(channels)}",
            )
            # channels = channels.split(' ')
            # self.core.config.set('montages', 'last_type',
            # f"{','.join(channels)}")
            self.core.config.save()

        self.parent_frame.comboBox_montages.setCurrentText(montage_name)
        self.parent_frame.spinBox_montage_channels.setValue(len(channels))

        self.generate_list_channels()
        [
            wg.setCurrentText(ch)
            for wg, ch in zip(self.channels_names_widgets, channels)
        ]

        self.update_topoplot()
        QApplication.restoreOverrideCursor()

    # ----------------------------------------------------------------------
    def validate_channels(self) -> None:
        """Highlight misconfigurations."""
        channels = [ch.currentText() for ch in self.channels_names_widgets]
        for channel, label in zip(channels, self.labels_names_widgets):
            if channels.count(channel) > 1:
                label.setStyleSheet(
                    "QLabel{color: #ff1744;}QLabel:disabled{color: rgba(255, 23, 68, 0.2)};"
                )
            else:
                label.setStyleSheet(
                    f"QLabel{{color: {os.environ.get('QTMATERIAL_SECONDARYTEXTCOLOR', '')};}}"
                    f"QLabel:disabled{{color: rgba(255, 255, 255, 0.2) }}"
                )

    # ----------------------------------------------------------------------
    def update_environ(self) -> None:
        """Update environment variables."""
        montage = {
            i + 1: ch.currentText()
            for i, ch in enumerate((self.channels_names_widgets))
            if ch.currentText() != 'Off'
        }

        # types = [int(w.currentText() == 'Monopolar')
        # for w in self.channels_bipolar_widgets]
        types = [
            int(not w.isChecked()) for w in self.channels_bipolar_widgets
        ]

        os.environ['BCISTREAM_CHANNELS'] = json.dumps(montage)
        os.environ['BCISTREAM_MONTAGE_TYPE'] = json.dumps(types)
        os.environ['BCISTREAM_MONTAGE_NAME'] = json.dumps(
            self.parent_frame.comboBox_montages.currentText()
        )
        # os.environ['BCISTREAM_DAISY'] = json.dumps(
        # bool(list(filter(lambda x: x > 8, montage.keys()))))

    # ----------------------------------------------------------------------
    @thread_this
    def start_impedance_measurement(self) -> None:
        """Change OpenBCI configurations to read impedance."""
        if self.parent_frame.checkBox_view_impedances.isChecked():

            if not hasattr(self.core.connection, 'openbci'):
                self.core.connection.openbci_connect()

            openbci = self.core.connection.openbci.openbci

            response = openbci.command(openbci.SAMPLE_RATE_250SPS)
            logging.warning(response)

            response = openbci.command(openbci.DEFAULT_CHANNELS_SETTINGS)
            logging.warning(response)

            openbci.leadoff_impedance(
                prop.CHANNELS,
                pchan=openbci.TEST_SIGNAL_NOT_APPLIED,
                nchan=openbci.TEST_SIGNAL_APPLIED,
            )

            self.measuring_impedance = True
            V = []
            with OpenBCIConsumer(host=prop.HOST, topics=['eeg']) as stream:

                n = 1000 // prop.STREAMING_PACKAGE_SIZE
                frame = 0
                for data in stream:
                    frame += 1
                    if data.topic == 'eeg':

                        v = data.value['data']
                        V.append(v)

                        if len(V) > 10:
                            V.pop(0)

                        if frame % n == 0:
                            z = np.array(
                                [
                                    self.topoplot_impedance.raw_to_z(v)
                                    for v in np.concatenate(V, axis=1)
                                ]
                            )
                            self.update_impedance(z / 1000)

                        if not self.measuring_impedance:
                            self.core.connection.openbci.session_settings()
                            break

        else:
            self.measuring_impedance = False


########################################################################
class NonEEGMontage:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
