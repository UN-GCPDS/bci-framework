from PySide2.QtUiTools import QUiLoader
from PySide2 import QtWidgets
from PySide2.QtCore import Qt

from bci_framework.qtgui.icons import resource_rc
from bci_framework.widgets import Montage, Projects, Connection, Records
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

        self.show_interface('Development')

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

        self.development = Development(self)
        self.visualization = Visualization(self)
        self.stimuli_delivery = StimuliDelivery(self)

        self.status_bar('No connected!')
        self.status_bar('No connected!')
        self.status_bar('No connected!')

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
