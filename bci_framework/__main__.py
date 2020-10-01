from multiprocessing import freeze_support
from pyside_material import apply_stylesheet  # , set_icons_theme
from PySide2.QtWidgets import QApplication, QSplashScreen
from PySide2.QtGui import QPixmap, QBitmap, QImage, QBrush, QPainter, QColor, QIcon
from PySide2.QtCore import Qt, QRect, QCoreApplication, SIGNAL
from .bci_framework import BCIFramework
import sys
import os
from pathlib import Path
import psutil
import logging
import json

import signal

import logging
logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger('kafka').setLevel(logging.ERROR)
logging.getLogger('matplotlib').setLevel(logging.ERROR)


"""A distributed processing tool, stimuli delivery, psychophysiological
experiments, and real-time visualizations for OpenBCI."""


os.environ.setdefault('APP_NAME', 'BCI Framework')
os.environ.setdefault(
    'BCISTREAM_ROOT', os.path.abspath(os.path.dirname(__file__)))
os.environ.setdefault('BCISTREAM_HOME', os.path.join(
    Path.home(), '.bciframework'))
# os.environ.setdefault('BCISTREAM_PIDS', os.path.join(
    # os.getenv('BCISTREAM_HOME'), '.pids'))
os.environ.setdefault('BCISTREAM_TMP', os.path.join(
    os.getenv('BCISTREAM_HOME'), 'tmp'))


if not os.path.exists(os.getenv('BCISTREAM_TMP')):
    os.mkdir(os.getenv('BCISTREAM_TMP'))


# sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# ----------------------------------------------------------------------
def kill_subprocess():
    """Kill all subprocess registered.

    On start, kill previous live subprocess. On exit, kill all subprocess
    registered in the current (parent) process.
    """

    file = os.path.join(os.environ['BCISTREAM_HOME'], '.subprocess')
    if not os.path.exists(file):
        return

    with open(file, 'r') as file_:
        try:
            subs = json.load(file_)
            for sub in subs:
                try:
                    os.kill(int(sub), signal.SIGKILL)
                    logging.info(f'killing {sub}')
                except ProcessLookupError:
                    pass
        except:
            pass

    os.remove(file)


# ----------------------------------------------------------------------
def kill_childs():
    """Kill the remaning childs not registered yet (only on exit)."""

    current_process = psutil.Process()
    children = current_process.children(recursive=True)
    for child in children:
        try:
            logging.info(f'killing {child.pid}')
            os.kill(child.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


# ----------------------------------------------------------------------
def main():
    """"""
    kill_subprocess()
    freeze_support()

    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

    app = QApplication(sys.argv)
    app.processEvents()
    app.setQuitOnLastWindowClosed(False)
    app.lastWindowClosed.connect(kill_subprocess)
    app.lastWindowClosed.connect(kill_childs)
    app.lastWindowClosed.connect(lambda: app.quit())

    os.environ['BCISTREAM_DPI'] = str(app.screens()[0].physicalDotsPerInch())

    if '--no_splash' in sys.argv:
        pixmap = QPixmap(os.path.join("assets", "splash_curves.svg"))
        splash = QSplashScreen(
            pixmap, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        splash.setMask(pixmap.mask())
        splash.show()
        splash.setStyleSheet("""
            font-family: mono;
            font-weight: normal;
            font-size: 11pt;
            """)

    extra = {'danger': '#dc3545',
             'warning': '#ffc107',
             'success': '#17a2b8',
             }
    apply_stylesheet(app, theme='dark_cyan.xml', extra=extra)

    QIcon.setThemeName("icons-dark")

    frame = BCIFramework()
    frame.main.showMaximized()

    if '--no_splash' in sys.argv:
        splash.finish(frame)

    app.exec_()


if __name__ == "__main__":
    main()
