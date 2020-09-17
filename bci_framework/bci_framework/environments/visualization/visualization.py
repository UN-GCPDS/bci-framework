import os
from datetime import datetime
from pathlib import Path

from .visualization_widget import VisualizationWidget

from PySide2.QtWidgets import QVBoxLayout, QMenuBar, QMenu, QMdiSubWindow, QWidget

from ...dialogs import Dialogs
from ...config_manager import ConfigManager

########################################################################
class Visualization:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, core):
        """Constructor"""

        self.parent_frame = core.main
        self.core = core
        self.config = ConfigManager()

        self.visualizations_list = []
        self.update_visualizations_list()
        self.connect()

    # ----------------------------------------------------------------------
    def connect(self):
        """"""
        # self.parent.comboBox_load_visualization.activated.connect(
        # self.add_subwindow)
        self.parent_frame.pushButton_load_visualizarion.clicked.connect(
            self.add_subwindow)

    # ----------------------------------------------------------------------
    def update_visualizations_list(self, event=None):
        """"""
        for i in range(self.parent_frame.listWidget_projects.count()):
            item = self.parent_frame.listWidget_projects.item(i)
            if item.icon_name == 'icon_viz':
                self.visualizations_list.append(item.text())
                # self.parent.comboBox_load_visualization.addItem(item.text())

    # ----------------------------------------------------------------------
    def add_subwindow(self, event=None):
        """"""        
        sub = VisualizationWidget(self.parent_frame.mdiArea, self.visualizations_list)
        self.parent_frame.mdiArea.addSubWindow(sub)
        sub.show()
        self.parent_frame.mdiArea.tileSubWindows()
        sub.update_menu_bar()
