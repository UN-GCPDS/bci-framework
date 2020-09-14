from multiprocessing import freeze_support
from pyside_material import apply_stylesheet  # , set_icons_theme
from PySide2.QtWidgets import QApplication, QSplashScreen
from PySide2.QtGui import QPixmap, QBitmap, QImage, QBrush, QPainter, QColor, QIcon
from PySide2.QtCore import Qt, QRect, QCoreApplication
from .bci_framework import BCIFramework
import sys
import os
from pathlib import Path


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


# ----------------------------------------------------------------------
def main():
    """"""
    freeze_support()

    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)

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

    app.processEvents()
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
