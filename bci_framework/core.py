# import os
# import sys
# from multiprocessing import Process, Pool
# from threading import Thread


import sys

from datetime import datetime, timedelta
import numpy as np

from PySide2.QtUiTools import QUiLoader
from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *

# from PySide2.Qtsc

# from .qtgui.mpl import MatplotlibWidget

from bci_framework.qtgui.icons import resource_rc
# from bci_framework.highlighters import PythonHighlighter

# from .visualization import VisualizationWidget

# from .widgets_admin import _load_global
# from .montage import Montage


from .config_manager import ConfigManager


# from .scripting import Scripting

import os

# import threading

# from .scripts.EEG import EEG
# from .scripts.Topoplot import TOPO


from bci_framework.dialogs import Dialogs


from bci_framework.widgets import Montage, Projects, Connection, Records

from bci_framework.environments import Development, Visualization

########################################################################
class BCIFramework(QtWidgets.QMainWindow):

    # ----------------------------------------------------------------------
    def __init__(self):
        super().__init__()

        self.main = QUiLoader().load('bci_framework/qtgui/main.ui', self)

        self.main.setCorner(Qt.BottomLeftCorner, Qt.LeftDockWidgetArea)
        self.main.setCorner(Qt.BottomRightCorner, Qt.RightDockWidgetArea)

        # mainWindow->setCorner(Qt::TopLeftCorner, Qt::LeftDockWidgetArea);
        # mainWindow->setCorner(Qt::TopRightCorner, Qt::RightDockWidgetArea);
        # mainWindow->setCorner(Qt::BottomLeftCorner, Qt::LeftDockWidgetArea);
        # mainWindow->setCorner(Qt::BottomRightCorner, Qt::RightDockWidgetArea);

        # self.main.pushButton_add_visualizarion.clicked.connect(self.add_subwindow)

        # self.main.splitter_preview.colla

        # self.threadpool = QtCore.QThreadPool()

        self.main.actionDevelopment.triggered.connect(
            lambda evt: self.show_interface('Development'))
        self.main.actionVisualizations.triggered.connect(
            lambda evt: self.show_interface('Visualizations'))
        self.main.actionStimulus_delivery.triggered.connect(
            lambda evt: self.show_interface('Stimulus_delivery'))
        # self.main.actionSandbox.triggered.connect(lambda evt: self.show_interface('Sandbox'))

        # self.main.actionOpen_project.triggered.connect(self.open_project)
        # self.main.treeWidget_project.itemDoubleClicked.connect(self.open_script)

        # self.main.listWidget_projects.itemDoubleClicked.connect(self.open_project)

        # self.main.pushButton_projects.clicked.connect(lambda evt: self.main.stackedWidget_projects.setCurrentWidget(getattr(self.main, "page_projects")))

        # self.main.listWidget_scripts_stimuli.itemClicked.connect(self.open_script)
        # # self.main.listWidget_scripts_visualization.itemDoubleClicked.connect(self.open_script)
        # self.main.listWidget_scripts_visualization.itemClicked.connect(self.open_script)
        # # self.main.listWidget_scripts_visualization.clicked = lambda evt: None
        # # self.main.listWidget_scripts_visualization.itemClicked = lambda evt: None

        self.show_interface('Development')

        # self.show

        # self.__initScripting__()

        # for i in range(6):
            # self.add_subwindow()

        self.config = ConfigManager()

        for i in range(self.main.toolBar_environs.layout().count()):
            tool_button = self.main.toolBar_environs.layout().itemAt(i).widget()
            tool_button.setMaximumWidth(200)
            tool_button.setMinimumWidth(200)

        self.set_editor()
        # self.load_scripts()

        # self.set_time_labels()

        self.connection = Connection(self)
        self.montage = Montage(self)
        self.projects = Projects(self.main, self)
        self.development = Development(self.main, self)
        self.visualization = Visualization(self.main, self)
        self.records = Records(self.main, self)

        # self.status_bar('message', icon=None)

    # # ----------------------------------------------------------------------
    # def add_subwindow(self):
        # """"""

        # sub = VisualizationWidget(self)
        # sub.update_visualizations()

        # self.main.mdiArea.addSubWindow(sub)
        # sub.show()

        # # # sub.moveToThread(self.my_thread)
        # # # self.my_thread.start()

        # self.main.mdiArea.tileSubWindows()

    # ----------------------------------------------------------------------

    def show_interface(self, interface):
        """"""
        self.main.stackedWidget_modes.setCurrentWidget(
            getattr(self.main, f"page{interface}"))
        for action in self.main.toolBar_environs.actions():
            action.setChecked(False)

        getattr(self.main, f"action{interface}").setChecked(True)

    # ----------------------------------------------------------------------

    def set_editor(self):
        """"""
        # self.main.plainTextEdit_preview_log.hide()
        self.main.plainTextEdit_preview_log.setStyleSheet("""
        *{

        font-weight: normal;
        font-family: 'mono';
        font-size: 13px;

        }
        """)

    # ----------------------------------------------------------------------
    def remove_widgets_from_layout(self, layout):
        """"""
        for i in reversed(range(layout.count())):
            if item := layout.takeAt(i):
                item.widget().deleteLater()

    # # ----------------------------------------------------------------------
    # def status_bar(self, message, icon=None):
        # """"""
        # statusbar = self.main.statusBar()

        # # # statusbar.showMessage('message', 50000)

        # icon = QIcon.fromTheme('media-playback-pause')

        # # pxm = QPixmap(icon)
        # pxm = QPixmap(icon.sca)

        # label = QLabel(statusbar)
        # label.setPixmap(pxm)

        # # btn = QPushButton(icon, "Hola EEG")
        # # btn.setFlat(True)
        # # # btn.setDisabled(True)
        # # btn.setMinimumHeight(24)
        # # btn.setMaximumHeight(24)
        # # # # progress = QProgressBar(self)
        # # # # progress.setValue(50)

        # # # spacer = QSpacerItem()

        # statusbar.addWidget(label)
