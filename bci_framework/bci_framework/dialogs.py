import os

from PySide2 import QtWidgets, QtGui
from PySide2.QtCore import Qt

# .QDialog.QFileDialog import getExistingDirectory


########################################################################
class Dialogs:
    """"""

    # ----------------------------------------------------------------------
    @classmethod
    def open_project(cls, parent, dirpath=None):
        """"""

        if dirpath is None:
            dirpath = parent.get_default_dir()

        open_dir = QtWidgets.QFileDialog.getExistingDirectory(
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
        msgBox = QtWidgets.QMessageBox.critical(
            parent, title, text, QtWidgets.QMessageBox.Ok)

    # ----------------------------------------------------------------------
    @classmethod
    def question_message(self, parent, title, text):
        """"""
        msgBox = QtWidgets.QMessageBox.question(
            parent, title, text, QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)

        return msgBox == QtWidgets.QMessageBox.Ok

    # ----------------------------------------------------------------------
    @classmethod
    def warning_message(self, parent, title, text):
        """"""
        msgBox = QtWidgets.QMessageBox.warning(
            parent, title, text, QtWidgets.QMessageBox.Ok
        )

    # ----------------------------------------------------------------------
    @staticmethod
    def save_filename(parent, title, start_dir, filter):
        """"""
        path = QtWidgets.QFileDialog.getSaveFileName(parent,
                                                     title,
                                                     start_dir, filter)

        # dial = QtWidgets.QFileDialog(parent)
        # dial.setStyleSheet("")
        # dial.setWindowTitle(title)
        # dial.getSaveFileName()

        # if dial.exec_() == QtWidgets.QFileDialog.Accepted:
            # path = dial.selectedFiles()[0]

        return path[0]
