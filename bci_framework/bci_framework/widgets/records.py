import sys
import os
import shutil
from datetime import datetime, timedelta

from PySide2.QtWidgets import QTableWidgetItem, QMenu, QApplication, QAction
from PySide2.QtCore import Qt, QTimer
from PySide2.QtGui import QCursor, QIcon

from openbci_stream.utils import HDF5Reader
from ..subprocess_script import run_subprocess
from ..dialogs import Dialogs


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

        self.connect()

        self.parent_frame.label_records_path.setText(self.records_dir)
        self.parent_frame.label_records_path.setStyleSheet(
            '*{font-family: "DejaVu Sans Mono";}')

        self.parent_frame.widget_record.hide()

    # ----------------------------------------------------------------------
    def on_focus(self):
        """"""
        self.load_records()

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
        records = filter(lambda s: s.endswith(
            'h5'), os.listdir(self.records_dir))

        i = 0
        for filename in records:
            try:
                metadata = self.get_metadata(filename)[:3]
            except:
                continue

            self.parent_frame.tableWidget_records.insertRow(i)
            for j, value in enumerate(metadata):
                item = QTableWidgetItem(value)
                item.previous_name = value
                if j != (self.parent_frame.tableWidget_records.columnCount() - 1):
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.parent_frame.tableWidget_records.setItem(i, j, item)

        self.parent_frame.tableWidget_records.sortByColumn(1)

    # ----------------------------------------------------------------------
    def get_metadata(self, filename, light=True):
        """"""
        file = None
        for _ in range(10):
            try:
                file = HDF5Reader(os.path.join(self.records_dir, filename))
                break
            except:
                continue

        if file is None:
            return False

        montage = file.header['montage']
        channels = file.header['channels']
        filename = filename.replace('.h5', '')
        created = datetime.fromtimestamp(
            file.header['datetime']).strftime("%x %X")
        _, samples = file.header['shape']
        sample_rate = file.header['sample_rate']
        duration = str(timedelta(seconds=int(samples / sample_rate)))

        if not light:
            annotations = file.annotations
        else:
            annotations = []

        file.close()
        return [duration, created, filename, montage, channels, annotations]

    # ----------------------------------------------------------------------
    def load_file(self, item):
        """"""
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))

        self.current_signal = item.row()
        name = self.parent_frame.tableWidget_records.item(
            item.row(), 2).text()

        duration, datetime, _, montage, electrodes, annotations = self.get_metadata(
            f"{name}.h5", light=False)

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

        self.parent_frame.tableWidget_annotations.clear()
        self.parent_frame.tableWidget_annotations.setRowCount(0)
        self.parent_frame.tableWidget_annotations.setColumnCount(3)

        self.parent_frame.tableWidget_annotations.setHorizontalHeaderLabels(
            ['Onset', 'Duration', 'Description'])

        for row, annotation in enumerate(annotations):
            self.parent_frame.tableWidget_annotations.insertRow(row)
            onset, duration, description = annotation

            item = QTableWidgetItem(f"{round(onset, 2)}")
            self.parent_frame.tableWidget_annotations.setItem(row, 0, item)
            item = QTableWidgetItem(f"{duration}")
            self.parent_frame.tableWidget_annotations.setItem(row, 1, item)
            item = QTableWidgetItem(description)
            self.parent_frame.tableWidget_annotations.setItem(row, 2, item)

        self.parent_frame.horizontalSlider_record.setValue(0)
        self.parent_frame.widget_record.show()
        QApplication.restoreOverrideCursor()

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

            QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
            self.record_reader = HDF5Reader(os.path.join(
                self.records_dir, f'{self.parent_frame.label_record_name.text()}.h5'))
            self.record_reader.eeg  # cached
            self.record_reader.aux  # cached
            QApplication.restoreOverrideCursor()

            self.start_streaming = 0

            self.start_play = datetime.now()
            self.timer = QTimer()
            self.timer.setInterval(1000 / 4)
            self.timer.timeout.connect(self.update_timer)
            self.timer.start()
            self.parent_frame.pushButton_play_signal.setIcon(
                QIcon.fromTheme('media-playback-pause'))

        else:
            self.record_reader.close()
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

        end_streaming = int((self.record_reader.eeg.shape[1] * self.parent_frame.horizontalSlider_record.value(
        )) / self.parent_frame.horizontalSlider_record.maximum())

        if samples := end_streaming - self.start_streaming:
            if samples < 0:
                samples = (4 * self.record_reader.eeg.shape[1] / 1000)

            # print(samples, [max([end_streaming - samples, 0]), end_streaming])
            samples = int(samples)

            data_ = {'context': 'context',
                     'data': (self.record_reader.eeg[:, max([end_streaming - samples, 0]): end_streaming],
                              self.record_reader.aux[:, max([end_streaming - samples, 0]): end_streaming]),
                     'binary_created': datetime.now().timestamp(),
                     'created': datetime.now().timestamp(),
                     'samples': samples,
                     }
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
            self.subprocess_script = run_subprocess([sys.executable, os.path.join(
                os.environ['BCISTREAM_ROOT'], 'transformers', 'record.py')])

        else:
            self.timer.stop()
            self.parent_frame.pushButton_record.setText(f"Record")
            self.subprocess_script.terminate()

            self.load_records()

