from PySide2.QtWidgets import QTableWidgetItem, QAction, QMenu
from PySide2.QtCore import Qt, QTimer
from openbci_stream.handlers import HDF5_Reader

from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

from PySide2.QtGui import QIcon

import os
from datetime import datetime, timedelta
# import numpy as np

import pickle

from datetime import datetime
# import time
import sys
import os
import shutil
import time

from ..subprocess_script import run_subprocess
from ..dialogs import Dialogs
from .. import doc_urls


########################################################################
class Records:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, parent, core):
        """Constructor"""

        self.parent_frame = parent
        self.core = core
        self.current_signal = None

        self.records_dir = os.path.join(
            os.getenv('BCISTREAM_HOME'), 'records')
        os.makedirs(self.records_dir, exist_ok=True)

        self.load_records()
        self.connect()

        self.parent_frame.label_records_path.setText(self.records_dir)
        self.parent_frame.label_records_path.setStyleSheet(
            '*{font-family: "DejaVu Sans Mono";}')

        self.parent_frame.widget_record.hide()

    # ----------------------------------------------------------------------
    def connect(self):
        """"""
        self.parent_frame.tableWidget_records.itemDoubleClicked.connect(
            self.load_file)
        self.parent_frame.horizontalSlider_record.valueChanged.connect(
            self.update_record_time)
        self.parent_frame.pushButton_play_signal.clicked.connect(
            self.play_signal)
        self.parent_frame.pushButton_record.toggled.connect(
            self.record_signal)

        self.parent_frame.tableWidget_records.itemChanged.connect(
            self.record_renamed)

        self.parent_frame.pushButton_remove_record.clicked.connect(
            self.remove_record)

        # self.parent.tableWidget_records.itemClicked.connect(lambda: None)
        # self.parent.horizontalSlider_record.valueChanged.connect(self.update_record_time)

        # self.parent.tableWidget_records.customContextMenuRequested.connect(self.table_contextMenuEvent)

    # # ----------------------------------------------------------------------
    # def table_contextMenuEvent(self, event):
        # """"""
        # menu = QMenu(self.parent.tableWidget_records)
        # menu.addAction(QAction(QIcon.fromTheme('media-playback-start'), "Load record", self.parent.tableWidget_records, triggered=self.load_file))
        # menu.exec_(event.globalPos())

    # ----------------------------------------------------------------------
    def remove_record(self):
        """"""
        filename = self.parent_frame.tableWidget_records.currentItem().previous_name

        response = Dialogs.question_message(self.parent_frame, 'Remove file?',
                                            f"""<p>This action cannot be undone.<br><br>
                                            <nobr>Remove permanently the file <code>{filename}.h5</code> from your system?</nobr></p>

                                            """)
        if response:
            os.remove(os.path.join(self.records_dir, f'{filename}.h5'))
            self.load_records()

    # ----------------------------------------------------------------------
    def record_renamed(self, item):
        """"""
        if not hasattr(item, 'previous_name'):
            return

        old_name = item.previous_name
        new_name = item.text()

        if old_name != new_name:
            shutil.move(os.path.join(self.records_dir, f'{old_name}.h5'),
                        os.path.join(self.records_dir, f'{new_name}.h5'))
            self.load_records()

    # ----------------------------------------------------------------------
    def load_records(self):
        """"""
        self.parent_frame.tableWidget_records.clear()

        self.parent_frame.tableWidget_records.setRowCount(0)
        self.parent_frame.tableWidget_records.setColumnCount(3)

        self.parent_frame.tableWidget_records.setHorizontalHeaderLabels(
            ['Duration', 'Datetime', 'Name'])

        # for i, text in enumerate():
        # self.parent.tableWidget_records.horizontalHeaderItem(
        # i).setText(text)

        # row = self.parent.tableWidget_records.rowCount()
        records = os.listdir(self.records_dir)
        for i, filename in enumerate(records):
            if not filename.endswith('h5'):
                continue

            self.parent_frame.tableWidget_records.insertRow(i)

            try:
                for j, value in enumerate(self.get_metadata(filename)[:3]):
                    item = QTableWidgetItem(value)
                    item.previous_name = value
                    if j != (self.parent_frame.tableWidget_records.columnCount() - 1):
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.parent_frame.tableWidget_records.setItem(i, j, item)
            except Exception as msg:
                self.parent_frame.tableWidget_records.removeRow(i)
                # print(msg)
                # item = QTableWidgetItem(f"[Corrupted file]")
                # self.parent.tableWidget_records.setItem(i, 0, item)
                # item = QTableWidgetItem(f"[Corrupted file]")
                # self.parent.tableWidget_records.setItem(i, 1, item)
                # item = QTableWidgetItem(f"{filename}")
                # self.parent.tableWidget_records.setItem(i, 2, item)
                pass

        self.parent_frame.tableWidget_records.sortByColumn(1)

        # for i, text in enumerate(['Duration', 'Datetime', 'Name']):
        # self.parent.tableWidget_records.horizontalHeaderItem(
        # i).setText(text)

    # ----------------------------------------------------------------------
    def get_metadata(self, filename):
        """"""
        file = HDF5_Reader(os.path.join(self.records_dir, filename))

        header = file.header
        channels, samples = file.eeg.shape
        dtm = datetime.fromtimestamp(header['datetime']).strftime("%x %X")
        sample_rate = header['sample_rate']

        duration = str(timedelta(seconds=int(samples / sample_rate)))
        file.close()

        return [duration, dtm, filename.replace('.h5', ''), header['montage'], header['channels']]

    # ----------------------------------------------------------------------
    def load_file(self, item):
        """"""
        self.current_signal = item.row()
        name = self.parent_frame.tableWidget_records.item(
            item.row(), 2).text()

        duration, datetime, _, montage, electrodes = self.get_metadata(
            f"{name}.h5")

        # _, mtg, electrodes = montage.split('|')

        electrodes = list(electrodes.values())
        electrodes = '\n'.join([', '.join(electrodes[n:n + 8])
                                for n in range(0, len(electrodes), 8)])

        self.parent_frame.label_record_name.setText(name)
        self.parent_frame.label_record_primary.setText(f" [{duration}]")
        self.parent_frame.label_record_datetime.setText(datetime)
        self.parent_frame.label_record_channels.setText(electrodes)
        self.parent_frame.label_record_montage.setText(montage)

        self.parent_frame.label_record_name.setStyleSheet(
            "*{font-family: 'mono'}")
        self.parent_frame.label_record_primary.setStyleSheet(
            "*{font-family: 'mono'}")
        self.parent_frame.label_record_datetime.setStyleSheet(
            "*{font-family: 'mono'}")
        self.parent_frame.label_record_channels.setStyleSheet(
            "*{font-family: 'mono'}")
        self.parent_frame.label_record_montage.setStyleSheet(
            "*{font-family: 'mono'}")

        self.parent_frame.horizontalSlider_record.setValue(0)
        self.parent_frame.widget_record.show()
        # self.core.show_interface('Visualizations')
        # self.parent.tableWidget_records.setSelectionMode(QAbstractItemView.SelectRows)
        # self.parent.tableWidget_records.selectRow(item.row())
        # self.parent.tableWidget_records.setSelectionMode(QAbstractItemView.NoSelection)

    # ----------------------------------------------------------------------
    def get_offset(self):
        """"""
        h, m, s = self.parent_frame.label_record_primary.text()[
            2:-1].split(':')
        seconds = int(h) * 60 * 60 + int(m) * 60 + int(s)
        value = self.parent_frame.horizontalSlider_record.value(
        ) / self.parent_frame.horizontalSlider_record.maximum()
        return seconds * value

    # ----------------------------------------------------------------------
    def update_record_time(self):
        """"""
        offset = timedelta(seconds=self.get_offset())
        self.start_play = datetime.now()

        self.parent_frame.label_time_current.setStyleSheet(
            "*{font-family: 'mono'}")
        self.parent_frame.label_time_current.setText(
            str(offset - timedelta(microseconds=offset.microseconds)))

    # ----------------------------------------------------------------------
    def play_signal(self, toggled):
        """"""
        self.parent_frame.tableWidget_records.selectRow(self.current_signal)

        if toggled:

            self.record_reader = HDF5_Reader(os.path.join(
                self.records_dir, f'{self.parent.label_record_name.text()}.h5'))

            try:
                self.producer_eeg = KafkaProducer(bootstrap_servers=['localhost:9092'],
                                                  compression_type='gzip',
                                                  value_serializer=pickle.dumps,
                                                  )
            except NoBrokersAvailable:

                Dialogs.critical_message(
                    self.parent_frame, 'Kafka: Error!',
                    f"""<p>Kafka: No Brokers Available!<br><br>

                    Please, refer to the documentation for a complete guide about how to
                    <a href='{doc_urls.CONFIGURE_KAFKA}'>configure Cafka</a>.
                    </p>"""
                )

                self.parent_frame.pushButton_play_signal.setChecked(False)
                return

            self.start_streaming = 0

            # self.record_reader

            self.start_play = datetime.now()
            self.timer = QTimer()
            self.timer.setInterval(1000 / 4)
            self.timer.timeout.connect(self.update_timer)
            self.timer.start()
            self.parent_frame.pushButton_play_signal.setIcon(
                QIcon.fromTheme('media-playback-pause'))

        else:

            self.timer.stop()
            self.parent_frame.pushButton_play_signal.setIcon(
                QIcon.fromTheme('media-playback-start'))

    # ----------------------------------------------------------------------
    def update_timer(self):
        """"""
        now = datetime.now()
        delta = now - self.start_play + timedelta(seconds=self.get_offset())

        h, m, s = self.parent_frame.label_record_primary.text()[
            2:-1].split(':')
        seconds = int(h) * 60 * 60 + int(m) * 60 + int(s)

        value = self.parent_frame.horizontalSlider_record.maximum() / \
            ((seconds / delta.total_seconds()))
        self.parent_frame.horizontalSlider_record.setValue(int(value))

        end_streaming = (self.record_reader.eeg.shape[1] * self.parent_frame.horizontalSlider_record.value(
        )) / self.parent_frame.horizontalSlider_record.maximum()

        if samples := end_streaming - self.start_streaming:
            if samples < 0:
                samples = (4 * self.record_reader.eeg.shape[1] / 1000)

            # print(samples, [max([end_streaming - samples, 0]), end_streaming])

            data_ = {'context': 'context',
                     'data': (self.record_reader.eeg[:, max([end_streaming - samples, 0]): end_streaming],
                              self.record_reader.aux[:, max([end_streaming - samples, 0]): end_streaming]),
                     'binary_created': datetime.now().timestamp(),
                     'created': datetime.now().timestamp(),
                     'samples': samples,
                     }

            self.producer_eeg.send('eeg', data_)
            self.start_streaming = end_streaming

    # ----------------------------------------------------------------------
    def update_timer_record(self):
        """"""
        now = datetime.now()
        delta = now - self.start_record

        n_time = datetime.strptime(str(delta), '%H:%M:%S.%f').time()

        self.parent_frame.pushButton_record.setText(
            f"Recording [{n_time.strftime('%H:%M:%S')}]")

    # ----------------------------------------------------------------------
    def record_signal(self, toggled):
        """"""
        if toggled:
            self.start_record = datetime.now()
            self.timer = QTimer()
            self.timer.setInterval(1000 / 1)
            self.timer.timeout.connect(self.update_timer_record)
            self.timer.start()
            # os.environ['BCI_RECORDING'] ------------------= 'False'
            self.subprocess_script = run_subprocess(
                [sys.executable, os.path.join('transformers', 'record.py')])

            # os.environ['BCI_RECORDING']

        else:
            self.timer.stop()
            self.parent_frame.pushButton_record.setText(f"Record")
            self.subprocess_script.terminate()
            # time.sleep(3)
            self.load_records()
