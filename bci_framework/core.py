from PySide2.QtUiTools import QUiLoader
from PySide2 import QtWidgets
from PySide2.QtCore import Qt

from bci_framework.qtgui.icons import resource_rc
from bci_framework.widgets import Montage, Projects, Connection, Records, Impedances
from bci_framework.environments import Development, Visualization, StimuliDelivery
from .config_manager import ConfigManager

########################################################################
class BCIFramework(QtWidgets.QMainWindow):

    # ----------------------------------------------------------------------
    def __init__(self):
        super().__init__()

        self.main = QUiLoader().load('bci_framework/qtgui/main.ui', self)

        self.main.setCorner(Qt.BottomLeftCorner, Qt.LeftDockWidgetArea)
        self.main.setCorner(Qt.BottomRightCorner, Qt.RightDockWidgetArea)

        self.main.actionDevelopment.triggered.connect(
            lambda evt: self.show_interface('Development'))
        self.main.actionVisualizations.triggered.connect(
            lambda evt: self.show_interface('Visualizations'))
        self.main.actionStimulus_delivery.triggered.connect(
            lambda evt: self.show_interface('Stimulus_delivery'))
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

        self.connection = Connection(self)
        self.montage = Montage(self)
        self.projects = Projects(self.main, self)
        self.records = Records(self.main, self)
        self.impedances = Impedances(self.main, self)

        self.development = Development(self)
        self.visualization = Visualization(self)
        self.stimuli_delivery = StimuliDelivery(self)

        self.status_bar('OpenBCI no connected')
        # self.status_bar('No connected!')
        # self.status_bar('No connected!')

        self.main.tabWidget_widgets.setCurrentIndex(0)
        self.style_welcome()

        self.connect()

    # ----------------------------------------------------------------------
    def connect(self):
        """"""
        self.main.dockWidget_global.dockLocationChanged.connect(
            self.update_dock_tabs)

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


