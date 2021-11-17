"""
=======
Dialogs
=======
"""

import os
from typing import TypeVar, Optional

from PySide2.QtWidgets import QFileDialog, QMessageBox

from ..extensions.timelock_analysis import FileHandler

PATH = TypeVar('Path')


########################################################################
class Dialogs:
    """"""

    # ---------------------------- ------------------------------------------
    @classmethod
    def critical_message(self, parent, title: str, text: str) -> None:
        """Critical message."""
        msgBox = QMessageBox.critical(
            parent, title, text, QMessageBox.Ok)

    # ----------------------------------------------------------------------
    @classmethod
    def question_message(self, parent, title: str, text: str) -> None:
        """Question message."""
        msgBox = QMessageBox.question(
            parent, title, text, QMessageBox.Ok | QMessageBox.Cancel)

        return msgBox == QMessageBox.Ok

    # ----------------------------------------------------------------------
    @classmethod
    def remove_file_warning(cls, parent, filename: PATH) -> bool:
        """"""
        return cls.question_message(parent, 'Remove file?', f"""<p>This action
        cannot be undone.<br><br><nobr>Remove permanently the file
        <code>{filename}.h5</code> from your system?</nobr></p>""")

    # ----------------------------------------------------------------------
    @classmethod
    def load_database(cls):
        """"""
        path = os.path.join(os.getenv('BCISTREAM_HOME'), 'records')
        filters = "EEG data (*.h5 *.edf)"

        filename = QFileDialog.getOpenFileName(
            None, 'Open file', path, filters)[0]

        return FileHandler(filename)

