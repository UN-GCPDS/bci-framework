import os
import json
import psutil
import pickle
from datetime import datetime

from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import Qt, QTimer, QSize, Signal, QThread, Slot
from PySide2.QtGui import QPixmap, QIcon
from PySide2.QtWidgets import QDesktopWidget, QMainWindow, QDialogButtonBox, QPushButton, QLabel

from kafka import KafkaProducer, KafkaConsumer

from .widgets import Montage, Projects, Connection, Records, Annotations
from .environments import Development, Visualization, StimuliDelivery
from .config_manager import ConfigManager
from .configuration import ConfigurationFrame


########################################################################
class Kafka(QThread):
    """"""
    over = Signal(object)
    message = Signal()
    continue_ = True

    # ----------------------------------------------------------------------
    def set_host(self, host):
        """"""
        self.host = host

    # ----------------------------------------------------------------------
    def stop(self):
        """"""
        self.continue_ = False
        self.terminate()

    # ----------------------------------------------------------------------
    def run(self):
        """"""
        try:
            self.create_produser()
            self.create_consumer()
        except:
            self.message.emit()
            self.stop()

    # ----------------------------------------------------------------------
    def create_consumer(self):
        """"""
        bootstrap_servers = [f'{self.host}:9092']
        topics = ['annotation', 'marker', 'eeg']
        self.consumer = KafkaConsumer(bootstrap_servers=bootstrap_servers,
                                      value_deserializer=pickle.loads,
                                      auto_offset_reset='latest',
                                      )

        self.consumer.subscribe(topics)

        for message in self.consumer:
            self.last_message = datetime.now()
            message.value['timestamp'] = message.timestamp / 1000
            self.over.emit({'topic': message.topic, 'value': message.value})

            if not self.continue_:
                return

    # ----------------------------------------------------------------------
    def create_produser(self):
        """"""
        self.produser = KafkaProducer(bootstrap_servers=[f'{self.host}:9092'],
                                      compression_type='gzip',
                                      value_serializer=pickle.dumps,
                                      )

########################################################################
class BCIFramework(QMainWindow):

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.main = QUiLoader().load(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                                  'qtgui', 'main.ui'))
        self.set_icons()

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
        self.records = Records(self.main, self)
        self.annotations = Annotations(self.main, self)

        self.development = Development(self)
        self.visualizations = Visualization(self)
        self.stimuli_delivery = StimuliDelivery(self)

        # self.status_bar('OpenBCI no connected')

        self.main.tabWidget_widgets.setCurrentIndex(0)
        self.style_welcome()

        self.connect()

        docs = os.path.abspath(os.path.join(
            'docs', 'build', 'html', 'index.html'))
        self.main.webEngineView_documentation.setUrl(f'file://{docs}')

        self.register_subprocess()

        self.status_bar(message='', right_message=('Diconected', None))

    # ----------------------------------------------------------------------
    def set_icons(self):

        def icon(name):
            return QIcon(f"bci:/primary/{name}.svg")

        self.main.actionDevelopment.setIcon(icon("file"))
        self.main.actionVisualizations.setIcon(icon("brain"))
        self.main.actionStimuli_delivery.setIcon(icon("imagery"))
        self.main.actionHome.setIcon(icon("home"))
        self.main.actionDocumentation.setIcon(icon("documentation"))

        self.main.pushButton_file.setIcon(icon("file"))
        self.main.pushButton_brain.setIcon(icon("brain"))
        self.main.pushButton_imagery.setIcon(icon("imagery"))
        self.main.pushButton_docs.setIcon(icon("documentation"))

        self.main.pushButton_stop_preview.setIcon(icon('media-playback-stop'))
        self.main.pushButton_script_preview.setIcon(
            icon('media-playback-start'))
        self.main.pushButton_play_signal.setIcon(icon('media-playback-start'))
        self.main.pushButton_clear_debug.setIcon(icon('edit-delete'))
        self.main.pushButton_record.setIcon(icon('media-record'))

        self.main.pushButton_projects_add_file.setIcon(icon('document-new'))
        self.main.pushButton_projects_add_folder.setIcon(icon('folder-add'))
        self.main.pushButton_add_project.setIcon(icon('folder-add'))
        self.main.pushButton_projects_remove.setIcon(icon('edit-delete'))
        self.main.pushButton_remove_project.setIcon(icon('edit-delete'))
        self.main.pushButton_remove_montage.setIcon(icon('edit-delete'))

        self.main.pushButton_projects.setIcon(icon('go-up'))
        self.main.pushButton_load_visualizarion.setIcon(icon('list-add'))

        self.main.setWindowIcon(icon("logo"))

    # ----------------------------------------------------------------------
    def register_subprocess(self):
        """"""
        self.subprocess_timer = QTimer()
        self.subprocess_timer.timeout.connect(self.save_subprocess)
        self.subprocess_timer.setInterval(5000)
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
        # And with the space is possible to add ad custom widget
        self.pushButton_collapse_dock = QPushButton(
            self.main.dockWidget_global)
        self.pushButton_collapse_dock.clicked.connect(
            self.set_dock_collapsed)

        icon = QIcon('bci:/primary/arrow-right-double.svg')
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
            icon = QIcon('bci:/primary/arrow-left-double.svg')
            self.previous_width = self.main.dockWidget_global.width()
        else:
            if self.main.dockWidget_global.width() > 50:
                return
            icon = QIcon('bci:/primary/arrow-right-double.svg')
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

        self.main.pushButton_show_about.clicked.connect(self.show_about)
        self.main.pushButton_show_configurations.clicked.connect(
            self.show_configurations)

        self.main.tabWidget_widgets.currentChanged.connect(self.show_widget)

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
            if on_focus := getattr(mod, 'on_focus'):
                on_focus()

    # ----------------------------------------------------------------------
    def show_widget(self, index):
        """"""
        widget = self.main.tabWidget_widgets.tabText(index)
        if wg := getattr(self, widget.lower(), False):
            if on_focus := getattr(wg, 'on_focus', False):
                on_focus()

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

        self.main.mdiArea.setStyleSheet(f"""
        *{{
        background: {os.environ.get('QTMATERIAL_SECONDARYDARKCOLOR')};
        }}
        """)

    # ----------------------------------------------------------------------
    def remove_widgets_from_layout(self, layout):
        """"""
        for i in reversed(range(layout.count())):
            if item := layout.takeAt(i):
                item.widget().deleteLater()

    # ----------------------------------------------------------------------
    def status_bar(self, message=None, right_message=None):
        """"""
        statusbar = self.main.statusBar()

        if not hasattr(statusbar, 'right_label'):
            statusbar.right_label = QLabel(statusbar)
            statusbar.right_label.setAlignment(Qt.AlignRight)
            statusbar.right_label.mousePressEvent = lambda evt: self.main.tabWidget_widgets.setCurrentWidget(
                self.main.tab_connection)
            statusbar.addPermanentWidget(statusbar.right_label)

            statusbar.btn = QPushButton()
            statusbar.btn.setProperty('class', 'connection')
            statusbar.btn.setCheckable(True)
            statusbar.addPermanentWidget(statusbar.btn)

        if message:
            statusbar.showMessage(message)

        if right_message:
            message, status = right_message
            statusbar.right_label.setText(message)
            if status is None:
                statusbar.btn.setDisabled(True)
            else:
                statusbar.btn.setDisabled(False)
                statusbar.btn.setChecked(not status)

    # ----------------------------------------------------------------------
    def style_welcome(self):
        """"""
        style = """
        *{
        width:      80px;
        height:     80px;
        max-width:  80px;
        min-width:  80px;
        max-height: 80px;
        min-height: 80px;
        }
        """
        self.main.pushButton_file.setStyleSheet(style)
        self.main.pushButton_brain.setStyleSheet(style)
        self.main.pushButton_imagery.setStyleSheet(style)
        self.main.pushButton_docs.setStyleSheet(style)

        style = f"""
        *{{
        background-color: {os.environ.get('secondaryColor')}
        }}
        """
        self.main.frame_3.setStyleSheet(style)
        self.main.frame_2.setStyleSheet(style)
        self.main.frame_5.setStyleSheet(style)
        self.main.frame.setStyleSheet(style)

        style = """
        *{
        font-family: "Roboto Light";
        font-weight: 300;
        font-size: 18px;
        }
        """

        self.main.label_15.setStyleSheet(style)
        self.main.label_16.setStyleSheet(style)
        self.main.label_17.setStyleSheet(style)
        self.main.label_20.setStyleSheet(style)

    # ----------------------------------------------------------------------
    def show_about(self, event=None):
        """"""

        frame = os.path.join(
            os.environ['BCISTREAM_ROOT'], 'bci_framework', 'qtgui', 'about.ui')
        about = QUiLoader().load(frame, self.main)
        about.label.setScaledContents(True)

        about.buttonBox.button(QDialogButtonBox.Close).clicked.connect(
            lambda evt: about.destroy())

        about.label.setMinimumSize(QSize(720, 200))
        about.label.setMaximumSize(QSize(720, 200))

        banner = os.path.join(
            os.environ['BCISTREAM_ROOT'], 'assets', 'banner.png')
        about.label.setPixmap(QPixmap(banner))

        about.tabWidget.setCurrentIndex(0)

        about.plainTextEdit_license.setStyleSheet("""
        *{
        font-weight: normal;
        font-family: 'DejaVu Sans Mono';
        font-size: 13px;
        }
        """)

        center = QDesktopWidget().availableGeometry().center()
        geometry = about.frameGeometry()
        geometry.moveCenter(center)
        about.move(geometry.topLeft())

        about.show()

    @Slot()
    # ----------------------------------------------------------------------
    def on_kafka_event(self, value):
        """"""
        self.main.pushButton_connect.setChecked(True)
        self.main.pushButton_connect.setText('Disconnect')
        self.streaming = True

        if value['topic'] == 'marker':
            self.annotations.add_marker(datetime.fromtimestamp(
                value['value']['timestamp']), value['value']['marker'])
        elif value['topic'] == 'annotation':
            self.annotations.add_annotation(datetime.fromtimestamp(value['value']['timestamp']),
                                            value['value']['duration'],
                                            value['value']['description'])
        elif value['topic'] == 'eeg':
            # self.status_bar('Incoming streaming detected')
            eeg, aux = value['value']['data']
            binary_created = datetime.fromtimestamp(
                value['value']['context']['binary_created'])
            message_created = datetime.fromtimestamp(
                value['value']['timestamp'])
            # since = (datetime.now() - binary_created).total_seconds()
            since = (message_created - binary_created).total_seconds()
            count = value['value']['context']['samples']
            channels = eeg.shape[0]

            if since * 1000 > 2000:
                color = '#ffc107'  # old data
            else:
                color = '#3fc55e'  # recent data

            message = f'Last package streamed <b style="color:{color};">{since*1000:0.2f} ms </b> ago | EEG ({channels},{count})'

            if aux.size:
                message += f' | AUX ({aux.shape[0]},{aux.shape[1]})'

            self.status_bar(right_message=(message, True))

    # ----------------------------------------------------------------------
    def update_kafka(self, host):
        """"""
        if hasattr(self, 'thread_kafka'):
            self.thread_kafka.stop()
            self.status_bar(right_message=('No streaming', False))
        # try:
        self.thread_kafka = Kafka()
        self.thread_kafka.over.connect(self.on_kafka_event)
        self.thread_kafka.message.connect(self.kafka_message)
        self.thread_kafka.set_host(host)
        self.thread_kafka.start()

        self.timer = QTimer()
        self.timer.setInterval(5000)
        self.timer.timeout.connect(self.keep_updated)
        self.timer.start()

    # ----------------------------------------------------------------------
    def stop_kafka(self):
        """"""
        self.streaming = False
        if hasattr(self, 'thread_kafka'):
            self.thread_kafka.stop()
            self.status_bar(right_message=('No streaming', False))

    # ----------------------------------------------------------------------
    def keep_updated(self):
        """"""
        if hasattr(self, 'thread_kafka') and hasattr(self.thread_kafka, 'last_message'):
            last = datetime.now() - self.thread_kafka.last_message
            if last.seconds > 3:
                self.status_bar(right_message=('No streaming', False))

    # ----------------------------------------------------------------------
    @Slot()
    def kafka_message(self):
        """"""
        self.streaming = False
        if self.main.comboBox_host.currentText() != 'localhost':
            self.conection_message = f'* Imposible to connect with remote Kafka on "{self.main.comboBox_host.currentText()}".'
        else:
            self.conection_message = '* Kafka is not running on this machine.'

    # ----------------------------------------------------------------------
    def show_configurations(self, event=None):
        """"""
        configuration = ConfigurationFrame(self)
        configuration.show()
