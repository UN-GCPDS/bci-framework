import os
import sys
import urllib
from pathlib import Path
from datetime import datetime
import shutil

from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QMdiSubWindow, QMenu, QAction
from PySide2.QtCore import QTimer, Qt

from PySide2.QtWidgets import QVBoxLayout, QMenuBar, QMenu, QMdiSubWindow, QWidget

from ...subprocess_script import LoadSubprocess
from ...projects import properties as prop
from ...dialogs import Dialogs
from ...config_manager import ConfigManager


########################################################################
class VisualizationWidget(QMdiSubWindow):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, mdi_area, visualizations_list):
        """Constructor"""
        super().__init__(None)
        ui = os.path.realpath(os.path.join(
            __file__, '..', '..', '..', 'qtgui', 'visualization_widget.ui'))
        self.main = QUiLoader().load(ui, self)
        self.mdi_area = mdi_area

        self.current_viz = None
        self.visualizations_list = visualizations_list

        # Dialogs.save_filename(self.main, '', '', '')

        if '--debug' in sys.argv:
            self.projects_dir = os.path.join(
                os.getenv('BCISTREAM_ROOT'), 'default_projects')
        else:
            self.projects_dir = os.path.join(
                os.getenv('BCISTREAM_HOME'), 'projects')

        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWidget(self.main)
        self.config = ConfigManager()

        self.setStyleSheet(f"""
        * {{
        border: 2px solid {os.getenv('PYSIDEMATERIAL_SECONDARYCOLOR', '#000000')};
        border-width: 0px 2px 2px 2px;
        }}
        QMenuBar {{
        border-width: 0;
        }}
        """)

    # ----------------------------------------------------------------------
    def contextMenuEvent(self, event):
        """"""
        menu = QMenu(self)

        menu.addAction(QAction(QIcon.fromTheme('dialog-cancel'),
                               "Remove", self, triggered=self.remove))
        if self.current_viz:
            menu.addAction(QAction(QIcon.fromTheme('view-refresh'),
                                   "Reload", self, triggered=self.reload))

        menu.exec_(event.globalPos())

    # ----------------------------------------------------------------------
    def remove(self):
        """"""
        self.stop_preview()
        self.deleteLater()
        QTimer().singleShot(1000 / 50, self.mdi_area.tileSubWindows)

    # ----------------------------------------------------------------------
    def reload(self):
        """"""
        self.stop_preview()
        if self.current_viz:
            self.load_visualization(self.current_viz)

    # ----------------------------------------------------------------------
    def save_img(self):
        """"""
        name = f"{self.current_viz.replace(' ', '')} {str(datetime.now()).replace(':', '_')}.jpg"
        # filename = os.path.join(os.getenv('BCISTREAM_TMP'), name)
        # self.stream_subprocess.main.web_engine.grab().save(filename, 'JPG')

        path = self.config.get(
            'directories', 'screenshots', str(Path.home()))

        dst = Dialogs.save_filename(self.mdi_area, 'Save\
        capture', os.path.join(path, name), filter="Images (*.jpg)")
        # if dst:
            # shutil.move(filename, dst)
            # self.config.set('directories', 'screenshots', str(os.path.dirname(dst)))
            # self.config.save()

    # ----------------------------------------------------------------------
    def load_visualization(self, visualization):
        """"""
        self.current_viz = visualization
        module = os.path.join(self.projects_dir, visualization, 'main.py')
        self.stream_subprocess = LoadSubprocess(
            self.main, module, debug=False, web_view='gridLayout_webview')

        self.update_menu_bar(visualization)

    # ----------------------------------------------------------------------
    def update_menu_bar(self, visualization=None):
        """"""
        self.build_menubar(self.visualizations_list, visualization)
        self.main.gridLayout_menubar.setMenuBar(self.menubar)
        self.menubar.adjustSize()
        self.menubar.setStyleSheet(
            self.menubar.styleSheet() + """QMenuBar::item {width: 1px;}""")

    # ----------------------------------------------------------------------
    def stop_preview(self):
        """"""
        if hasattr(self, 'preview_stream'):
            self.stream_subprocess.stop_preview()

    # ----------------------------------------------------------------------
    def build_menubar(self, visualizations_list, visualization):
        """"""
        self.menubar = QMenuBar(self)

        self.right_menubar = QMenuBar(self)
        # Visualization
        if visualization:
            menu_visualization = QMenu(visualization + ' 🞃')
        else:
            menu_visualization = QMenu('Visualization' + ' 🞃')

        # menu_visualization.setProperty('class', 'accent')

        for viz in visualizations_list:
            if viz != visualization:
                menu_visualization.addAction(QAction(viz, menu_visualization,
                                                     triggered=self.set_visualization(viz)))
        # self.menubar.addMenu(menu_visualization)
        self.right_menubar.addMenu(menu_visualization)

        self.right_menubar.setStyleSheet(f"""
        QMenuBar::item {{
            background-color: {os.getenv('PYSIDEMATERIAL_PRIMARYCOLOR', '#ffffff')};
            color: {os.getenv('PYSIDEMATERIAL_PRIMARYTEXTCOLOR', '#ffffff')};
        }}

        """)
        # self.right_menubar.setStyleSheet(f"""QMenuBar::item {{color: {os.getenv('PYSIDEMATERIAL_PRIMARYCOLOR', '#ffffff')};}}""")

        # menu_visualization.setStyleSheet(f"""* {{color: {os.getenv('PYSIDEMATERIAL_PRIMARYCOLOR', '#ffffff')};}}""")

        # self.menubar.addMenu(menu_visualization)
        self.menubar.setCornerWidget(
            self.right_menubar, corner=Qt.TopLeftCorner)

        # View
        menu_view = QMenu("View")
        if visualization:
            menu_view.addAction(
                QAction('Reload', menu_view, triggered=self.reload))
            menu_view.addAction(
                QAction('Save capture', menu_view, triggered=self.save_img))
            menu_view.addSeparator()
            menu_view.addAction(
                QAction('Close', menu_view, triggered=self.remove))
        else:
            menu_view.setEnabled(False)
        self.menubar.addMenu(menu_view)

        # DPI
        menu_dpi = QMenu("DPI (60)")
        if visualization:
            for dpi in [60, 70, 80, 90, 100, 110, 120, 130]:
                menu_dpi.addAction(QAction(
                    f'{dpi}', menu_dpi, checkable=True, triggered=self.set_dpi(menu_dpi, f'{dpi}', dpi)))
                if dpi == 60:
                    self.set_dpi(menu_dpi, f'{dpi}', dpi)()
            # menu_dpi.addAction(QAction(f'{prop.DPI:.2f} (system)', menu_dpi, checkable=True, triggered=self.set_dpi(menu_dpi, f'{prop.DPI:.2f} (system)', prop.DPI)))
        else:
            menu_dpi.setEnabled(False)
        self.menubar.addMenu(menu_dpi)

    # ----------------------------------------------------------------------
    def set_dpi(self, menu_dpi, text, dpi):
        """"""
        def wrap():
            [action.setChecked(False) for action in menu_dpi.actions()]
            [action.setChecked(
                True) for action in menu_dpi.actions() if action.text() == text]
            self.main.DPI = dpi
            menu_dpi.setTitle(f'DPI ({dpi})')
        return wrap

    # ----------------------------------------------------------------------
    def set_visualization(self, visualization):
        """"""
        def wrap():
            self.load_visualization(visualization)
        return wrap


