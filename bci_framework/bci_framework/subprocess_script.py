"""
"""

import os
import sys
import socket
import logging
import subprocess
from urllib import request
from contextlib import closing

from PySide2.QtCore import QTimer, QSize
from PySide2.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

from .nbstreamreader import NonBlockingStreamReader as NBSR


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
    def __init__(self, parent, path=None, debug=False, web_view='gridLayout_webview', endpoint=''):
        """Constructor"""

        print('subprocess.......................')

        self.parent = parent
        self.debug = debug
        self.endpoint = endpoint
        self.web_view = getattr(self.parent, web_view)
        self.plot_size = QSize(0, 0)

        if path:
            self.load_path(path)

    # ----------------------------------------------------------------------
    def load_path(self, path):
        """"""
        self.timer = QTimer()
        self.port = self.get_free_port()
        self.subprocess_script = run_subprocess(
            [sys.executable, path, self.port])

        if self.debug:
            self.stdout = NBSR(self.subprocess_script.stdout)
        self.timer.singleShot(500, self.get_mode)

    # ----------------------------------------------------------------------
    def get_mode(self):
        """"""
        try:
            mode = request.urlopen(
                f'http://localhost:{self.port}/mode', timeout=10).read()
        except:
            self.timer.singleShot(1000 / 30, self.get_mode)
            return

        if mode == b'visualization':
            self.parent.widget_development_webview.show()
            self.url = f'http://localhost:{self.port}'
            self.load_webview(debug_javascript=False)
            # self.parent.web_engine.resizeEvent.connect()
        elif mode == b'stimuli':
            self.parent.widget_development_webview.show()
            self.url = f'http://localhost:{self.port}/{self.endpoint}'
            self.load_webview(debug_javascript=True)

    # ----------------------------------------------------------------------
    def stop_preview(self):
        """"""
        self.timer.stop()
        if hasattr(self, 'subprocess_script'):
            # self.subprocess_script.kill()
            self.subprocess_script.terminate()

        if hasattr(self.parent, 'web_engine'):
            self.parent.web_engine.setUrl('about:blank')

    # ----------------------------------------------------------------------
    def load_webview(self, debug_javascript=False):
        """"""
        if not hasattr(self.parent, 'web_engine'):
            self.parent.web_engine = QWebEngineView()

            self.parent.web_engine.setStyleSheet("""
            * {
                background-color: red;
                border: 1px solid blue;
                border-radius: 4px;
            }
            """)

            self.web_view.addWidget(self.parent.web_engine)

        if debug_javascript and self.debug:
            console = JavaScriptConsole()
            page = QWebEnginePage(self.parent.web_engine)
            page.javaScriptConsoleMessage = console.feed
            self.parent.web_engine.setPage(page)
            self.stdout = console
            page.profile().clearHttpCache()
            # self.parent.web_engine.setZoomFactor(0.5)
            # settings = self.parent.web_engine.settings()
            # settings.ShowScrollBars(False)

        # self.parent.web_engine.setUrl(url)
        self.timer.singleShot(100, self.auto_size)

    # ----------------------------------------------------------------------
    def auto_size(self):
        """"""
        dpi = float(os.environ['BCISTREAM_DPI'])
        f = 2.7

        size = self.parent.web_engine.size()
        if self.plot_size != size:
            self.parent.web_engine.setUrl(
                self.url + f'/?width={f * size.width() / dpi:.2f}&height={f * size.height() / dpi:.2f}&dpi={dpi/f:.2f}')

            self.plot_size = size

        self.timer.singleShot(1000, self.auto_size)

    # ----------------------------------------------------------------------
    def get_free_port(self):
        """"""
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind(('', 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            port = str(s.getsockname()[1])
            logging.warning(f'Free port found in {port}')
            return port
