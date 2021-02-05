import os
from datetime import datetime
from pathlib import Path

from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QVBoxLayout, QMenuBar, QMenu, QMdiSubWindow, QWidget

from ..dialogs import Dialogs
from ..config_manager import ConfigManager
from ..stream_handler import VisualizationWidget


########################################################################
class Visualization:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, core):
        """Constructor"""

        self.parent_frame = core.main
        self.core = core
        self.config = ConfigManager()

        self.connect()
        self.on_focus()
        self.add_subwindow()

    # ----------------------------------------------------------------------
    def connect(self):
        """"""
        self.parent_frame.pushButton_load_visualizarion.clicked.connect(
            self.add_subwindow)
        self.parent_frame.pushButton_visualizations_remove_all.clicked.connect(
            self.remove_all)
        self.parent_frame.pushButton_visualizations_reload_all.clicked.connect(
            self.reload_all)

    # ----------------------------------------------------------------------
    def on_focus(self):
        """"""
        self.parent_frame.mdiArea.tileSubWindows()

        self.visualizations_list = []
        for i in range(self.parent_frame.listWidget_projects_visualizations.count()):
            item = self.parent_frame.listWidget_projects_visualizations.item(i)
            self.visualizations_list.append(item.text())

    # ----------------------------------------------------------------------
    def reload_all(self):
        """"""
        for sub in self.parent_frame.mdiArea.subWindowList():
            sub.reload()

    # ----------------------------------------------------------------------
    def remove_all(self):
        """"""
        for sub in self.parent_frame.mdiArea.subWindowList():
            sub.remove()
        QTimer().singleShot(100, self.widgets_set_enabled)

    # ----------------------------------------------------------------------
    def add_subwindow(self):
        """"""
        sub = VisualizationWidget(
            self.parent_frame.mdiArea, self.visualizations_list, mode='visualization')
        self.parent_frame.mdiArea.addSubWindow(sub)
        sub.show()
        self.parent_frame.mdiArea.tileSubWindows()
        sub.update_menu_bar()
        sub.loaded = self.widgets_set_enabled

        sub.destroyed.connect(self.widgets_set_enabled)
        self.widgets_set_enabled()

    # ----------------------------------------------------------------------
    def widgets_set_enabled(self):
        """"""
        subwindows = len(self.parent_frame.mdiArea.subWindowList()) != 0
        self.parent_frame.pushButton_visualizations_remove_all.setEnabled(
            subwindows)

        self.parent_frame.pushButton_visualizations_reload_all.setEnabled(
            False)

        for sub in self.parent_frame.mdiArea.subWindowList():
            if getattr(sub, 'stream_subprocess', False):
                self.parent_frame.pushButton_visualizations_reload_all.setEnabled(
                    True)
                break


