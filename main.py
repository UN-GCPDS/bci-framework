from multiprocessing import freeze_support
from pyside_material import apply_stylesheet  # , set_icons_theme
from PySide2.QtWidgets import QApplication, QSplashScreen
from PySide2.QtGui import QPixmap, QBitmap, QImage, QBrush, QPainter, QColor, QIcon
from PySide2.QtCore import Qt, QRect, QCoreApplication
from bci_framework import BCIFramework
import sys
import os

"""A distributed processing tool, stimuli delivery, psychophysiological
experiments, and real-time visualizations for OpenBCI."""


os.environ.setdefault('APP_NAME', 'BCI Framework')


if __name__ == "__main__":
    freeze_support()

    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)

    os.environ['BCISTREAM_DPI'] = str(app.screens()[0].physicalDotsPerInch())

    # pixmap = QPixmap("assets/splash3.svg")
    # splash = QSplashScreen(
        # pixmap, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    # splash.setMask(pixmap.mask())
    # splash.show()
    # splash.setStyleSheet("""
        # font-family: mono;
        # font-weight: normal;
        # font-size: 11pt;
        # """)

    # def splash_logging(msg):
        # if not splash is None:
            # splash.showMessage(
                # '\t' + msg, color=QColor("#888e93"), alignment=Qt.AlignBottom)
    # splash_logging(f'eeg-framework 0.1')

    app.processEvents()

    extra = {'danger': '#dc3545',
             'warning': '#ffc107',
             'success': '#17a2b8',
             }
    apply_stylesheet(app, theme='dark_cyan.xml', extra=extra)
    # apply_stylesheet(app, theme='light_cyan_500.xml',
                     # extra=extra, light_secondary=True)

    QIcon.setThemeName("icons-dark")

    frame = BCIFramework()
    frame.main.showMaximized()

    # if not splash is None:
        # splash.finish(frame)

    app.exec_()

