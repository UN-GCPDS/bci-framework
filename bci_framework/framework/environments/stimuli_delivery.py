"""
================
Stimuli Delivery
================

Run an experiment in a dedicated space, without debugger or code editor.
"""

import os
import socket
import webbrowser
import logging
import sys
import json

from PySide2.QtCore import QTimer, Qt
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QPixmap, QKeySequence
from PySide2.QtWidgets import QShortcut

from ..extensions_handler import ExtensionWidget
from ..subprocess_handler import run_subprocess

import socket
from contextlib import closing

DEFAULT_LOCAL_IP = 'localhost'


########################################################################
class StimuliDelivery:
    """Dashboard for experiments executions."""

    # ----------------------------------------------------------------------
    def __init__(self, core):
        """Constructor"""

        self.parent_frame = core.main
        self.core = core

        self.parent_frame.pushButton_stop_calibration.setVisible(False)
        self.parent_frame.mdiArea_latency.hide()
        self.parent_frame.label_calibration_image.show()

        self.connect()

    # ----------------------------------------------------------------------
    def on_focus(self) -> None:
        """Update mdiAreas."""
        self.stimuli_list = []
        self.update_experiments_list()

        self.parent_frame.mdiArea_stimuli.tileSubWindows()
        self.parent_frame.mdiArea_latency.tileSubWindows()

        if not self.parent_frame.mdiArea_stimuli.subWindowList():
            self.build_dashboard()

    # ----------------------------------------------------------------------
    def build_dashboard(self) -> None:
        """Create the experiments selector."""
        sub = ExtensionWidget(
            self.parent_frame.mdiArea_stimuli, extensions_list=self.stimuli_list, mode='stimuli')
        self.parent_frame.mdiArea_stimuli.addSubWindow(sub)
        sub.show()
        self.parent_frame.mdiArea_stimuli.tileSubWindows()

        sub.update_ip = self.update_ip
        sub.update_menu_bar()
        sub.loaded = self.widgets_set_enabled

        QTimer().singleShot(100, self.widgets_set_enabled)

    # ----------------------------------------------------------------------
    def update_experiments_list(self) -> None:
        """Update the experiments selector."""
        for i in range(self.parent_frame.listWidget_projects_delivery.count()):
            item = self.parent_frame.listWidget_projects_delivery.item(i)
            if item.text().startswith('_'):
                continue
            if item.text().startswith('Tutorial :'):
                continue
            self.stimuli_list.append([item.text(), item.path])

    # ----------------------------------------------------------------------
    def connect(self) -> None:
        """Connect events."""
        self.parent_frame.pushButton_stimuli_browser.clicked.connect(
            self.open_browser)
        self.parent_frame.pushButton_stimuli_subwindow.clicked.connect(
            self.open_subwindow)

        # self.parent_frame.pushButton_stimuli_browser_lat.clicked.connect(
            # self.open_browser)
        # self.parent_frame.pushButton_stimuli_subwindow_lat.clicked.connect(
            # self.open_subwindow)

        self.parent_frame.pushButton_start_calibration.clicked.connect(
            self.start_calibration)
        self.parent_frame.pushButton_stop_calibration.clicked.connect(
            self.stop_calibration)

    # ----------------------------------------------------------------------
    def get_local_ip_address(self) -> str:
        """Connect to internet for get the local IP."""

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip_address = s.getsockname()[0]
            s.close()
            return local_ip_address

        except:
            logging.warning('Impossible to detect a network connection, the WiFi'
                            'module and this machine must share the same network.')
            logging.warning(f'If you are using this machine as server (access point) '
                            f'the address {DEFAULT_LOCAL_IP} will be used.')

            return DEFAULT_LOCAL_IP

    # ----------------------------------------------------------------------
    def open_browser(self) -> None:
        """Open delivery on browser."""

        if address := self.parent_frame.lineEdit_stimuli_ip.text():
            webbrowser.open_new_tab(address)
        # elif address := self.parent_frame.lineEdit_stimuli_ip_lat.text():
            # webbrowser.open_new_tab(address)

    # ----------------------------------------------------------------------
    def open_subwindow(self, url=None) -> None:
        """Open an auxiliar window for stimuli delivery."""
        if not url:
            # url = self.parent_frame.lineEdit_stimuli_ip.text()
            if address := self.parent_frame.lineEdit_stimuli_ip.text():
                url = address
            # elif address := self.parent_frame.lineEdit_stimuli_ip_lat.text():
                # url = address

        if not url:
            return

        if not hasattr(self, 'sub_window_delivery'):
            frame = os.path.join(
                os.environ['BCISTREAM_ROOT'], 'framework', 'qtgui', 'stimuli_delivery_subwindow.ui')
            self.sub_window_delivery = QUiLoader().load(frame, self.parent_frame)

            shortcut_fullscreen = QShortcut(
                QKeySequence('F11'), self.sub_window_delivery)
            shortcut_fullscreen.activated.connect(lambda: self.sub_window_delivery.showNormal() if self.sub_window_delivery.windowState(
            ) & Qt.WindowFullScreen else self.sub_window_delivery.showFullScreen())

        self.sub_window_delivery.show()

        if url.startswith('http://'):
            self.sub_window_delivery.webEngineView.setUrl(url)
        else:
            self.sub_window_delivery.webEngineView.setUrl(f'http://{url}/')

    # ----------------------------------------------------------------------
    def widgets_set_enabled(self) -> None:
        """Update action buttons."""
        if subwindows := self.parent_frame.mdiArea_stimuli.subWindowList():
            sub = subwindows[0]
            enabled = hasattr(sub, 'stream_subprocess')
        else:
            enabled = False

        if not enabled:
            self.parent_frame.lineEdit_stimuli_ip.setText('')
        self.parent_frame.lineEdit_stimuli_ip.setEnabled(enabled)
        self.parent_frame.pushButton_stimuli_browser.setEnabled(enabled)
        self.parent_frame.pushButton_stimuli_subwindow.setEnabled(enabled)

    # ----------------------------------------------------------------------
    def update_ip(self, port) -> None:
        """Update the QLineEdit with the current ip address."""
        self.parent_frame.lineEdit_stimuli_ip.setText(
            f'{self.get_local_ip_address()}:{port}')

    # ----------------------------------------------------------------------
    def start_calibration(self):
        """"""
        self.parent_frame.label_calibration_image.hide()
        self.parent_frame.mdiArea_latency.show()
        os.environ['BCISTREAM_SYNCLATENCY'] = json.dumps(0)
        kafka_scripts_dir = os.path.join(
            os.environ['BCISTREAM_ROOT'], 'kafka_scripts')

        # port_viz = self.get_free_port()
        # self.latency_calibration = run_subprocess([sys.executable, os.path.join(
            # kafka_scripts_dir, 'latency_synchronization_stimuli_marker', 'main.py'), port_viz])

        if not hasattr(self, 'latency_visualization'):
            self.latency_visualization = ExtensionWidget(
                self.parent_frame.mdiArea_latency, mode='visualization',
                autostart='latency_synchronization_visualization', hide_menu=True, directory=kafka_scripts_dir)
            self.parent_frame.mdiArea_latency.addSubWindow(
                self.latency_visualization)
        else:
            self.latency_visualization.load_extension(
                'latency_synchronization_visualization')

        self.latency_visualization.show()
        self.parent_frame.mdiArea_latency.tileSubWindows()
        # self.latency_visualization.update_menu_bar()

        # self.parent_frame.lineEdit_stimuli_ip_lat.setText(
            # f'{self.get_local_ip_address()}:{port_viz}')
        # self.parent_frame.lineEdit_stimuli_ip_lat.setEnabled(True)
        # self.parent_frame.pushButton_stimuli_browser_lat.setEnabled(True)
        # self.parent_frame.pushButton_stimuli_subwindow_lat.setEnabled(True)
        self.parent_frame.pushButton_start_calibration.setVisible(False)
        self.parent_frame.pushButton_stop_calibration.setVisible(True)

    # ----------------------------------------------------------------------
    def stop_calibration(self):
        """"""
        capture = self.latency_visualization.save_img('last_calibration.jpg')
        self.parent_frame.label_calibration_image.setPixmap(QPixmap(capture))

        self.latency_visualization.stop_preview()
        # self.latency_calibration.terminate()

        self.parent_frame.mdiArea_latency.hide()
        self.parent_frame.label_calibration_image.show()

        # self.parent_frame.lineEdit_stimuli_ip_lat.setText('')
        # self.parent_frame.lineEdit_stimuli_ip_lat.setEnabled(False)
        # self.parent_frame.pushButton_stimuli_browser_lat.setEnabled(False)
        # self.parent_frame.pushButton_stimuli_subwindow_lat.setEnabled(False)
        self.parent_frame.pushButton_start_calibration.setVisible(True)
        self.parent_frame.pushButton_stop_calibration.setVisible(False)

    # ----------------------------------------------------------------------
    def get_free_port(self) -> str:
        """Get any free port available."""
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind(('', 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            port = str(s.getsockname()[1])
            logging.info(f'Free port found in {port}')
            return port
