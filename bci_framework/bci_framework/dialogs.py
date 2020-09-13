import os

from PySide2 import QtWidgets
# from PySide2 import QtGui
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

        open_dir = QtWidgets.QFileDialog.getExistingDirectory(parent,
                                                              "{APP_NAME} - Open project".format(
                                                                  **os.environ),
                                                              dirpath)

        if open_dir:
            return open_dir
        else:
            return None

    # ----------------------------------------------------------------------
    @classmethod
    def critical_message(self, parent, title, text):
        """"""
        msgBox = QtWidgets.QMessageBox.critical(parent,
                                                title,
                                                text,
                                                QtWidgets.QMessageBox.Ok)

    # ----------------------------------------------------------------------
    @classmethod
    def question_message(self, parent, title, text):
        """"""
        msgBox = QtWidgets.QMessageBox.question(parent,
                                                title,
                                                text,
                                                QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)

        return msgBox == QtWidgets.QMessageBox.Ok

    # ----------------------------------------------------------------------

    @classmethod
    def warning_message(self, parent, title, text):
        """"""
        msgBox = QtWidgets.QMessageBox.warning(parent,
                                               title,
                                               text,
                                               QtWidgets.QMessageBox.Ok)
