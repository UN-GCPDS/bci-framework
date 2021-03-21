"""
===========
Annotations
===========
"""

from typing import Optional

from PySide2.QtWidgets import QTableWidgetItem


########################################################################
class Annotations:
    """Widget connected with Kafka to stream messages."""

    # ----------------------------------------------------------------------
    def __init__(self, parent, core):
        """Constructor"""

        self.parent_frame = parent
        self.core = core
        self.connect()

    # ----------------------------------------------------------------------
    def set_enable(self, enable):
        """"""
        self.parent_frame.pushButton_save_annotation.setEnabled(enable)
        self.parent_frame.pushButton_save_marker.setEnabled(enable)
        self.parent_frame.pushButton_save_command.setEnabled(enable)

    # ----------------------------------------------------------------------
    def connect(self) -> None:
        """Connect events."""
        self.parent_frame.pushButton_save_annotation.clicked.connect(
            self.save_annotation)
        self.parent_frame.pushButton_save_marker.clicked.connect(
            self.save_marker)
        self.parent_frame.pushButton_save_command.clicked.connect(
            self.save_command)

        self.parent_frame.pushButton_remove_annotations.clicked.connect(lambda:
                                                                        self.parent_frame.tableWidget_annotations.setRowCount(0))
        self.parent_frame.pushButton_remove_markers.clicked.connect(lambda:
                                                                    self.parent_frame.tableWidget_markers.setRowCount(0))
        self.parent_frame.pushButton_remove_commands.clicked.connect(lambda:
                                                                     self.parent_frame.tableWidget_commands.setRowCount(0))

    # ----------------------------------------------------------------------
    def save_annotation(self) -> None:
        """Write the annotation in the streaming."""
        content = self.parent_frame.textEdit_annotations.toPlainText()
        duration = self.parent_frame.doubleSpinBox_annotation_duration.value()

        data_ = {'duration': duration,
                 'description': content, }

        self.core.thread_kafka.produser.send('annotation', data_)

    # ----------------------------------------------------------------------
    def save_marker(self) -> None:
        """Write the marker in the streaming."""
        marker = self.parent_frame.lineEdit_marker.text()
        data_ = {'marker': marker, }
        self.core.thread_kafka.produser.send('marker', data_)

    # ----------------------------------------------------------------------
    def save_command(self) -> None:
        """Write the command in the streaming."""
        command = self.parent_frame.lineEdit_command.text()
        data_ = {'command': command, }
        self.core.thread_kafka.produser.send('command', data_)

    # ----------------------------------------------------------------------
    def add_annotation(self, onset, duration: str, description: str, action: Optional[bool] = True) -> None:
        """Write the annotation in the GUI."""
        row = self.parent_frame.tableWidget_annotations.rowCount()
        self.parent_frame.tableWidget_annotations.insertRow(row)

        item = QTableWidgetItem(onset.strftime("%x %X"))
        self.parent_frame.tableWidget_annotations.setItem(row, 0, item)
        item = QTableWidgetItem(f"{duration}")
        self.parent_frame.tableWidget_annotations.setItem(row, 1, item)
        item = QTableWidgetItem(description)
        self.parent_frame.tableWidget_annotations.setItem(row, 2, item)

        if description == 'start_record':
            self.core.records.record_signal(True)
        elif description == 'stop_record':
            self.core.records.record_signal(False)

    # ----------------------------------------------------------------------
    def add_marker(self, onset: str, marker: str, timestamp: Optional[bool] = True) -> None:
        """Write the marker in the GUI."""
        row = self.parent_frame.tableWidget_markers.rowCount()
        self.parent_frame.tableWidget_markers.insertRow(row)

        if timestamp:
            item = QTableWidgetItem(onset.strftime("%x %X"))
        else:
            item = QTableWidgetItem(onset)
        self.parent_frame.tableWidget_markers.setItem(row, 0, item)
        item = QTableWidgetItem(f"{marker}")
        self.parent_frame.tableWidget_markers.setItem(row, 1, item)

    # ----------------------------------------------------------------------
    def add_command(self, onset: str, command: str) -> None:
        """Write the command in the GUI."""
        row = self.parent_frame.tableWidget_commands.rowCount()
        self.parent_frame.tableWidget_commands.insertRow(row)

        item = QTableWidgetItem(onset.strftime("%x %X"))
        self.parent_frame.tableWidget_commands.setItem(row, 0, item)
        item = QTableWidgetItem(f"{marker}")
        self.parent_frame.tableWidget_commands.setItem(row, 1, item)

    # ----------------------------------------------------------------------
    def bulk_annotations(self, annotations):
        """"""
        columns = ['Onset', 'Duration', 'Description']
        self.parent_frame.tableWidget_annotations.clear()
        self.parent_frame.tableWidget_annotations.setRowCount(0)
        self.parent_frame.tableWidget_annotations.setColumnCount(len(columns))
        self.parent_frame.tableWidget_annotations.setHorizontalHeaderLabels(
            columns)
        for onset, duration, description in annotations:
            if not description in ['start_record', 'stop_record']:
                self.add_annotation(onset, duration, description, action=False)
        self.parent_frame.tableWidget_annotations.sortByColumn(0)

    # ----------------------------------------------------------------------
    def bulk_markers(self, markers):
        """"""
        columns = ['Datetime', 'Marker']
        self.parent_frame.tableWidget_markers.clear()
        self.parent_frame.tableWidget_markers.setRowCount(0)
        self.parent_frame.tableWidget_markers.setColumnCount(len(columns))
        self.parent_frame.tableWidget_markers.setHorizontalHeaderLabels(
            columns)
        for marker in markers:
            for onset in markers[marker]:
                self.add_marker(f'{onset/1000:.2f} s', marker, timestamp=False)
        self.parent_frame.tableWidget_markers.sortByColumn(0)
