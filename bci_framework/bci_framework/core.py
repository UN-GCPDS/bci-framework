from PySide2.QtUiTools import QUiLoader
from PySide2 import QtWidgets, QtGui, QtCore
from PySide2.QtCore import Qt, QTimer

from PySide2.QtWidgets import QDialogButtonBox

from .qtgui.icons import resource_rc
from .widgets import Montage, Projects, Connection, Records, Annotations
from .environments import Development, Visualization, StimuliDelivery
from .config_manager import ConfigManager

import psutil
import os
import webbrowser
import json


########################################################################
class BCIFramework:

    # ----------------------------------------------------------------------
    def __init__(self):

        self.main = QUiLoader().load(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                                  'qtgui', 'main.ui'))

        self.main.setCorner(Qt.BottomLeftCorner, Qt.LeftDockWidgetArea)
        self.main.setCorner(Qt.BottomRightCorner, Qt.RightDockWidgetArea)

        self.main.actionDevelopment.triggered.connect(
            lambda evt: self.show_interface('Development'))
        self.main.actionVisualizations.triggered.connect(
            lambda evt: self.show_interface('Visualizations'))
        self.main.actionStimuli_delivery.triggered.connect(
            lambda evt: self.show_interface('Stimuli_delivery'))
        self.main.actionHome.triggered.connect(
            lambda evt: self.show_interface('Home'))
        self.main.actionDocumentation.triggered.connect(
            lambda evt: self.show_interface('Documentation'))

        self.show_interface('Home')

        self.config = ConfigManager()

        for i in range(self.main.toolBar_environs.layout().count()):
            tool_button = self.main.toolBar_environs.layout().itemAt(i).widget()
            tool_button.setMaximumWidth(200)
            tool_button.setMinimumWidth(200)

        self.set_editor()
        self.build_collapse_button()

        self.montage = Montage(self)
        self.connection = Connection(self)
        self.projects = Projects(self.main, self)
        self.annotations = Annotations(self.main, self)
        self.records = Records(self.main, self)

        self.development = Development(self)
        self.visualizations = Visualization(self)
        self.stimuli_delivery = StimuliDelivery(self)

        self.status_bar('OpenBCI no connected')

        self.main.tabWidget_widgets.setCurrentIndex(0)
        self.style_welcome()

        self.connect()

        docs = os.path.abspath(os.path.join(
            'docs', 'build', 'html', 'index.html'))
        self.main.webEngineView_documentation.setUrl(f'file://{docs}')

        self.register_subprocess()

    # ----------------------------------------------------------------------
    def register_subprocess(self):
        """"""
        self.subprocess_timer = QTimer()
        self.subprocess_timer.timeout.connect(self.save_subprocess)
        self.subprocess_timer.setInterval(5)
        self.subprocess_timer.start()

    # ----------------------------------------------------------------------
    def save_subprocess(self):
        """"""
        current_process = psutil.Process()
        children = current_process.children(recursive=True)
        file = os.path.join(os.environ['BCISTREAM_HOME'], '.subprocess')
        try:
            with open(file, 'w') as file_:
                json.dump({ch.pid: ch.name()
                           for ch in children}, file_, indent=2)
        except:  # psutil.NoSuchProcess: psutil.NoSuchProcess process no longer exists
            pass

    # ----------------------------------------------------------------------
    def build_collapse_button(self):
        """"""
        # # Corner widget not work on 'West' Tabs, but its make space
        # container = QtWidgets.QWidget(self.main)
        # layout = QtWidgets.QHBoxLayout(container)
        # layout.addWidget(QtWidgets.QPushButton())
        # self.main.tabWidget_widgets.setCornerWidget(
            # container, Qt.TopLeftCorner)

        # And with the space is possible to add ad custom widget
        self.pushButton_collapse_dock = QtWidgets.QPushButton(
            self.main.dockWidget_global)
        self.pushButton_collapse_dock.clicked.connect(
            self.set_dock_collapsed)

        icon = QtGui.QIcon.fromTheme('arrow-right-double')
        self.pushButton_collapse_dock.setIcon(icon)
        self.pushButton_collapse_dock.setCheckable(True)
        self.pushButton_collapse_dock.setFlat(True)

        w = self.main.tabWidget_widgets.tabBar().width()
        self.pushButton_collapse_dock.setMinimumWidth(w)
        self.pushButton_collapse_dock.setMaximumWidth(w)
        self.pushButton_collapse_dock.move(5, 5)

    # ----------------------------------------------------------------------
    def set_dock_collapsed(self, collapsed):
        """"""
        if collapsed:
            w = self.main.tabWidget_widgets.tabBar().width() + 10
            icon = QtGui.QIcon.fromTheme('arrow-left-double')
            self.previous_width = self.main.dockWidget_global.width()
        else:
            if self.main.dockWidget_global.width() > 50:
                return
            icon = QtGui.QIcon.fromTheme('arrow-right-double')
            w = self.previous_width

        self.pushButton_collapse_dock.setIcon(icon)
        self.main.dockWidget_global.setMaximumWidth(w)
        self.main.dockWidget_global.setMinimumWidth(w)

        if not collapsed:
            self.main.dockWidget_global.setMaximumWidth(9999)
            self.main.dockWidget_global.setMinimumWidth(100)

    # ----------------------------------------------------------------------
    def connect(self):
        """"""
        # self.main.dockWidget_global.dockLocationChanged.connect(
            # self.update_dock_tabs)
        # self.main.tabWidget_widgets.currentChanged.connect(
            # self.widget_update)
        self.main.tabWidget_widgets.currentChanged.connect(
            lambda: self.set_dock_collapsed(False))

        self.main.pushButton_add_project_2.clicked.connect(
            self.projects.show_create_project_dialog)

        self.main.pushButton_show_visualization.clicked.connect(
            lambda evt: self.show_interface('Visualizations'))
        self.main.pushButton_show_stimuli_delivery.clicked.connect(
            lambda evt: self.show_interface('Stimuli_delivery'))

        self.main.pushButton_show_documentation.clicked.connect(
            lambda evt: self.show_interface('Documentation'))

        self.main.pushButton_go_to_repository.clicked.connect(
            lambda evt: webbrowser.open_new_tab('https://github.com/UN-GCPDS/bci-framework'))

        self.main.pushButton_show_about.clicked.connect(self.show_about)

    # # ----------------------------------------------------------------------
    # def widget_update(self, index):
        # """"""
        # tab = self.main.tabWidget_widgets.tabText(index)

        # if tab == 'Impedances':
            # self.impedances.update_impedance()

    # ----------------------------------------------------------------------
    def update_dock_tabs(self, event):
        """"""
        if b'Left' in event.name:
            self.main.tabWidget_widgets.setTabPosition(
                self.main.tabWidget_widgets.East)
        elif b'Right' in event.name:
            self.main.tabWidget_widgets.setTabPosition(
                self.main.tabWidget_widgets.West)

    # ----------------------------------------------------------------------
    def show_interface(self, interface):
        """"""
        self.main.stackedWidget_modes.setCurrentWidget(
            getattr(self.main, f"page{interface}"))
        for action in self.main.toolBar_environs.actions():
            action.setChecked(False)
        for action in self.main.toolBar_Documentation.actions():
            action.setChecked(False)
        if action := getattr(self.main, f"action{interface}", False):
            action.setChecked(True)

        if mod := getattr(self, f'{interface.lower().replace(" ", "_")}', False):
            if mod and hasattr(mod, 'on_focus'):
                mod.on_focus()

    # ----------------------------------------------------------------------
    def set_editor(self):
        """"""
        self.main.plainTextEdit_preview_log.setStyleSheet("""
        *{
        font-weight: normal;
        font-family: 'DejaVu Sans Mono';
        font-size: 13px;
        }
        """)

    # ----------------------------------------------------------------------
    def remove_widgets_from_layout(self, layout):
        """"""
        for i in reversed(range(layout.count())):
            if item := layout.takeAt(i):
                item.widget().deleteLater()

    # ----------------------------------------------------------------------
    def status_bar(self, message):
        """"""
        statusbar = self.main.statusBar()
        if not hasattr(statusbar, 'label'):
            statusbar.label = QtWidgets.QLabel(statusbar)
            statusbar.label.mousePressEvent = lambda evt: self.main.tabWidget_widgets.setCurrentWidget(
                self.main.tab_connection)
            statusbar.addWidget(statusbar.label)

        statusbar.label.setText(message)

    # ----------------------------------------------------------------------
    def style_welcome(self):
        """"""
        style = """
        *{
        max-height: 50px;
        min-height: 50px;
        }
        """
        self.main.pushButton_4.setStyleSheet(style)
        self.main.pushButton_6.setStyleSheet(style)
        self.main.pushButton_8.setStyleSheet(style)

        style = """
        *{
        border-color: #4dd0e1;

        }
        """
        self.main.frame_3.setStyleSheet(style)
        self.main.frame_2.setStyleSheet(style)
        self.main.frame.setStyleSheet(style)

        style = """
        *{
        font-family: "Roboto Light";
        font-weight: 400;
        font-size: 18px;
        }
        """
        # color: #4dd0e1;

        self.main.label_15.setStyleSheet(style)
        self.main.label_16.setStyleSheet(style)
        self.main.label_17.setStyleSheet(style)

    # ----------------------------------------------------------------------
    def show_about(self, event=None):
        """"""

        frame = os.path.join(
            os.environ['BCISTREAM_ROOT'], 'bci_framework', 'qtgui', 'about.ui')
        about = QUiLoader().load(frame, self.main)
        about.label.setScaledContents(True)

        about.buttonBox.button(QDialogButtonBox.Close).clicked.connect(
            lambda evt: about.destroy())

        about.tabWidget.setCurrentIndex(0)

        about.plainTextEdit_license.setStyleSheet("""
        *{
        font-weight: normal;
        font-family: 'DejaVu Sans Mono';
        font-size: 13px;
        }
        """)

        about.show()


