import os

from PySide2 import QtWidgets
# .QDialog.QFileDialog import getExistingDirectory


########################################################################
class Dialogs:
    """"""

    #----------------------------------------------------------------------
    @classmethod
    def open_project(cls, parent, dirpath=None):
        """"""

        if dirpath is None:
            dirpath = parent.get_default_dir()

        open_dir = QtWidgets.QFileDialog.getExistingDirectory(parent,
                "{APP_NAME} - Open project".format(**os.environ),
                dirpath)

        if open_dir:
            return open_dir
        else:
            return None
