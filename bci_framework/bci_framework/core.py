from PySide2.QtUiTools import QUiLoader
from PySide2 import QtWidgets
from PySide2.QtCore import Qt, QTimer

from PySide2.QtWidgets import QDialogButtonBox

from .qtgui.icons import resource_rc
from .widgets import Montage, Projects, Connection, Records
from .environments import Development, Visualization, StimuliDelivery
from .config_manager import ConfigManager

import os
import webbrowser

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

        # self.show_interface('Development')
        self.show_interface('Home')
        # self.show_interface('Documentation')
        # self.main.stackedWidget_modes.setCurrentWidget(self.main.pa)

        self.config = ConfigManager()

        for i in range(self.main.toolBar_environs.layout().count()):
            tool_button = self.main.toolBar_environs.layout().itemAt(i).widget()
            tool_button.setMaximumWidth(200)
            tool_button.setMinimumWidth(200)

        self.set_editor()

        self.montage = Montage(self)
        self.connection = Connection(self)
        self.projects = Projects(self.main, self)
        self.records = Records(self.main, self)

        self.development = Development(self)
        self.visualization = Visualization(self)
        self.stimuli_delivery = StimuliDelivery(self)

        self.status_bar('OpenBCI no connected')

        self.main.tabWidget_widgets.setCurrentIndex(0)
        self.style_welcome()

        self.connect()

        docs = os.path.abspath(os.path.join(
            'docs', 'build', 'html', 'index.html'))
        self.main.webEngineView_documentation.setUrl(f'file://{docs}')

        # from .dialogs import Dialogs

        # Dialogs.save_filename(self, '', '', '')

    # ----------------------------------------------------------------------
    def connect(self):
        """"""
        self.main.dockWidget_global.dockLocationChanged.connect(
            self.update_dock_tabs)
        self.main.tabWidget_widgets.currentChanged.connect(
            self.widget_update)

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

    # ----------------------------------------------------------------------
    def widget_update(self, index):
        """"""
        tab = self.main.tabWidget_widgets.tabText(index)

        if tab == 'Impedances':
            self.impedances.update_impedance()

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

    # ----------------------------------------------------------------------
    def set_editor(self):
        """"""
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
        about = QUiLoader().load('bci_framework/qtgui/about.ui', self)
        about.label.setScaledContents(True)

        about.buttonBox.button(QDialogButtonBox.Close).clicked.connect(
            lambda evt: about.destroy())

        about.show()


