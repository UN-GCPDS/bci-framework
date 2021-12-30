"""
=============
BCI-Framework
=============
"""

import sys
import os
import json
import psutil
import shutil
import signal
import logging
from pathlib import Path
from multiprocessing import freeze_support

from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QCoreApplication
from qt_material import apply_stylesheet, build_stylesheet

from .framework import BCIFramework
from .framework.config_manager import ConfigManager


# Set logging
logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger('kafka').setLevel(logging.ERROR)
logging.getLogger('matplotlib').setLevel(logging.ERROR)

os.environ.setdefault('BCISTREAM_RASPAD',
                      json.dumps(('--raspad' in sys.argv)))

# Deafine defaults variables
os.environ.setdefault('APP_NAME', 'BCI Framework')
os.environ.setdefault(
    'BCISTREAM_ROOT', os.path.abspath(os.path.dirname(__file__)))
os.environ.setdefault('BCISTREAM_HOME', os.path.join(
    Path.home(), '.bciframework'))
os.environ.setdefault('BCISTREAM_SYNCLATENCY', '0')
# os.environ.setdefault('BCISTREAM_TMP', os.path.join(os.getenv('BCISTREAM_HOME'), 'tmp'))

# Create custom directories
if not os.path.exists(os.environ['BCISTREAM_HOME']):
    os.mkdir(os.environ['BCISTREAM_HOME'])

# Create configuration if not exists
if not os.path.exists(os.path.join(os.environ['BCISTREAM_HOME'], '.bciframework')):
    shutil.copy(os.path.join(os.environ['BCISTREAM_ROOT'], 'assets', 'bciframework.default'),
                os.path.join(os.environ['BCISTREAM_HOME'], '.bciframework'))

# Copy default_extensions if not exists
if not os.path.exists(os.path.join(os.environ['BCISTREAM_HOME'], 'default_extensions')):
    shutil.copytree(os.path.join(os.environ['BCISTREAM_ROOT'], 'default_extensions'),
                    os.path.join(os.environ['BCISTREAM_HOME'], 'default_extensions'))

# Copy kafka_scripts if not exists
if not os.path.exists(os.path.join(os.environ['BCISTREAM_HOME'], 'kafka_scripts')):
    shutil.copytree(os.path.join(os.environ['BCISTREAM_ROOT'], 'kafka_scripts'),
                    os.path.join(os.environ['BCISTREAM_HOME'], 'kafka_scripts'))

    # Copy python_scripts if not exists
    if not os.path.exists(os.path.join(os.environ['BCISTREAM_HOME'], 'python_scripts')):
        shutil.copytree(os.path.join(os.environ['BCISTREAM_ROOT'], 'python_scripts'),
                        os.path.join(os.environ['BCISTREAM_HOME'], 'python_scripts'))

# Copy notebooks if not exists
if not os.path.exists(os.path.join(os.environ['BCISTREAM_HOME'], 'notebooks')):
    shutil.copytree(os.path.join(os.environ['BCISTREAM_ROOT'], 'notebooks'),
                    os.path.join(os.environ['BCISTREAM_HOME'], 'notebooks'))

from .framework.qtgui.icons import generate_icons


# ----------------------------------------------------------------------
def kill_subprocess() -> None:
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
def kill_childs() -> None:
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
def main() -> None:
    """"""
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)

    # ------------------------------------------------------------
    # Splash
    # splash_file = os.path.join(
        # os.environ['BCISTREAM_ROOT'], 'assets', 'banner.svg')
    # pixmap = QPixmap(splash_file, 'svg')
    # splash = QSplashScreen(
        # pixmap, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    # splash.setMask(pixmap.mask())
    # splash.show()
    # ------------------------------------------------------------

    kill_subprocess()
    freeze_support()

    app.processEvents()
    app.setQuitOnLastWindowClosed(False)
    app.lastWindowClosed.connect(kill_subprocess)
    app.lastWindowClosed.connect(kill_childs)
    app.lastWindowClosed.connect(app.quit)

    os.environ['BCISTREAM_DPI'] = str(app.screens()[0].physicalDotsPerInch())

    # ------------------------------------------------------------
    # Theme
    extra = {'danger': '#dc3545',
             'warning': '#e2a963',
             'success': '#17a2b8',

             'font_family': 'Roboto',
             'density_scale': -1,
             }

    if json.loads(os.getenv('BCISTREAM_RASPAD')):
        light_theme = 'light_teal.xml'
        dark_theme = 'dark_teal.xml'
        extra['density_scale'] = 2
    else:
        # light_theme = 'light_blue.xml'
        # dark_theme = 'dark_blue.xml'
        light_theme = 'light_cyan_500.xml'
        dark_theme = 'dark_cyan.xml'

    custom_style = os.path.join(os.path.dirname(__file__), 'custom.css')

    if ConfigManager().get('framework', 'theme', 'light') == 'light':
        apply_stylesheet(app, theme=light_theme, invert_secondary=True,
                         extra=extra, parent='bci_framework_qt_material',
                         style='Fusion')
        custom_builded = build_stylesheet(theme=light_theme, invert_secondary=True,
                                          extra=extra, parent='bci_framework_qt_material',
                                          template=custom_style)
    else:
        apply_stylesheet(app, theme=dark_theme, extra=extra,
                         parent='bci_framework_qt_material', style='Fusion')
        custom_builded = build_stylesheet(theme=dark_theme, extra=extra,
                                          parent='bci_framework_qt_material', template=custom_style)

    app.setStyleSheet(app.styleSheet() + custom_builded)

    generate_icons()
    # ------------------------------------------------------------

    frame = BCIFramework()
    frame.main.showMaximized()
    if json.loads(os.getenv('BCISTREAM_RASPAD')):
        frame.main.showFullScreen()
    # splash.finish(frame)  # Hide Splash
    app.exec_()


if __name__ == "__main__":
    main()
