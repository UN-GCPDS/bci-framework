"""
========
Projects
========
"""

import sys

from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QApplication

from openbci_stream.acquisition import restart_services


########################################################################
class Raspad:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, parent, core):
        """"""
        self.parent_frame = parent
        self.core = core

        self.parent_frame.checkBox_full_screen.setChecked(
            '--raspad' in sys.argv)

        self.connect()

    # ----------------------------------------------------------------------
    def connect(self) -> None:
        """Connect events."""

        self.parent_frame.checkBox_full_screen.clicked.connect(
            self.fullscreen)
        self.parent_frame.pushButton_close_framework.clicked.connect(
            QApplication.closeAllWindows)
        self.parent_frame.pushButton_restart_daemons.clicked.connect(
            self.core.connection.restart_services)
        self.parent_frame.pushButton_take_screenshot.clicked.connect(
            lambda: QTimer().singleShot(3000, self.take_screenshot))

    # ----------------------------------------------------------------------
    def fullscreen(self):
        """"""
        if self.parent_frame.checkBox_full_screen.isChecked():
            self.parent_frame.showMaximized()
            self.parent_frame.showFullScreen()
        else:
            self.parent_frame.showMaximized()

    # ----------------------------------------------------------------------
    def take_screenshot(self):
        """"""
        pixmap = self.parent_frame.grab()
        pixmap.save(f'/home/yeison/screenshot.png')



