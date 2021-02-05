import sys
import os
import json
import psutil
import shutil
import signal
import logging
from pathlib import Path
from multiprocessing import freeze_support

from PySide2.QtWidgets import QApplication
from PySide2.QtCore import Qt, QCoreApplication
from qt_material import apply_stylesheet

from .bci_framework import BCIFramework
from .bci_framework.config_manager import ConfigManager


# Set logging
logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger('kafka').setLevel(logging.ERROR)
logging.getLogger('matplotlib').setLevel(logging.ERROR)

os.environ.setdefault('APP_NAME', 'BCI Framework')
os.environ.setdefault(
    'BCISTREAM_ROOT', os.path.abspath(os.path.dirname(__file__)))
os.environ.setdefault('BCISTREAM_HOME', os.path.join(
    Path.home(), '.bciframework'))
# os.environ.setdefault('BCISTREAM_TMP', os.path.join(os.getenv('BCISTREAM_HOME'), 'tmp'))


# Create configuration if not exists
if not os.path.exists(os.path.join(os.environ['BCISTREAM_HOME'], '.bciframework')):
    shutil.copy(os.path.join(os.environ['BCISTREAM_ROOT'], 'assets', 'bciframework.default'),
                os.path.join(os.environ['BCISTREAM_HOME'], '.bciframework'))

# Copy default_projects if not exists
if not os.path.exists(os.path.join(os.environ['BCISTREAM_HOME'], 'default_projects')):
    shutil.copytree(os.path.join(os.environ['BCISTREAM_ROOT'], 'default_projects'),
                    os.path.join(os.environ['BCISTREAM_HOME'], 'default_projects'))


from .bci_framework.qtgui.icons import generate_icons
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

    extra = {'danger': '#dc3545',
             'warning': '#e2a963',
             'success': '#17a2b8',
             }

    if ConfigManager().get('framework', 'theme') == 'light':
        apply_stylesheet(app, theme='light_cyan_500.xml', invert_secondary=True,
                         extra=extra, parent='bci_framework_qt_material')
    else:
        apply_stylesheet(app, theme='dark_cyan.xml', extra=extra,
                         parent='bci_framework_qt_material')

    stylesheet = app.styleSheet()
    with open(os.path.join(os.path.dirname(__file__), 'custom.css')) as file:
        app.setStyleSheet(stylesheet + file.read().format(**os.environ))

    generate_icons()

    frame = BCIFramework()
    frame.main.showMaximized()

    app.exec_()


if __name__ == "__main__":
    main()
