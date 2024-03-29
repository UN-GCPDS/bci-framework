"""
===============
Stream handlers
===============
"""

import os
import sys
import json
import pickle
from datetime import datetime
from typing import Optional, List, Callable, TypeVar
from collections.abc import Sequence

from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QTimer, Qt, QRect
from PySide6.QtWidgets import QMdiSubWindow, QMenu, QMenuBar
from PySide6.QtGui import QAction, QActionGroup

from .subprocess_handler import LoadSubprocess
from .config_manager import ConfigManager

BCIFR_FILE = 'bcifr'

PathLike = TypeVar('PathLike')
Event = TypeVar('QEvent')


########################################################################
class ExtensionWidget(QMdiSubWindow):
    """MDIArea with extension."""

    # ----------------------------------------------------------------------
    def __init__(self, mdi_area,
                 mode: str,
                 extensions_list: List[str] = [],
                 autostart: Optional[str] = None,
                 hide_menu: Optional[bool] = False,
                 directory: Optional[str] = None):
        """"""
        super().__init__(None)

        if mode == 'timelock':
            ui = os.path.realpath(os.path.join(
                os.environ['BCISTREAM_ROOT'], 'framework', 'qtgui', 'extension_timelock_widget.ui'))
        else:
            ui = os.path.realpath(os.path.join(
                os.environ['BCISTREAM_ROOT'], 'framework', 'qtgui', 'extension_widget.ui'))

        self.main = QUiLoader().load(ui, self)
        self.mdi_area = mdi_area

        self.main.DPI = 70
        self.mode = mode
        self.current_viz = None

        if autostart:
            self.extensions_list = [('name', autostart)]
        else:
            self.extensions_list = extensions_list

        if directory:
            self.projects_dir = directory
        else:
            if '--local' in sys.argv:
                self.projects_dir = os.path.join(
                    os.getenv('BCISTREAM_ROOT'), 'default_extensions')
            else:
                self.projects_dir = os.path.join(
                    os.getenv('BCISTREAM_HOME'), 'default_extensions')

        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWidget(self.main)
        self.config = ConfigManager()

        if not self.is_timeloclk:
            style = f"""
            * {{
            border: 2px solid {os.getenv('QTMATERIAL_SECONDARYCOLOR', '#000000')};
            border-width: 0px 2px 2px 2px;
            }}
            """
        else:
            style = ''

        self.setStyleSheet(f"""
        {style}

        QMenuBar {{
        background: {os.getenv('QTMATERIAL_SECONDARYCOLOR', '#000000')};
        border-width: 0;
        }}
        """)

        if autostart:
            self.load_extension(autostart)

        if hide_menu:
            self.menubar.hide()

    # ----------------------------------------------------------------------
    @property
    def is_visualization(self) -> str:
        """"""
        return self.mode == 'visualization'

    # ----------------------------------------------------------------------
    @property
    def is_stimuli(self) -> bool:
        """"""
        return self.mode in ['stimuli', 'delivery']

    # ----------------------------------------------------------------------
    @property
    def is_analysis(self) -> bool:
        """"""
        return self.mode == 'analysis'

    # ----------------------------------------------------------------------
    @property
    def is_timeloclk(self) -> bool:
        """"""
        return self.mode == 'timelock'

    # ----------------------------------------------------------------------
    def load_extension(self, extension: str, debugger: bool = False) -> None:
        """Load project."""
        self.current_viz = extension
        module = os.path.join(self.projects_dir, extension, 'main.py')
        self.stream_subprocess = LoadSubprocess(
            self.main, module, use_webview=not self.is_analysis, debugger=debugger)

        interact = os.path.join(self.projects_dir, extension, 'interact')
        if os.path.exists(interact):
            with open(interact, 'r') as file:
                interact_contet = [json.loads(c)
                                   for c in file.read().split('\n') if c]
        else:
            interact_contet = None

        bcifr = pickle.load(
            open(os.path.join(self.projects_dir, extension, BCIFR_FILE), 'rb'))
        bcifr['name']

        self.update_menu_bar(bcifr['name'], debugger, interact_contet)
        # self.update_ip(self.stream_subprocess.port)
        self.update_ip('9999')
        self.loaded()

    # ----------------------------------------------------------------------
    def loaded(self, *args, **kwargs) -> None:
        """Method to connect events."""
        # keep this

    # ----------------------------------------------------------------------
    def update_ip(self, *args, **kwargs) -> None:
        """Method to connect events."""
        # keep this

    # ----------------------------------------------------------------------
    def remove(self) -> None:
        """Remove active extension."""
        self.stop_preview()
        if hasattr(self, 'stream_subprocess'):
            del self.stream_subprocess

        if self.is_visualization:
            self.deleteLater()
            QTimer().singleShot(1000 / 50, self.mdi_area.tileSubWindows)
        elif self.is_stimuli:
            self.update_menu_bar()
            self.loaded()

        if hasattr(self, 'on_remove_callback'):
            self.on_remove_callback()

    # ----------------------------------------------------------------------
    def on_remove(self, callback: Callable) -> None:
        """"""
        self.on_remove_callback = callback

    # ----------------------------------------------------------------------
    def save_img(self, name: Optional[str] = None) -> PathLike:
        """Save capture of visualization in the project directory."""
        if name is None:
            name = f"{self.current_viz.replace(' ', '')} {str(datetime.now()).replace(':', '_')}.jpg"
        captures_dir = os.path.join(
            self.projects_dir, self.current_viz, 'captures')
        filename = os.path.join(captures_dir, name)

        if not os.path.exists(captures_dir):
            os.makedirs(captures_dir, exist_ok=True)

        if os.path.exists(f'{filename}'):
            os.remove(f'{filename}')

        if web_engine := getattr(self.stream_subprocess.main, 'web_engine', False):
            web_engine.grab().save(filename, 'JPG')

        return filename

    # ----------------------------------------------------------------------
    def update_menu_bar(self, visualization: Optional[bool] = None, debugger: bool = False, interact_content: Optional[list] = []) -> None:
        """Create menubar."""
        if self.is_visualization:
            self.build_menu_visualization(
                visualization, debugger, interact_content)
        elif self.is_stimuli:
            self.build_menu_stimuli(visualization, debugger)
        elif self.is_timeloclk:
            self.build_menu_timeloclk(visualization, debugger)

        if not self.is_analysis:

            self.menubar.setStyleSheet("""
            QToolButton:hover,
            QToolButton:pressed,
            QToolButton {
              background-color: transparent;
            }
            """)
            # self.resize_menubar()
            self.main.gridLayout_menubar.setMenuBar(self.menubar)

    # ----------------------------------------------------------------------
    def resize_menubar(self) -> None:
        """"""
        if hasattr(self, 'menubar'):
            self.menubar.setGeometry(
                QRect(0, 0, self.menubar.parent().rect().width(), 37))

    # ----------------------------------------------------------------------
    def resizeEvent(self, event: Event) -> None:
        """"""
        super().resizeEvent(event)
        self.resize_menubar()
        # QTimer.singleShot(10, self.resize_menubar)

    # ----------------------------------------------------------------------
    def stop_preview(self) -> None:
        """Stop process."""
        if hasattr(self, 'stream_subprocess'):
            self.stream_subprocess.stop_preview()

    # ----------------------------------------------------------------------
    def reload(self) -> None:
        """Restart process."""
        self.stream_subprocess.reload()

    # ----------------------------------------------------------------------
    def build_menu_visualization(self, visualization: bool, debugger: Optional[bool] = False, interact_content: Optional[list] = []) -> None:
        """Menu for visualizations."""
        self.menubar = QMenuBar(self)
        self.menubar.clear()
        # self.menubar.setMinimumWidth(1e4)

        self.accent_menubar = QMenuBar(self)

        # Title
        if debugger:
            menu_stimuli = QMenu(f"Debugging: {visualization}")
        else:
            if visualization:
                menu_stimuli = QMenu(f'{visualization } 🞃')
            else:
                menu_stimuli = QMenu('Real-time analysis 🞃')

        # Add visualizations
        for viz, path in self.extensions_list:
            if viz != visualization:
                menu_stimuli.addAction(QAction(viz, menu_stimuli,
                                               triggered=self.set_extension(path)))

        self.accent_menubar.addMenu(menu_stimuli)

        # Menu with accent color
        self.accent_menubar.setStyleSheet(f"""
        QMenuBar::item {{
            background-color: {os.getenv('QTMATERIAL_PRIMARYCOLOR', '#ffffff')};
            color: {os.getenv('QTMATERIAL_PRIMARYTEXTCOLOR', '#ffffff')};
            }}""")

        # Set the menu in first position
        self.menubar.setCornerWidget(
            self.accent_menubar, corner=Qt.TopLeftCorner)

        # View
        menu_view = QMenu("View")
        if visualization:

            menu_view.addAction(
                QAction('Reload', menu_view, triggered=self.reload))

            menu_view.addAction(
                QAction('Save capture', menu_view, triggered=self.save_img))
            if not debugger:
                menu_view.addSeparator()
                menu_view.addAction(
                    QAction('Close', menu_view, triggered=self.remove))
        else:
            menu_view.setEnabled(False)
        self.menubar.addMenu(menu_view)

        # DPI
        # menu_dpi = QMenu("DPI (60)")
        # if visualization:

            # for dpi in [60, 70, 80, 90, 100, 110, 120, 130]:
                # menu_dpi.addAction(QAction(
                    # f'{dpi}', menu_dpi, checkable=True, triggered=self.set_dpi(menu_dpi, f'{dpi}', dpi)))
                # if dpi == 60:
                    # self.set_dpi(menu_dpi, f'{dpi}', dpi)()
        # else:
            # menu_dpi.setEnabled(False)
        # self.menubar.addMenu(menu_dpi)

        self.main.INTERACTIVE = {}
        if interact_content:
            self.build_interactive(interact_content)

    # ----------------------------------------------------------------------
    def build_interactive(self, items: Sequence[str, List[str], str, str, bool]) -> None:
        """"""
        for item in items:

            if item[0] == '#':
                continue

            name, values, default, _, exclusive = item
            menu_ = QMenu(f'{name} ({default})')

            if exclusive:
                action_group = QActionGroup(menu_)
                action_group.setExclusive(True)

            for value in values:

                if exclusive:
                    # action = ag.addAction(QAction(
                        # f'{value}', menu_, checkable=True, checked=True))
                    action = QAction(
                        f'{value}', menu_, checkable=True, triggered=self.set_interactive(menu_, name, value))
                    action_group.addAction(action)
                else:
                    action = QAction(f'{value}', menu_, checkable=True,
                                     triggered=self.set_interactive_non_exclusive(menu_, name, value))
                menu_.addAction(action)

                if value == default:
                    action.setChecked(True)
                self.main.INTERACTIVE[name] = default
            self.menubar.addMenu(menu_)

    # ----------------------------------------------------------------------
    def set_interactive_non_exclusive(self, menu_, name: str, value: int) -> Callable:
        """"""
        def wrap():
            if value == 'All':
                [action.setChecked(False) for action in menu_.actions()]
                [action.setChecked(True) for action in menu_.actions(
                ) if action.text() == f'{value}']
            else:
                menu_.actions()[0].setChecked(False)

            self.main.INTERACTIVE[name] = ','.join([
                action.text() for action in menu_.actions() if action.isChecked()])
            menu_.setTitle(f'{name} ({value})')
        return wrap

    # ----------------------------------------------------------------------
    def set_interactive(self, menu_, name: str, value: int) -> Callable:
        """Set the DPI value for matplotlib figures."""
        def wrap():
            [action.setChecked(False) for action in menu_.actions()]
            [action.setChecked(
                True) for action in menu_.actions() if action.text() == f'{value}']
            self.main.INTERACTIVE[name] = value
            menu_.setTitle(f'{name} ({value})')
        return wrap

    # ----------------------------------------------------------------------
    def build_menu_stimuli(self, visualization: bool, debugger: bool = False) -> None:
        """Menu for stimuli delivery."""
        self.menubar = QMenuBar(self)
        self.menubar.clear()

        self.accent_menubar = QMenuBar(self)
        self.accent_menubar.clear()
        self.menubar.setMinimumWidth(1e4)

        # Title
        if debugger:
            menu_stimuli = QMenu(f"Debugging: {visualization}")
        else:
            if visualization:
                menu_stimuli = QMenu(visualization + ' 🞃')
            else:
                menu_stimuli = QMenu('Stimuli' + ' 🞃')

        for viz, path in self.extensions_list:
            if viz != visualization:
                menu_stimuli.addAction(QAction(viz, menu_stimuli,
                                               triggered=self.set_extension(path)))
        # self.menubar.addMenu(menu_stimuli)
        self.accent_menubar.addMenu(menu_stimuli)

        self.accent_menubar.setStyleSheet(f"""
        QMenuBar::item {{
            background-color: {os.getenv('QTMATERIAL_PRIMARYCOLOR', '#ffffff')};
            color: {os.getenv('QTMATERIAL_PRIMARYTEXTCOLOR', '#ffffff')};
        }}

        """)

        # self.menubar.addMenu(menu_stimuli)
        self.menubar.setCornerWidget(
            self.accent_menubar, corner=Qt.TopLeftCorner)

        # View
        menu_view = QMenu("View")
        if visualization:

            menu_view.addAction(
                QAction('Reload', menu_view, triggered=self.reload))

            if debugger:
                menu_view.addAction(
                    QAction('Open subwindow delivery', menu_view, triggered=self.open_subwindow))
            if not debugger:
                menu_view.addSeparator()
                menu_view.addAction(
                    QAction('Close', menu_view, triggered=self.remove))
        else:
            menu_view.setEnabled(False)
        self.menubar.addMenu(menu_view)

    # # ----------------------------------------------------------------------
    # def set_dpi(self, menu_dpi, text: str, dpi: int) -> Callable:
        # """Set the DPI value for matplotlib figures."""
        # def wrap():
            # [action.setChecked(False) for action in menu_dpi.actions()]
            # [action.setChecked(
                # True) for action in menu_dpi.actions() if action.text() == text]
            # self.main.DPI = dpi
            # menu_dpi.setTitle(f'DPI ({dpi})')
        # return wrap

    # ----------------------------------------------------------------------
    def set_extension(self, visualization: str) -> Callable:
        """Load extension from menu."""
        def wrap():
            self.load_extension(visualization)
        return wrap

    # ----------------------------------------------------------------------
    def build_menu_timeloclk(self, visualization: bool, debugger: Optional[bool] = False) -> None:
        """"""
        self.menubar = QMenuBar(self)
        self.menubar.clear()
        self.menubar.setMinimumWidth(1e4)

        self.accent_menubar = QMenuBar(self)

        # Title
        if debugger:
            menu_stimuli = QMenu(f"Debugging: {visualization}")
        else:
            if visualization:
                menu_stimuli = QMenu(f'{visualization } 🞃')
            else:
                menu_stimuli = QMenu('Timelock analysis 🞃')

        # Add visualizations
        for viz, path in self.extensions_list:
            if viz != visualization:
                menu_stimuli.addAction(QAction(viz, menu_stimuli,
                                               triggered=self.set_extension(path)))

        self.accent_menubar.addMenu(menu_stimuli)

        # Menu with accent color
        self.accent_menubar.setStyleSheet(f"""
        QMenuBar::item {{
            background-color: {os.getenv('QTMATERIAL_PRIMARYCOLOR', '#ffffff')};
            color: {os.getenv('QTMATERIAL_PRIMARYTEXTCOLOR', '#ffffff')};
            }}""")

        # Set the menu in first position
        self.menubar.setCornerWidget(
            self.accent_menubar, corner=Qt.TopLeftCorner)

        # View
        menu_view = QMenu("View")
        if visualization:

            menu_view.addAction(
                QAction('Reload', menu_view, triggered=self.reload))

            # menu_view.addAction(
                # QAction('Save capture', menu_view, triggered=self.save_img))
            # if not debugger:
                # menu_view.addSeparator()
                # menu_view.addAction(
                    # QAction('Close', menu_view, triggered=self.remove))
        else:
            menu_view.setEnabled(False)
        self.menubar.addMenu(menu_view)
