"""
===========
Annotations
===========
"""


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
    def connect(self) -> None:
        """Connect events."""
        self.parent_frame.pushButton_save_annotation.clicked.connect(
            self.save_annotation)
        self.parent_frame.pushButton_save_marker.clicked.connect(
            self.save_marker)

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
    def add_annotation(self, onset, duration, description):
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
    def add_marker(self, onset, marker):
        """Write the marker in the GUI."""
        row = self.parent_frame.tableWidget_markers.rowCount()
        self.parent_frame.tableWidget_markers.insertRow(row)

        item = QTableWidgetItem(onset.strftime("%x %X"))
        self.parent_frame.tableWidget_markers.setItem(row, 0, item)
        item = QTableWidgetItem(f"{marker}")
        self.parent_frame.tableWidget_markers.setItem(row, 1, item)
