"""
===========
Development
===========

This environment use the integrated development environt to code a test new
extensions.
"""

import os
from typing import TypeVar

from PySide2.QtCore import QTimer
from PySide2.QtGui import QTextCursor

from ..extensions_handler import ExtensionWidget
from ..editor import Autocompleter


PATH = TypeVar('Path')


########################################################################
class Development:
    """Main Action with an integrated development environ."""

    # ----------------------------------------------------------------------
    def __init__(self, core):
        """Constructor"""

        self.parent_frame = core.main
        self.core = core

        self.parent_frame.pushButton_stop_preview.hide()

        self.log_timer = QTimer()
        self.log_timer.timeout.connect(self.update_log)
        self.log_timer.setInterval(500)

        self.timer_autosave = QTimer()
        self.timer_autosave.timeout.connect(self.save_all_files)
        self.timer_autosave.setInterval(5000)
        self.timer_autosave.start()

        self.connect()
        self.hide_preview()

        self.build_linenumber()

    # ----------------------------------------------------------------------
    def build_linenumber(self) -> None:
        """The same linenumber is used for all editors."""

        self.parent_frame.textEdit_linenumber.setStyleSheet(f"""
        QTextEdit {{
        background-color: {os.environ.get('QTMATERIAL_SECONDARYDARKCOLOR')};
        color: {os.environ.get('QTMATERIAL_SECONDARYTEXTCOLOR')};
        font-weight: normal;
        font-family: 'DejaVu Sans Mono';
        font-size: 15px;
        line-height: 15px;
        border: 0px solid {os.environ.get('QTMATERIAL_SECONDARYLIGHTCOLOR')};
        border-right: 10px solid {os.environ.get('QTMATERIAL_SECONDARYLIGHTCOLOR')};
        border-radius: 0px;
        padding: 8px 0px ;
        padding-top: 41px;

        }}
        """)

    # ----------------------------------------------------------------------
    def connect(self) -> None:
        """Connect events."""
        self.parent_frame.pushButton_script_preview.clicked.connect(
            self.start_preview)
        self.parent_frame.pushButton_stop_preview.clicked.connect(
            self.stop_preview)

    # ----------------------------------------------------------------------
    def hide_preview(self) -> None:
        """Expand editor."""
        if self.mode != 'analysis':
            self.parent_frame.mdiArea_development.hide()
            self.parent_frame.splitter_preview.moveSplitter(
                self.parent_frame.splitter_preview.getRange(1)[1], 1)
            self.handle_width = self.parent_frame.splitter_preview.handleWidth()
            self.parent_frame.splitter_preview.setHandleWidth(0)

    # ----------------------------------------------------------------------
    def show_preview(self) -> None:
        """Show previsualization."""
        if self.mode != 'analysis':
            self.parent_frame.mdiArea_development.show()
            self.parent_frame.splitter_preview.moveSplitter(
                self.parent_frame.splitter_preview.getRange(1)[1] // 2, 1)
            self.parent_frame.splitter_preview.setHandleWidth(self.handle_width)

    # ----------------------------------------------------------------------
    def get_project(self) -> PATH:
        """Return the path of the current project."""
        return os.path.split(self.parent_frame.treeWidget_project.path)[1]

    # ----------------------------------------------------------------------
    def start_preview(self) -> None:
        """Initialize the previsualization and the debugger."""
        self.show_preview()
        self.parent_frame.mdiArea_development.tileSubWindows()
        self.save_all_files()
        self.parent_frame.plainTextEdit_preview_log.setPlainText('')
        self.sub.load_extension(self.get_project(), debugger=self)
        self.log_timer.start()

        self.parent_frame.pushButton_stop_preview.show()
        self.parent_frame.pushButton_script_preview.hide()

    # ----------------------------------------------------------------------
    def open_subwindow(self) -> None:
        """Open an auxiliar window for stimuli delivery."""
        url = self.sub.stream_subprocess.url
        self.core.stimuli_delivery.open_subwindow(
            url.replace('/dashboard', '/'))

    # ----------------------------------------------------------------------
    def on_focus(self) -> None:
        """Set the correct projects widget."""
        self.parent_frame.mdiArea_development.tileSubWindows()
        self.parent_frame.tabWidget_widgets.setCurrentWidget(
            self.parent_frame.tab_projects)
        self.parent_frame.actionDevelopment.setEnabled(
            self.parent_frame.tabWidget_project.count())

    # ----------------------------------------------------------------------
    def build_preview(self) -> None:
        """Update mdiAreas."""
        self.stop_preview()
        for sub in self.parent_frame.mdiArea_development.subWindowList():
            sub.remove()

        if sub := getattr(self, 'sub', False):
            sub.deleteLater()

        self.sub = ExtensionWidget(
            self.parent_frame.mdiArea_development, [], mode=self.mode)
        self.parent_frame.mdiArea_development.addSubWindow(self.sub)
        self.sub.show()
        self.parent_frame.mdiArea_development.tileSubWindows()

    # ----------------------------------------------------------------------
    def stop_preview(self) -> None:
        """Stop subprocess."""
        self.log_timer.stop()
        if hasattr(self, 'sub'):
            self.sub.stop_preview()

        self.parent_frame.pushButton_stop_preview.hide()
        self.parent_frame.pushButton_script_preview.show()
        self.hide_preview()

    # ----------------------------------------------------------------------
    def update_log(self) -> None:
        """Write logs into debugger.

        Logging messages could be from Python or JavaScript (Bryhon).
        """

        if not hasattr(self.sub, 'stream_subprocess'):
            # self.timer.singleShot(50, self.update_log)
            return

        if not hasattr(self.sub.stream_subprocess, 'stdout'):
            self.sub.stream_subprocess.start_debug()
            return

        warning = self.parent_frame.checkBox_log_warning.isChecked()
        error = self.parent_frame.checkBox_log_error.isChecked()
        lines = []

        if hasattr(self.sub.stream_subprocess, 'subprocess_script'):
            if line := self.sub.stream_subprocess.subprocess_script.nb_stdout.readline(timeout=0.01):
                lines.append(line.decode())
        if line := self.sub.stream_subprocess.stdout.readline(timeout=0.01):
            lines.append(line.decode())

        filter_ = [
            'using indexedDB',
            'Synchronous XMLHttpRequest',
            'Error 404 means',
            'The AudioContext',
            'WARNING:tornado.access:404',
            'upgrade needed',
        ]

        for line in lines:
            if not line.strip():
                continue

            trace = 'Traceback (most recent call last):'
            if trace in line:
                line = line[line.find(trace):]

            c = False
            for f in filter_:
                if f in line:
                    c = True
                    break
            if c:
                continue

            self.parent_frame.plainTextEdit_preview_log.moveCursor(
                QTextCursor.End)
            if line.startswith('WARNING') and warning:
                self.parent_frame.plainTextEdit_preview_log.insertPlainText(
                    line)
            elif line.startswith('ERROR') and error:
                self.parent_frame.plainTextEdit_preview_log.insertPlainText(
                    line)
            elif not line.startswith('WARNING') and not line.startswith('ERROR'):
                self.parent_frame.plainTextEdit_preview_log.insertPlainText(
                    line)

            if not line.endswith('\n'):
                self.parent_frame.plainTextEdit_preview_log.insertPlainText(
                    '\n')

        if lines:
            self.log_timer.setInterval(10)
        else:
            self.log_timer.setInterval(500)

    # ----------------------------------------------------------------------
    def save_all_files(self) -> None:
        """Save all opened files."""
        for i, tab_text in enumerate(map(self.parent_frame.tabWidget_project.tabText, range(self.parent_frame.tabWidget_project.count()))):
            if tab_text.endswith('*'):
                editor = self.parent_frame.tabWidget_project.widget(i)

                with open(editor.path, 'w') as file:
                    content = editor.toPlainText()
                    file.write(content)

                    if not editor.completer:
                        if 'bci_framework.extensions.stimuli_delivery' in content:
                            completer = Autocompleter(mode='stimuli')
                            editor.set_completer(completer)
                        elif 'bci_framework.projects.figure' in content:
                            completer = Autocompleter(mode='visualization')
                            editor.set_completer(completer)

                    self.parent_frame.tabWidget_project.setTabText(
                        i, tab_text.strip('*'))

    # ----------------------------------------------------------------------
    @property
    def mode(self):
        """"""
        return getattr(self.core.projects, 'mode', None)
