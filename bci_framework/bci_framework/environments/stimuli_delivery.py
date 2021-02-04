import os
import socket
import sys
import webbrowser

from PySide2.QtCore import QTimer
from PySide2.QtUiTools import QUiLoader

from ..stream_handler import VisualizationWidget


########################################################################
class StimuliDelivery:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, core):
        """Constructor"""

        self.parent_frame = core.main
        self.core = core
        self.connect()

    # ----------------------------------------------------------------------
    def on_focus(self):
        """"""
        self.stimuli_list = []
        self.update_experiments_list()

        self.parent_frame.mdiArea_stimuli.tileSubWindows()

        if not self.parent_frame.mdiArea_stimuli.subWindowList():
            self.build_dashboard()

    # ----------------------------------------------------------------------
    def build_dashboard(self):
        """"""
        sub = VisualizationWidget(
            self.parent_frame.mdiArea_stimuli, self.stimuli_list, mode='stimuli')
        self.parent_frame.mdiArea_stimuli.addSubWindow(sub)
        sub.show()
        self.parent_frame.mdiArea_stimuli.tileSubWindows()

        sub.update_ip = self.update_ip
        sub.update_menu_bar()
        sub.loaded = self.widgets_set_enabled

        QTimer().singleShot(100, self.widgets_set_enabled)

    # ----------------------------------------------------------------------
    def update_experiments_list(self):
        """"""
        for i in range(self.parent_frame.listWidget_projects_delivery.count()):
            item = self.parent_frame.listWidget_projects_delivery.item(i)

            if item.text().startswith('_'):
                continue

            if item.text().startswith('Tutorial |'):
                continue

            self.stimuli_list.append(item.text())

    # ----------------------------------------------------------------------
    def connect(self):
        """"""
        self.parent_frame.pushButton_stimuli_browser.clicked.connect(
            self.open_browser)
        self.parent_frame.pushButton_stimuli_subwindow.clicked.connect(
            self.open_subwindow)

    # ----------------------------------------------------------------------
    def get_local_ip_address(self):
        """Connect to internet for get the local IP."""
        try:
            local_ip_address = socket.gethostbyname(socket.gethostname())
            return local_ip_address
        except:
            return 'localhost'

    # ----------------------------------------------------------------------
    def open_browser(self):
        """"""
        webbrowser.open_new_tab(
            self.parent_frame.lineEdit_stimuli_ip.text())

    # ----------------------------------------------------------------------
    def open_subwindow(self, url=None):
        """"""
        if not url:
            url = self.parent_frame.lineEdit_stimuli_ip.text()

        if not url:
            return

        if not hasattr(self, 'sub_window_delivery'):
            frame = os.path.join(
                os.environ['BCISTREAM_ROOT'], 'bci_framework', 'qtgui', 'stimuli_delivery.ui')
            self.sub_window_delivery = QUiLoader().load(frame, self.parent_frame)

        self.sub_window_delivery.show()

        if url.startswith('http://'):
            self.sub_window_delivery.webEngineView.setUrl(url)
        else:
            self.sub_window_delivery.webEngineView.setUrl(f'http://{url}/')

    # ----------------------------------------------------------------------
    def widgets_set_enabled(self):
        """"""
        if subwindows := self.parent_frame.mdiArea_stimuli.subWindowList():
            sub = subwindows[0]
            enabled = hasattr(sub, 'stream_subprocess')
        else:
            enabled = False

        self.parent_frame.lineEdit_stimuli_ip.setEnabled(enabled)
        self.parent_frame.pushButton_stimuli_browser.setEnabled(enabled)
        self.parent_frame.pushButton_stimuli_subwindow.setEnabled(enabled)

    # ----------------------------------------------------------------------
    def update_ip(self, port):
        """"""
        self.parent_frame.lineEdit_stimuli_ip.setText(
            f'{self.get_local_ip_address()}:{port}')
