from PySide2.QtWidgets import QTableWidgetItem
from datetime import datetime


########################################################################
class Annotations:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, parent, core):
        """Constructor"""

        self.parent_frame = parent
        self.core = core

        self.parent_frame.stackedWidget_annotations.setStyleSheet("""
        .QWidget {
        background-color: '#232629';
        }""")

        self.parent_frame.plainTextEdit_annotations.setStyleSheet("""
        * {
        padding: 10px;
        }
        """)

        self.parent_frame.pushButton_remove_annotation.setDisabled(True)

        self.editor_set_visible(visible=False)
        self.connect()

    # ----------------------------------------------------------------------
    def editor_set_visible(self, visible=True):
        """"""
        if visible:
            index = 1
        else:
            index = 0
        self.parent_frame.stackedWidget_annotations.setCurrentIndex(index)

    # ----------------------------------------------------------------------
    def connect(self):
        """"""
        self.parent_frame.pushButton_save_annotation.clicked.connect(self.save_annotation)
        self.parent_frame.pushButton_new_annotation.clicked.connect(self.new_annotation)
        self.parent_frame.pushButton_remove_annotation.clicked.connect(self.remove_annotation)
        self.parent_frame.pushButton_cancel_annotation.clicked.connect(lambda: self.editor_set_visible(visible=False))

    # ----------------------------------------------------------------------
    def save_annotation(self):
        """"""
        content = self.parent_frame.plainTextEdit_annotations.toPlainText()
        self.editor_set_visible(visible=False)

        row = self.parent_frame.tableWidget_annotations.rowCount()
        self.parent_frame.tableWidget_annotations.insertRow(row)

        item = QTableWidgetItem(self.now_annotation.strftime("%x %X"))
        self.parent_frame.tableWidget_annotations.setItem(row, 0, item)
        item = QTableWidgetItem(content)
        self.parent_frame.tableWidget_annotations.setItem(row, 1, item)

        self.parent_frame.pushButton_remove_annotation.setEnabled(True)

    # ----------------------------------------------------------------------
    def new_annotation(self):
        """"""
        self.now_annotation = datetime.now()
        self.editor_set_visible(True)
        content = "<NEW ANNOTATION>"
        self.parent_frame.plainTextEdit_annotations.setPlainText(content)
        cursor = self.parent_frame.plainTextEdit_annotations.selectAll()

    # ----------------------------------------------------------------------
    def remove_annotation(self):
        """"""
        row = self.parent_frame.tableWidget_annotations.currentRow()
        if row >= 0:
            self.parent_frame.tableWidget_annotations.removeRow(row)

        if not self.parent_frame.tableWidget_annotations.rowCount():
            self.parent_frame.pushButton_remove_annotation.setDisabled(True)
