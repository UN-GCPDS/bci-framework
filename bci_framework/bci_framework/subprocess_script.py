"""
"""

import os
import sys
import socket
import signal
import logging
import subprocess
from urllib import request
from contextlib import closing

from PySide2.QtCore import QTimer, QSize
from PySide2.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

from .nbstreamreader import NonBlockingStreamReader as NBSR
from .projects import properties as prop


# ----------------------------------------------------------------------
def run_subprocess(call):
    """"""
    my_env = os.environ.copy()
    my_env['PYTHONPATH'] = ":".join(
        sys.path + [os.path.join(os.path.dirname(sys.argv[0]), 'bci_framework')])

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

        self.main = parent
        self.debug = debug
        self.endpoint = endpoint
        self.web_view = getattr(self.main, web_view)
        self.plot_size = QSize(0, 0)
        self.plot_dpi = 0
        self.stopped = False

        self.main.DPI = 60

        if path:
            self.load_path(path)

    # ----------------------------------------------------------------------
    def load_path(self, path):
        """"""
        self.timer = QTimer()
        self.port = self.get_free_port()
        self.subprocess_script = run_subprocess(
            [sys.executable, path, self.port])

        with open(os.environ['BCISTREAM_PIDS'], 'a+') as file:
            file.write(f'{self.subprocess_script.pid}\n')

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
            self.main.widget_development_webview.show()
            self.url = f'http://localhost:{self.port}'
            self.load_webview(debug_javascript=False)
            # self.parent.web_engine.resizeEvent.connect()
        elif mode == b'stimuli':
            self.main.widget_development_webview.show()
            self.url = f'http://localhost:{self.port}/{self.endpoint}'
            self.load_webview(debug_javascript=True)

    # ----------------------------------------------------------------------
    def stop_preview(self):
        """"""
        self.timer.stop()
        self.stopped = True
        if hasattr(self, 'subprocess_script'):
            # self.subprocess_script.kill()
            self.subprocess_script.terminate()
            try:
                os.kill(self.subprocess_script.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass

        if hasattr(self.main, 'web_engine'):
            self.main.web_engine.setUrl('about:blank')

    # # ----------------------------------------------------------------------
    # def force_feed(self):
        # """"""
        # request.urlopen(f'{self.url}/feed', timeout=1)

    # ----------------------------------------------------------------------
    def load_webview(self, debug_javascript=False):
        """"""

        if not hasattr(self.main, 'web_engine'):
            self.main.web_engine = QWebEngineView()
            self.web_view.addWidget(self.main.web_engine)

        if debug_javascript and self.debug:
            console = JavaScriptConsole()
            page = QWebEnginePage(self.main.web_engine)
            page.javaScriptConsoleMessage = console.feed
            self.main.web_engine.setPage(page)
            self.stdout = console
            page.profile().clearHttpCache()
            # self.parent.web_engine.setZoomFactor(0.5)
            # settings = self.parent.web_engine.settings()
            # settings.ShowScrollBars(False)

        # self.feed()
        if not debug_javascript:
            self.timer.singleShot(1000, self.auto_size)
        else:
            self.main.web_engine.setUrl(self.url)

    # # ----------------------------------------------------------------------
    # def feed(self):
        # """"""
        # self.auto_size(timer=False)
        # self.timer.singleShot(800, lambda :request.urlopen(f'{self.url}/feed', timeout=1))

    # ----------------------------------------------------------------------

    def auto_size(self, timer=True):
        """"""
        if self.stopped:
            return

        dpi = prop.DPI
        f = dpi / self.main.DPI
        try:
            size = self.main.web_engine.size()
            if self.plot_size != size or self.plot_dpi != self.main.DPI:
                self.main.web_engine.setUrl(
                    self.url + f'/?width={f * size.width() / dpi:.2f}&height={f * size.height() / dpi:.2f}&dpi={dpi/f:.2f}')
                self.plot_size = size
                self.plot_dpi = self.main.DPI
        except:
            pass

        if timer:
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

