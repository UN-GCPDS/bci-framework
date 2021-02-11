"""
==================
Subprocess handler
==================
"""

import os
import sys
import socket
import logging
import subprocess
from urllib import request
from contextlib import closing
from typing import TypeVar, Optional

from PySide2.QtCore import QTimer, QSize
from PySide2.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

from .nbstreamreader import NonBlockingStreamReader as NBSR
from ..extensions import properties as prop


COMMAND = TypeVar('Command')
PATH = TypeVar('Path')


# ----------------------------------------------------------------------
def run_subprocess(call: COMMAND) -> subprocess.Popen:
    """Run a python script with non blocking debugger installed."""
    my_env = os.environ.copy()
    my_env['PYTHONPATH'] = ":".join(
        sys.path + [os.path.join(os.path.dirname(sys.argv[0]))])

    sub = subprocess.Popen(call,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT,
                           env=my_env,
                           preexec_fn=os.setsid,
                           # shell=True,
                           )

    sub.nb_stdout = NBSR(sub.stdout)

    return sub


########################################################################
class BrythonLogging:
    """Log messages from Brython."""

    message = ""

    # ----------------------------------------------------------------------
    def feed(self, level: int, message: str, lineNumber: int, sourceID: str) -> None:
        """Concatenae messages."""
        self.message += message

    # ----------------------------------------------------------------------
    def readline(self, timeout: Optional[int] = None) -> str:
        """Get mesage from JavaScriptConsole."""
        tmp = self.message
        self.message = ''
        return tmp.encode()


########################################################################
class VisualizationSubprocess:
    """Define matplotlib properties and start the auto-resizer."""

    # ----------------------------------------------------------------------
    def viz_auto_size(self, timer: bool = True) -> None:
        """"""
        if self.stopped:
            return

        dpi = prop.DPI
        f = dpi / self.main.DPI
        try:
            size = self.main.web_engine.size()
            if self.plot_size != size or self.plot_dpi != self.main.DPI:
                if 'light' in os.environ.get('QTMATERIAL_THEME'):
                    background = 'ffffff'
                else:
                    background = '000000'

                self.main.web_engine.setUrl(
                    self.url + f'/?width={f * size.width() / dpi:.2f}&height={f * size.height() / dpi:.2f}&dpi={dpi/f:.2f}&background={background}')
                self.plot_dpi = self.main.DPI
                self.plot_size = size
        except:
            pass

        if timer:
            self.timer.singleShot(1000, self.viz_auto_size)

    # ----------------------------------------------------------------------
    def viz_debug(self) -> None:
        """"""
        self.stdout = self.subprocess_script.nb_stdout

    # ----------------------------------------------------------------------
    def viz_start(self) -> None:
        """"""
        self.timer.singleShot(1000, self.viz_auto_size)


########################################################################
class StimuliSubprocess:
    """Connect with Brython logs."""

    # ----------------------------------------------------------------------
    def stm_debug(self) -> None:
        """"""
        console = BrythonLogging()
        self.web_engine_page = QWebEnginePage(self.main.web_engine)
        self.web_engine_page.javaScriptConsoleMessage = console.feed
        self.main.web_engine.setPage(self.web_engine_page)
        self.stdout = console
        self.web_engine_page .profile().clearHttpCache()
        self.stm_start()

    # ----------------------------------------------------------------------
    def stm_start(self) -> None:
        """"""
        self.main.web_engine.setUrl(self.url)


########################################################################
class LoadSubprocess(VisualizationSubprocess, StimuliSubprocess):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, parent, path: PATH = None):
        """"""
        self.main = parent
        self.web_view = self.main.gridLayout_webview
        self.plot_size = QSize(0, 0)
        self.plot_dpi = 0
        self.stopped = False

        if path:
            self.load_path(path)

    # ----------------------------------------------------------------------
    def load_path(self, path: PATH) -> None:
        """Load Python scipt."""
        self.timer = QTimer()
        self.port = self.get_free_port()
        self.subprocess_script = run_subprocess(
            [sys.executable, path, self.port])

        self.prepare()

    # ----------------------------------------------------------------------
    def prepare(self) -> None:
        """Try to load the webview."""
        # Try to get mode
        try:
            self.mode = request.urlopen(
                f'http://localhost:{self.port}/mode', timeout=10).read().decode()
        except:  # if fail
            self.timer.singleShot(100, self.prepare)  # call again
            return

        # and only when the mode is explicit...

        if self.mode == 'visualization':
            self.is_visualization = True
            self.is_stimuli = False
            endpoint = ''
        elif self.mode == 'stimuli':
            self.is_visualization = False
            self.is_stimuli = True
            endpoint = 'dashboard'

        # self.main.widget_development_webview.show()
        self.url = f'http://localhost:{self.port}/{endpoint}'
        self.load_webview()

    # ----------------------------------------------------------------------
    def stop_preview(self) -> None:
        """Kill the subprocess and crear the webview."""
        self.timer.stop()
        self.stopped = True
        if hasattr(self, 'subprocess_script'):
            self.subprocess_script.nb_stdout.stop()
            self.subprocess_script.terminate()
            if hasattr(self, 'subprocess_script'):
                self.timer.singleShot(
                    300, lambda: self.__delattr__('subprocess_script'))

        if hasattr(self, 'web_engine_page'):
            try:
                self.web_engine_page.deleteLater()
            except:  # already deleted.
                pass

        # TODO: A wait page could be a god idea
        self.main.widget_development_webview.hide()
        if hasattr(self.main, 'web_engine'):
            self.main.web_engine.setUrl('about:blank')

    # ----------------------------------------------------------------------
    def load_webview(self) -> None:
        """After the process starting, set the URL into the webview."""
        self.main.widget_development_webview.show()

        # Create main QWebEngineView object
        if not hasattr(self.main, 'web_engine'):
            self.main.web_engine = QWebEngineView()
            self.web_view.addWidget(self.main.web_engine)

        else:
            self.main.web_engine.deleteLater()
            self.main.web_engine = QWebEngineView()
            self.web_view.addWidget(self.main.web_engine)

        # Set URL and start interface
        if self.is_visualization:
            self.viz_start()
        elif self.is_stimuli:
            self.stm_start()

    # ----------------------------------------------------------------------
    def start_debug(self) -> None:
        """Try to start the debugger."""
        try:
            if self.is_stimuli:
                self.stm_debug()
            elif self.is_visualization:
                self.viz_debug()
        except:
            pass

    # ----------------------------------------------------------------------
    def reload(self) -> None:
        """Restart the webview."""
        self.main.web_engine.setUrl(self.url)

    # ----------------------------------------------------------------------
    def get_free_port(self) -> str:
        """Get any free port available."""
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind(('', 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            port = str(s.getsockname()[1])
            logging.info(f'Free port found in {port}')
            return port

