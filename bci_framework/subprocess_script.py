"""
"""


import os
import sys
import socket
import logging
import subprocess
from urllib import request
from contextlib import closing

from PySide2.QtCore import QTimer, Qt
from PySide2.QtGui import QPixmap
from PySide2.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

from bci_framework.environments.development.nbstreamreader import NonBlockingStreamReader as NBSR


# ----------------------------------------------------------------------
def run_subprocess(call):
    """"""
    my_env = os.environ.copy()
    my_env['PYTHONPATH'] = ":".join(sys.path)

    return subprocess.Popen(call,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            env=my_env,
                            )


########################################################################
class JavaScriptConsole:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.message = ""

    # ----------------------------------------------------------------------
    def feed(self, level, message, lineNumber, sourceID):
        """"""
        self.message += message

    # ----------------------------------------------------------------------
    def readline(self, timeout=None):
        """"""
        tmp = self.message
        self.message = ''
        return tmp.encode()


########################################################################
class LoadSubprocess:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, parent, path=None, debug=False):
        """Constructor"""

        self.parent = parent
        self.debug = debug

        if path:
            self.load_path(path)

    # ----------------------------------------------------------------------
    def load_path(self, path):
        """"""
        self.timer = QTimer()
        self.port = self.get_free_port()
        # print(self.port)
        self.subprocess_script = run_subprocess(
            [sys.executable, path, self.port])

        if self.debug:
            self.stdout = NBSR(self.subprocess_script.stdout)
        self.timer.singleShot(500, self.get_mode)

    # ----------------------------------------------------------------------
    def get_mode(self):
        """"""
        try:
            try:
                mode = request.urlopen(
                    f'http://localhost:{self.port}/mode', timeout=5).read()
            except:
                mode = request.urlopen(
                    f'http://localhost:5000/mode', timeout=5).read()

            if mode == b'visualization':
                self.parent.label_stream.show()
                self.parent.widget_development_webview.hide()
                self.load_visualization()
            elif mode == b'stimuli':
                self.parent.label_stream.hide()
                self.parent.widget_development_webview.show()
                self.load_webview(f'http://localhost:5000/development')
        except:
            self.timer.singleShot(1000 / 30, self.get_mode)

    # ----------------------------------------------------------------------
    def stop_preview(self):
        """"""
        self.timer.stop()
        if hasattr(self, 'subprocess_script'):
            self.subprocess_script.kill()

        if hasattr(self.parent, 'web_engine'):
            self.parent.web_engine.setUrl('about:blank')

    # ----------------------------------------------------------------------
    def load_visualization(self):
        """"""
        if not hasattr(self, 'stream'):
            try:
                self.stream = request.urlopen(
                    f'http://localhost:{self.port}/', timeout=5)
                self.data_stream = b''
            except:
                pass
            self.timer.singleShot(1000 / 30, self.load_visualization)
            return

        try:
            q = self.stream.read(100000)
        except:  # socket.timeout: timed out
        # except socket.timeout:
            self.timer.singleShot(1000 / 30, self.load_visualization)
            return
        self.data_stream += q

        if self.data_stream.count(b'--frame') >= 2:
            start = self.data_stream.find(b'--frame')
            end = self.data_stream.find(b'--frame', start + 1)

            frame = self.data_stream[start:end]

            self.data_stream = self.data_stream[end:]

            qp = QPixmap()
            qp.loadFromData(frame[37:-2])

            try:
                self.parent.label_stream.setPixmap(
                    qp.scaled(*self.parent.label_stream.size().toTuple(), Qt.KeepAspectRatio))
            except RuntimeError:
                pass

        self.timer.singleShot(1000 / 30, self.load_visualization)

    # ----------------------------------------------------------------------
    def load_webview(self, url):
        """"""
        if not hasattr(self.parent, 'web_engine'):
            self.parent.web_engine = QWebEngineView()
            self.parent.gridLayout_webview.addWidget(self.parent.web_engine)

        if self.debug:
            console = JavaScriptConsole()
            page = QWebEnginePage(self.parent.web_engine)
            page.javaScriptConsoleMessage = console.feed
            self.parent.web_engine.setPage(page)
            self.stdout = console
            page.profile().clearHttpCache()
            # self.parent.web_engine.setZoomFactor(0.5)
            # settings = self.parent.web_engine.settings()
            # settings.ShowScrollBars(False)

        self.parent.web_engine.setUrl(url)

    # ----------------------------------------------------------------------
    def get_free_port(self):
        """"""
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind(('', 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            port = str(s.getsockname()[1])
            logging.info(f'Free port found in {port}')
            return port
