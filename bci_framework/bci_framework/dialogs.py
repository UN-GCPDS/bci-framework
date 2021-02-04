import os

from PySide2.QtWidgets import QFileDialog, QMessageBox


########################################################################
class Dialogs:
    """"""

    # ----------------------------------------------------------------------
    @classmethod
    def open_project(cls, parent, dirpath=None):
        """"""

        if dirpath is None:
            dirpath = parent.get_default_dir()

        open_dir = QFileDialog.getExistingDirectory(
            parent, "{APP_NAME} - Open project".format(**os.environ), dirpath
        )

        if open_dir:
            return open_dir
        else:
            return None

    # ---------------------------- ------------------------------------------
    @classmethod
    def critical_message(self, parent, title, text):
        """"""
        msgBox = QMessageBox.critical(
            parent, title, text, QMessageBox.Ok)

    # ----------------------------------------------------------------------
    @classmethod
    def question_message(self, parent, title, text):
        """"""
        msgBox = QMessageBox.question(
            parent, title, text, QMessageBox.Ok | QMessageBox.Cancel)

        return msgBox == QMessageBox.Ok

    # ----------------------------------------------------------------------
    @classmethod
    def warning_message(self, parent, title, text):
        """"""
        msgBox = QMessageBox.warning(
            parent, title, text, QMessageBox.Ok
        )

    # ----------------------------------------------------------------------
    @staticmethod
    def save_filename(parent, title, start_dir, filter):
        """"""
        path = QFileDialog.getSaveFileName(parent,
                                           title,
                                           start_dir, filter)

        # dial = QFileDialog(parent)
        # dial.setStyleSheet("")
        # dial.setWindowTitle(title)
        # dial.getSaveFileName()

        # if dial.exec_() == QFileDialog.Accepted:
            # path = dial.selectedFiles()[0]

        return path[0]
