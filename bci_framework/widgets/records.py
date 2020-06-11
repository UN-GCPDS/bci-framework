from PySide2.QtWidgets import QTableWidgetItem, QAction, QMenu
from PySide2.QtCore import Qt, QTimer
from openbci_stream.handlers import HDF5_Reader

from PySide2.QtGui import QIcon

import os
from datetime import datetime, timedelta
import numpy as np


########################################################################
class Records:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, parent, core):
        """Constructor"""

        self.parent = parent
        self.core = core

        self.current_signal = None

        self.load_records()
        self.connect()

        self.parent.widget_record.hide()

    # ----------------------------------------------------------------------
    def connect(self):
        """"""
        self.parent.tableWidget_records.itemDoubleClicked.connect(self.load_file)
        # self.parent.tableWidget_records.itemClicked.connect(lambda: None)
        self.parent.horizontalSlider_record.valueChanged.connect(self.update_record_time)
        self.parent.pushButton_play_signal.clicked.connect(self.play_signal)
        # self.parent.horizontalSlider_record.valueChanged.connect(self.update_record_time)

        # self.parent.tableWidget_records.customContextMenuRequested.connect(self.table_contextMenuEvent)

    # # ----------------------------------------------------------------------
    # def table_contextMenuEvent(self, event):
        # """"""
        # menu = QMenu(self.parent.tableWidget_records)
        # menu.addAction(QAction(QIcon.fromTheme('media-playback-start'), "Load record", self.parent.tableWidget_records, triggered=self.load_file))
        # menu.exec_(event.globalPos())

    # ----------------------------------------------------------------------
    def load_records(self):
        """"""
        row = self.parent.tableWidget_records.rowCount()
        records = os.listdir('records')
        for i, filename in enumerate(records):
            self.parent.tableWidget_records.insertRow(row + i)

            for j, value in enumerate(self.get_metadata(filename)[:3]):

                item = QTableWidgetItem(value)

                if j != (self.parent.tableWidget_records.columnCount() - 1):
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)

                self.parent.tableWidget_records.setItem(row + i, j, item)

    # ----------------------------------------------------------------------
    def get_metadata(self, filename):
        """"""
        file = HDF5_Reader(os.path.join('records', filename))

        header = file.header
        samples, channels = file.eeg.shape
        dtm = datetime.fromtimestamp(header['datetime']).strftime("%x %X")
        sample_rate = header['sample_rate']

        duration = str(timedelta(seconds=samples / sample_rate))

        return [duration, dtm, filename.replace('.h5', ''), header['montage']]

    # ----------------------------------------------------------------------
    def load_file(self, item):
        """"""
        self.current_signal = item.row()
        name = self.parent.tableWidget_records.item(item.row(), 2).text()

        duration, datetime, _, montage = self.get_metadata(f"{name}.h5")

        _, mtg, electrodes = montage.split('|')

        electrodes = electrodes.replace(' ', '').split(',')
        electrodes = '\n'.join([', '.join(electrodes[n:n + 8]) for n in range(0, len(electrodes), 8)])

        self.parent.label_record_name.setText(name)
        self.parent.label_record_primary.setText(f" [{duration}]")
        self.parent.label_record_datetime.setText(datetime)
        self.parent.label_record_channels.setText(electrodes)
        self.parent.label_record_montage.setText(mtg)

        self.parent.label_record_name.setStyleSheet("*{font-family: 'mono'}")
        self.parent.label_record_primary.setStyleSheet("*{font-family: 'mono'}")
        self.parent.label_record_datetime.setStyleSheet("*{font-family: 'mono'}")
        self.parent.label_record_channels.setStyleSheet("*{font-family: 'mono'}")
        self.parent.label_record_montage.setStyleSheet("*{font-family: 'mono'}")

        self.parent.horizontalSlider_record.setValue(0)
        self.parent.widget_record.show()
        self.core.show_interface('Visualizations')
        # self.parent.tableWidget_records.setSelectionMode(QAbstractItemView.SelectRows)
        # self.parent.tableWidget_records.selectRow(item.row())
        # self.parent.tableWidget_records.setSelectionMode(QAbstractItemView.NoSelection)

    # ----------------------------------------------------------------------
    def get_offset(self):
        """"""
        h, m, s = self.parent.label_record_primary.text()[2:-1].split(':')
        seconds = int(h) * 60 * 60 + int(m) * 60 + int(s)
        value = self.parent.horizontalSlider_record.value() / self.parent.horizontalSlider_record.maximum()
        return int(seconds * value)

    # ----------------------------------------------------------------------
    def update_record_time(self):
        """"""
        offset = timedelta(seconds=self.get_offset())
        self.start_play = datetime.now()

        self.parent.label_time_current.setStyleSheet("*{font-family: 'mono'}")
        self.parent.label_time_current.setText(str(offset))

    # ----------------------------------------------------------------------
    def play_signal(self, toggled):
        """"""
        self.parent.tableWidget_records.selectRow(self.current_signal)

        if toggled:
            # h, m, s = self.parent.label_time_current.text().split(':')
            self.start_play = datetime.now()  # - timedelta(hours=int(h), minutes=int(m), seconds=int(s))
            self.timer = QTimer()
            self.timer.setInterval(1000 / 1)
            self.timer.timeout.connect(self.update_timer)
            self.timer.start()
            self.parent.pushButton_play_signal.setIcon(QIcon.fromTheme('media-playback-pause'))
        else:

            self.timer.stop()
            self.parent.pushButton_play_signal.setIcon(QIcon.fromTheme('media-playback-start'))

    # ----------------------------------------------------------------------
    def update_timer(self):
        """"""
        now = datetime.now()
        delta = now - self.start_play + timedelta(seconds=self.get_offset())
        self.parent.label_time_current.setText(str(timedelta(seconds=int(delta.total_seconds()))))

        h, m, s = self.parent.label_record_primary.text()[2:-1].split(':')
        seconds = int(h) * 60 * 60 + int(m) * 60 + int(s)

        value = self.parent.horizontalSlider_record.maximum() // ((seconds / delta.total_seconds()))
        self.parent.horizontalSlider_record.setValue(int(value))

