"""
====
Core
====
"""

import os
import sys
import time
import json
import psutil
import pickle
import platform
import subprocess
from datetime import datetime
from typing import TypeVar, Optional

from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt, QTimer, QSize, Signal, QThread, Slot
from PySide6.QtGui import QPixmap, QIcon, QFontDatabase, QKeySequence, QShortcut
from PySide6.QtWidgets import QWidget, QMainWindow, QPushButton, QLabel, QCheckBox

from kafka import KafkaProducer, KafkaConsumer
import ntplib

from .widgets import Montage, Projects, Connection, Records, Annotations
from .environments import Development, Visualization, StimuliDelivery, TimeLockAnalysis
from .config_manager import ConfigManager
from .configuration import ConfigurationFrame
from .subprocess_handler import run_subprocess
from .raspad import Raspad

KafkaMessage = TypeVar('KafkaMessage')
PathLike = TypeVar('PathLike')
HostLike = TypeVar('HostLike')
Millis = TypeVar('Milliseconds')


########################################################################
class ClockOffset(QThread):
    """"""
    signal_offset = Signal(object)

    # ----------------------------------------------------------------------
    def set_host(self, host: HostLike) -> None:
        """Set the host for kafka."""
        self.host = host

    # ----------------------------------------------------------------------
    def run(self) -> None:
        """"""
        try:
            client = ntplib.NTPClient()
            r = client.request(self.host)
            clock_offset = r.offset  # * 1000
            self.signal_offset.emit(clock_offset)
            print(f'offset: {clock_offset}')
        except Exception:
            pass


########################################################################
class Kafka(QThread):
    """Kafka run on a thread."""
    signal_kafka_message = Signal(object)
    signal_exception_message = Signal()
    signal_produser = Signal()
    keep_alive = True

    # ----------------------------------------------------------------------
    def set_host(self, host: HostLike) -> None:
        """Set the host for kafka."""
        self.host = host

    # ----------------------------------------------------------------------
    def stop(self) -> None:
        """Kill the thread."""
        self.keep_alive = False
        self.terminate()

    # ----------------------------------------------------------------------
    def run(self) -> None:
        """Start the produser and consumer for Kafka."""
        try:
            self.create_produser()
            self.signal_produser.emit()
            self.consumed = False
            self.create_consumer()
        except Exception:
            self.signal_exception_message.emit()
            self.stop()

    # ----------------------------------------------------------------------
    def create_consumer(self) -> None:
        """Basic consumer to check stream status and availability."""
        bootstrap_servers = [f'{self.host}:9092']
        topics = ['annotation', 'marker',
                  'command', 'eeg', 'aux', 'feedback']
        self.consumer = KafkaConsumer(bootstrap_servers=bootstrap_servers,
                                      value_deserializer=pickle.loads,
                                      auto_offset_reset='latest',
                                      )

        self.consumer.subscribe(topics)
        for message in self.consumer:
            self.last_message = datetime.now()
            message.value['timestamp'] = message.timestamp / 1000

            self.signal_kafka_message.emit(
                {'topic': message.topic, 'value': message.value})

            if not self.keep_alive:
                return

    # ----------------------------------------------------------------------
    def create_produser(self) -> None:
        """The produser is used for stream annotations and markers."""
        self.produser = KafkaProducer(bootstrap_servers=[f'{self.host}:9092'],
                                      compression_type='gzip',
                                      value_serializer=pickle.dumps,
                                      )


########################################################################
class BCIFramework(QMainWindow):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.load_fonts()
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
        self.main.actionTimelock_analysis.triggered.connect(
            lambda evt: self.show_interface('Timelock_analysis'))
        self.main.actionHome.triggered.connect(
            lambda evt: self.show_interface('Home'))
        self.main.actionDocumentation.triggered.connect(
            lambda evt: self.show_interface('Documentation'))
        self.main.actionRaspad_settings.triggered.connect(
            lambda evt: self.show_interface('Raspad_settings'))

        self.main.stackedWidget_montage.setCurrentWidget(
            self.main.page_montage)

        self.show_interface('Home')
        self.config = ConfigManager()

        for i in range(self.main.toolBar_Environs.layout().count()):
            tool_button = self.main.toolBar_Environs.layout().itemAt(i).widget()
            tool_button.setMaximumWidth(200)
            tool_button.setMinimumWidth(200)

        self.set_editor()
        self.build_collapse_button()

        self.montage = Montage(self)
        self.connection = Connection(self)
        self.projects = Projects(self.main, self)
        self.records = Records(self.main, self)
        self.annotations = Annotations(self.main, self)
        self.raspad = Raspad(self)

        self.development = Development(self)
        self.visualizations = Visualization(self)
        self.stimuli_delivery = StimuliDelivery(self)
        self.timelock_analysis = TimeLockAnalysis(self)

        # self.status_bar('OpenBCI no connected')

        self.main.tabWidget_widgets.setCurrentIndex(0)
        self.main.tabWidget_data_analysis.setCurrentIndex(0)
        self.main.tabWidget_stimuli_delivery.setCurrentIndex(0)
        self.style_home_page()

        self.connect()

        docs = os.path.abspath(os.path.join(os.environ.get(
            'BCISTREAM_ROOT'), 'documentation', 'index.html'))
        self.main.webEngineView_documentation.setUrl(f'file://{docs}')

        self.subprocess_timer = QTimer()
        self.subprocess_timer.timeout.connect(self.save_subprocess)
        self.subprocess_timer.setInterval(5000)
        self.subprocess_timer.start()

        self.clock_offset = 0
        self.eeg_size = 0
        self.aux_size = 0
        self.sample_rate = 0
        self.last_update = 0

        # QTimer().singleShot(1000, self.calculate_offset)
        QTimer().singleShot(3000, self.start_stimuli_server)

        self.status_bar(message='', right_message=('disconnected', None))

        shortcut_fullscreen = QShortcut(QKeySequence('F11'), self.main)
        shortcut_fullscreen.activated.connect(lambda: self.main.showMaximized(
        ) if self.main.windowState() & Qt.WindowFullScreen else self.main.showFullScreen())

        shortcut_docs = QShortcut(QKeySequence('F1'), self.main)
        shortcut_docs.activated.connect(
            lambda: self.show_interface('Documentation'))

        shortcut_docs = QShortcut(QKeySequence('F2'), self.main)
        shortcut_docs.activated.connect(self.toggle_dock_collapsed)

        shortcut_docs = QShortcut(QKeySequence('F9'), self.main)
        shortcut_docs.activated.connect(
            self.timelock_analysis.show_fullscreen)

        self.main.toolBar_Environs.setStyleSheet("""
          * {
          min-width: 200px;
          }
          """)

    # ----------------------------------------------------------------------
    def set_icons(self) -> None:
        """The Qt resource system has been deprecated."""
        def icon(name):
            return QIcon(f"bci:/primary/{name}.svg")

        self.main.actionDevelopment.setIcon(icon("file"))
        self.main.actionVisualizations.setIcon(icon("latency2"))
        self.main.actionStimuli_delivery.setIcon(icon("imagery"))
        self.main.actionTimelock_analysis.setIcon(icon("brain"))
        self.main.actionHome.setIcon(icon("home"))
        self.main.actionDocumentation.setIcon(icon("documentation"))

        if json.loads(os.getenv('BCISTREAM_RASPAD')):
            self.main.actionRaspad_settings.setIcon(icon("brain_settings"))
        else:
            self.main.actionRaspad_settings.setVisible(False)

        self.main.pushButton_file.setIcon(icon("file"))
        self.main.pushButton_brain.setIcon(icon("brain"))
        self.main.pushButton_imagery.setIcon(icon("imagery"))
        self.main.pushButton_docs.setIcon(icon("documentation"))
        self.main.pushButton_latency.setIcon(icon("latency"))
        self.main.pushButton_annotations.setIcon(icon("annotation"))
        self.main.pushButton_timelock.setIcon(icon("latency2"))

        self.main.pushButton_stop_preview.setIcon(
            icon('media-playback-stop'))
        self.main.pushButton_script_preview.setIcon(
            icon('media-playback-start'))
        self.main.pushButton_play_signal.setIcon(
            icon('media-playback-start'))
        self.main.pushButton_clear_debug.setIcon(icon('edit-delete'))
        self.main.pushButton_remove_record.setIcon(icon('edit-delete'))
        self.main.pushButton_remove_annotations.setIcon(icon('edit-delete'))
        self.main.pushButton_remove_markers.setIcon(icon('edit-delete'))
        self.main.pushButton_remove_commands.setIcon(icon('edit-delete'))
        self.main.pushButton_record.setIcon(icon('media-record'))

        self.main.pushButton_projects_add_file.setIcon(icon('document-new'))
        self.main.pushButton_projects_add_folder.setIcon(icon('folder-add'))
        self.main.pushButton_add_project.setIcon(icon('folder-add'))
        self.main.pushButton_projects_remove.setIcon(icon('edit-delete'))
        self.main.pushButton_remove_project.setIcon(icon('edit-delete'))
        self.main.pushButton_remove_montage.setIcon(icon('edit-delete'))

        self.main.pushButton_projects.setIcon(icon('go-previous'))
        self.main.pushButton_load_visualizarion.setIcon(icon('list-add'))

        self.main.pushButton_open_records_folder.setIcon(icon('folder'))
        self.main.pushButton_open_extension_folder.setIcon(icon('folder'))

        for i in range(1, 5):
            getattr(self.main, f'pushButton_update_wifi{i}').setIcon(
                icon('gtk-convert'))

        self.main.setWindowIcon(icon("logo"))

    # ----------------------------------------------------------------------
    def save_subprocess(self) -> None:
        """Save in a file all the child subprocess."""
        current_process = psutil.Process()
        children = current_process.children(recursive=True)
        children.append(current_process)
        file = os.path.join(os.environ['BCISTREAM_HOME'], '.subprocess')
        try:
            with open(file, 'w') as file_:
                json.dump({ch.pid: ch.name()
                           for ch in children}, file_, indent=2)
        except:  # psutil.NoSuchProcess: psutil.NoSuchProcess process no longer exists
            pass

    # ----------------------------------------------------------------------
    def load_fonts(self) -> None:
        """Load custom fonts."""
        fonts_path = os.path.join(
            os.environ['BCISTREAM_ROOT'], 'assets', 'fonts')

        for font_dir in [os.path.join('dejavu', 'ttf')]:
            for font in filter(lambda s: s.endswith('.ttf'), os.listdir(os.path.join(fonts_path, font_dir))):
                QFontDatabase.addApplicationFont(
                    os.path.join(fonts_path, font_dir, font))

    # ----------------------------------------------------------------------
    def build_collapse_button(self) -> None:
        """Custom collapsible widgets area."""
        # This dockWidget has empy name so,
        # with in that space is possible to add a custom widget
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
    def set_dock_collapsed(self, collapsed: bool) -> None:
        """Collapse widgets area."""
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
            self.main.dockWidget_global.setMaximumWidth(w * 99)
            self.main.dockWidget_global.setMinimumWidth(0)

    # ----------------------------------------------------------------------
    def toggle_dock_collapsed(self) -> None:
        """"""
        if self.main.dockWidget_global.maximumWidth() < 100:
            self.set_dock_collapsed(False)
        else:
            self.set_dock_collapsed(True)

    # ----------------------------------------------------------------------
    def connect(self) -> None:
        """Connect events."""
        self.main.tabWidget_widgets.currentChanged.connect(
            lambda: self.set_dock_collapsed(False))

        self.main.pushButton_add_project_2.clicked.connect(
            self.projects.show_create_project_dialog)

        self.main.pushButton_show_visualization.clicked.connect(
            lambda evt: self.show_interface('Visualizations'))
        self.main.pushButton_show_stimuli_delivery.clicked.connect(
            lambda evt: self.show_interface('Stimuli_delivery', 0))
        self.main.pushButton_show_timelock.clicked.connect(
            lambda evt: self.show_interface('Timelock_analysis', 0))

        self.main.pushButton_show_documentation.clicked.connect(
            lambda evt: self.show_interface('Documentation'))

        self.main.pushButton_show_about.clicked.connect(self.show_about)
        self.main.pushButton_show_configurations.clicked.connect(
            self.show_configurations)

        self.main.pushButton_show_latency_correction.clicked.connect(
            lambda evt: self.show_interface('Stimuli_delivery', 1))

        self.main.pushButton_show_annotations.clicked.connect(
            lambda evt: self.main.tabWidget_widgets.setCurrentIndex(3))

        self.main.tabWidget_widgets.currentChanged.connect(self.show_widget)

        self.main.pushButton_open_extension_folder.clicked.connect(
            lambda: self.open_folder_in_system(self.main.label_projects_path.text()))
        self.main.pushButton_open_records_folder.clicked.connect(
            lambda: self.open_folder_in_system(self.main.label_records_path.text()))

        self.main.checkBox_board1.toggled.connect(
            lambda checked: not checked and self.main.checkBox_board1.setChecked(True))
        # self.main.checkBox_board1.toggled.connect(
            # lambda b: self.board_handle(self.main.checkBox_board2, b))
        self.main.checkBox_board2.toggled.connect(
            lambda b: self.board_handle(self.main.checkBox_board3, b))
        self.main.checkBox_board3.toggled.connect(
            lambda b: self.board_handle(self.main.checkBox_board4, b))

    # ----------------------------------------------------------------------
    def board_handle(self, chbox: QCheckBox, enable: bool) -> None:
        """"""
        chbox.setEnabled(enable)
        chbox.setChecked(False)

    # ----------------------------------------------------------------------
    def open_folder_in_system(self, path: PathLike) -> None:
        """"""
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    # ----------------------------------------------------------------------
    def show_interface(self, interface: str, sub_widget: Optional[int] = None) -> None:
        """Switch between environs."""
        self.main.stackedWidget_modes.setCurrentWidget(
            getattr(self.main, f"page{interface}"))
        for action in self.main.toolBar_Environs.actions():
            action.setChecked(False)
        for action in self.main.toolBar_Documentation.actions():
            action.setChecked(False)
        if action := getattr(self.main, f"action{interface}", False):
            action.setChecked(True)

        if mod := getattr(self, f'{interface.lower().replace(" ", "_")}', False):
            if on_focus := getattr(mod, 'on_focus'):
                on_focus()

        if sub_widget != None:
            if interface == 'Stimuli_delivery':
                self.main.tabWidget_stimuli_delivery.setCurrentIndex(
                    sub_widget)

    # ----------------------------------------------------------------------
    def show_widget(self, index: int) -> None:
        """Call `on_focus` method for all widgets."""
        widget = self.main.tabWidget_widgets.tabText(index)
        if wg := getattr(self, widget.lower(), False):
            if on_focus := getattr(wg, 'on_focus', False):
                on_focus()

    # ----------------------------------------------------------------------
    def set_editor(self) -> None:
        """Change some styles."""
        self.main.plainTextEdit_preview_log.setStyleSheet("""
        *{
        font-weight: normal;
        font-family: 'DejaVu Sans Mono';
        }
        """)

        self.main.mdiArea.setStyleSheet(f"""
        *{{
        background: {os.environ.get('QTMATERIAL_SECONDARYDARKCOLOR')};
        }}
        """)

    # # ----------------------------------------------------------------------
    # def remove_widgets_from_layout(self, layout) -> None:
        # """"""
        # for i in reversed(range(layout.count())):
        # if item := layout.takeAt(i):
        # item.widget().deleteLater()

    # ----------------------------------------------------------------------
    def status_bar(self, message: Optional[str] = None, right_message: Optional[str] = None) -> None:
        """Update messages for status bar."""
        statusbar = self.main.statusBar()

        if not hasattr(statusbar, 'right_label'):
            statusbar.right_label = QLabel(statusbar)
            statusbar.right_label.setAlignment(Qt.AlignRight)
            statusbar.right_label.mousePressEvent = lambda evt: self.main.tabWidget_widgets.setCurrentWidget(
                self.main.tab_connection)
            statusbar.addPermanentWidget(statusbar.right_label)

            statusbar.btn = QPushButton()
            statusbar.btn.setProperty('class', 'connection')
            statusbar.btn.blockSignals(True)
            statusbar.addPermanentWidget(statusbar.btn)

        if message:
            statusbar.showMessage(message)

        if right_message:
            # statusbar.btn.blockSignals(False)
            message, status = right_message
            statusbar.right_label.setText(message)
            if status is None:
                statusbar.btn.setDisabled(True)
                if 'light' in os.environ.get('QTMATERIAL_THEME'):
                    statusbar.btn.setStyleSheet(f"""*{{
                    border: 1px solid {os.environ.get('QTMATERIAL_SECONDARYDARKCOLOR')};
                    background-color: {os.environ.get('QTMATERIAL_SECONDARYDARKCOLOR')};}}""")
                else:
                    statusbar.btn.setStyleSheet(f"""*{{
                    border: 1px solid {os.environ.get('QTMATERIAL_SECONDARYLIGHTCOLOR')};
                    background-color: {os.environ.get('QTMATERIAL_SECONDARYLIGHTCOLOR')};}}""")
            else:
                statusbar.btn.setDisabled(False)
                if status:
                    statusbar.btn.setStyleSheet("""*{
                      border: 1px solid #3fc55e;
                    background-color: #3fc55e;}""")
                else:
                    statusbar.btn.setStyleSheet("""*{
                      border: 1px solid #dc3545;
                    background-color: #dc3545;}""")

    # ----------------------------------------------------------------------
    def style_home_page(self) -> None:
        """Set the styles for home page."""

        if json.loads(os.getenv('BCISTREAM_RASPAD')):
            size = 50
            version = 'RASPAD'
        else:
            size = 80
            version = ''

        if '--local' in sys.argv:
            mode = 'DEBUG'
        else:
            mode = ''

        style = f"""
        *{{
        width:      {size}px;
        height:     {size}px;
        max-width:  {size}px;
        min-width:  {size}px;
        max-height: {size}px;
        min-height: {size}px;
        background-color: {os.environ.get('secondaryColor')}
        }}
        """
        self.main.pushButton_file.setStyleSheet(style)
        self.main.pushButton_brain.setStyleSheet(style)
        self.main.pushButton_imagery.setStyleSheet(style)
        self.main.pushButton_docs.setStyleSheet(style)
        self.main.pushButton_latency.setStyleSheet(style)
        self.main.pushButton_annotations.setStyleSheet(style)
        self.main.pushButton_timelock.setStyleSheet(style)

        style = f"""
        QFrame {{
        background-color: {os.environ.get('secondaryColor')}
        }}
        """
        self.main.frame_3.setStyleSheet(style)
        self.main.frame_2.setStyleSheet(style)
        self.main.frame_5.setStyleSheet(style)
        self.main.frame_6.setStyleSheet(style)
        self.main.frame_7.setStyleSheet(style)
        self.main.frame_4.setStyleSheet(style)
        self.main.frame.setStyleSheet(style)

        style = """
        *{
        color: black;
        }
        """

        # FONTSIZE
        labels = [self.main.label_15, self.main.label_16, self.main.label_17,
                  self.main.label_20, self.main.label_21, self.main.label_22,
                  self.main.label_23]
        for label in labels:
            if json.loads(os.getenv('BCISTREAM_RASPAD')):
                label.setText(label.text().replace(
                    'font-size:12pt', 'font-size:10pt'))

        with open(os.path.join(os.environ['BCISTREAM_ROOT'], '_version.txt'), 'r') as file:
            self.main.label_software_version.setText(
                f'{file.read().strip()} {version} {mode}')

    # ----------------------------------------------------------------------
    def show_about(self, *args, **wargs) -> None:
        """Display about window."""
        frame = os.path.join(
            os.environ['BCISTREAM_ROOT'], 'framework', 'qtgui', 'about.ui')
        about = QUiLoader().load(frame, self.main)
        about.label.setScaledContents(True)

        about.pushButton_close.clicked.connect(
            lambda evt: about.destroy())

        about.label.setMinimumSize(QSize(600, 200))
        about.label.setMaximumSize(QSize(600, 200))

        banner = os.path.join(
            os.environ['BCISTREAM_ROOT'], 'assets', 'banner.png')
        about.label.setPixmap(QPixmap(banner))

        about.tabWidget.setCurrentIndex(0)

        about.setStyleSheet(f"""
        QPlainTextEdit {{
        font-weight: normal;
        font-family: 'DejaVu Sans Mono';
        font-size: 13px;
        }}

        QTextEdit {{
        color: {os.environ.get('QTMATERIAL_SECONDARYTEXTCOLOR')};
        }}
        """)

        center = QWidget.screen(self).availableGeometry().center()
        geometry = about.frameGeometry()
        geometry.moveCenter(center)
        about.move(geometry.topLeft())

        about.show()

    # ----------------------------------------------------------------------
    @Slot()
    def on_kafka_event(self, value: KafkaMessage) -> None:
        """Register annotations and markers."""

        self.streaming = True

        if value['topic'] == 'marker':
            self.annotations.add_marker(datetime.fromtimestamp(
                value['value']['timestamp']), value['value']['marker'])
        elif value['topic'] == 'command':
            self.annotations.add_command(datetime.fromtimestamp(
                value['value']['timestamp']), value['value']['command'])
        elif value['topic'] == 'annotation':
            self.annotations.add_annotation(datetime.fromtimestamp(value['value']['timestamp']),
                                            value['value']['duration'],
                                            value['value']['description'])
        elif value['topic'] == 'feedback':
            self.handle_feedback(value['value'])

        elif value['topic'] in ['eeg', 'aux']:

            if time.time() < self.last_update + 1:
                return
            self.last_update = time.time()

            # Use only remote times to make the calculation, so the
            # differents clocks not affect the measure
            binary_created = datetime.fromtimestamp(
                min(value['value']['context']['timestamp.binary']))
            message_created = datetime.fromtimestamp(
                value['value']['timestamp'])
            since = (message_created - binary_created).total_seconds()
            if value['topic'] == 'eeg':
                self.eeg_size = value['value']['data'].shape
            elif value['topic'] == 'aux':
                self.aux_size = value['value']['data'].shape

            if since * 1000 > 2000:
                color = '#ffc107'  # old data
            else:
                color = '#3fc55e'  # recent data

            message = f'Last package streamed <b style="color:{color};">{since*1000:0.2f} ms </b> ago | EEG{self.eeg_size} | AUX{self.aux_size}'

            if status := getattr(self.records, 'recording_status', None):
                message += f' | <b style="color:#dc3545;">{status}</b>'

            self.status_bar(right_message=(message, True))
            # self.last_update = value['value']['timestamp']

    # ----------------------------------------------------------------------
    def update_kafka(self, host: HostLike) -> None:
        """Try to restart kafka services."""
        if hasattr(self, 'thread_kafka'):
            self.thread_kafka.stop()
            self.status_bar(right_message=('No streaming', False))
        # try:
        self.thread_kafka = Kafka()
        self.thread_kafka.signal_kafka_message.connect(self.on_kafka_event)
        # self.thread_kafka.first_consume.connect(lambda: self.connection.on_connect(
            # True))
        self.thread_kafka.signal_exception_message.connect(
            self.kafka_message)
        self.thread_kafka.signal_produser.connect(
            self.kafka_produser_connected)
        self.thread_kafka.set_host(host)
        self.thread_kafka.start()

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.keep_updated)
        self.timer.start()

    # ----------------------------------------------------------------------
    def calculate_offset(self) -> None:
        """"""
        host = self.thread_kafka.host
        if host != 'localhost':
            self.offset_thread = ClockOffset()
            self.offset_thread.signal_offset.connect(self.set_offset)
            self.offset_thread.set_host(self.thread_kafka.host)
            self.offset_thread.start()
        else:
            self.set_offset(0)

    # ----------------------------------------------------------------------
    def set_offset(self, offset: Millis) -> None:
        """"""
        os.environ['BCISTREAM_OFFSET'] = json.dumps(offset)

    # ----------------------------------------------------------------------
    def stop_kafka(self) -> None:
        """Stop kafka."""
        self.streaming = False
        if hasattr(self, 'thread_kafka'):
            self.thread_kafka.stop()
            self.status_bar(right_message=('No streaming', False))

    # ----------------------------------------------------------------------
    def keep_updated(self) -> None:
        """The status is update each 3 seconds."""
        if hasattr(self, 'thread_kafka') and hasattr(self.thread_kafka, 'last_message'):
            last = datetime.now() - self.thread_kafka.last_message
            if last.seconds > 3:
                self.status_bar(right_message=('No streaming', False))
                self.annotations.set_enable(False)
                self.main.pushButton_record.setEnabled(False)
                self.streaming = False
            else:
                self.annotations.set_enable(True)
                self.main.pushButton_record.setEnabled(True)

    # ----------------------------------------------------------------------
    @Slot()
    def kafka_message(self) -> None:
        """Error on kafka."""
        self.streaming = False
        if self.main.comboBox_host.currentText() != 'localhost':
            self.conection_message = f'* Imposible to connect with remote Kafka on "{self.main.comboBox_host.currentText()}".'
        else:
            self.conection_message = '* Kafka is not running on this machine.'

        self.status_bar(right_message=('Disconnected', None))

    # ----------------------------------------------------------------------
    @Slot()
    def kafka_produser_connected(self) -> None:
        """If produser connected is posible the consumer too."""
        self.status_bar(right_message=('Connected', False))

    # ----------------------------------------------------------------------
    def show_configurations(self, *args, **kwargs) -> None:
        """Show configuration window."""
        configuration = ConfigurationFrame(self)
        configuration.show()

    # ----------------------------------------------------------------------
    def handle_feedback(self, data) -> None:
        """"""
        if fn := getattr(self, f"feedback_{data['name']}", False):
            fn(data['value'])

    # ----------------------------------------------------------------------
    def feedback_set_latency(self, latency: Millis) -> None:
        """"""
        os.environ['BCISTREAM_SYNCLATENCY'] = json.dumps(latency)

    # ----------------------------------------------------------------------
    def start_stimuli_server(self) -> None:
        """"""
        if '--local' in sys.argv:
            self.bciframework_server = run_subprocess([sys.executable, os.path.join(
                os.environ['BCISTREAM_ROOT'], 'python_scripts', 'bciframework_server', 'main.py')])
        else:
            self.bciframework_server = run_subprocess([sys.executable, os.path.join(
                os.environ['BCISTREAM_HOME'], 'python_scripts', 'bciframework_server', 'main.py')])
