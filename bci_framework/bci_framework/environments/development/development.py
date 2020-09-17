import os
# import traceback
# from importlib import reload
import psutil

from PySide2.QtCore import QTimer, Qt
from PySide2.QtGui import QTextCursor

from ...subprocess_script import LoadSubprocess


########################################################################
class Development:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, core):
        """Constructor"""

        self.parent_frame = core.main
        self.core = core

        self.parent_frame.pushButton_stop_preview.hide()

        self.timer = QTimer()
        self.timer_autosave = QTimer()

        self.connect()
        self.hide_preview()

        self.save_all_files()
        self.build_linenumber()

        self.check_tabs()

    # ----------------------------------------------------------------------
    def build_linenumber(self):
        """"""

        self.parent_frame.textEdit_linenumber.setStyleSheet("""
        QTextEdit {
        background-color: #263238;
        color: white;
        font-weight: normal;
        font-family: 'DejaVu Sans Mono';
        font-size: 15px;
        line-height: 15px;
        border: 0px solid #4f5b62;
        border-right: 10px solid #4f5b62;
        border-radius: 0px;
        padding: 8px 0px ;
        padding-top: 41px;

        }
        """)

        # self.parent.textEdit_linenumber.setAlignment(Qt.AlignRight)

    # ----------------------------------------------------------------------
    def connect(self):
        """Constructor"""

        self.parent_frame.pushButton_script_preview.clicked.connect(
            self.run_preview)
        self.parent_frame.pushButton_stop_preview.clicked.connect(
            self.stop_preview)
        self.parent_frame.tabWidget_project.currentChanged.connect(
            self.check_tabs)

    # ----------------------------------------------------------------------
    def check_tabs(self, event=None):
        """"""
        if self.parent_frame.tabWidget_project.count():
            self.parent_frame.tabWidget_project.show()
            self.parent_frame.textEdit_linenumber.show()
            self.parent_frame.widget_new_project.hide()
        else:
            self.parent_frame.tabWidget_project.hide()
            self.parent_frame.textEdit_linenumber.hide()
            self.parent_frame.widget_new_project.show()

    # ----------------------------------------------------------------------
    def hide_preview(self):
        """"""
        self.parent_frame.splitter_preview.moveSplitter(
            self.parent_frame.splitter_preview.getRange(1)[1], 1)
        self.handle_width = self.parent_frame.splitter_preview.handleWidth()
        self.parent_frame.splitter_preview.setHandleWidth(0)

    # ----------------------------------------------------------------------
    def show_preview(self):
        """"""
        self.parent_frame.splitter_preview.moveSplitter(
            self.parent_frame.splitter_preview.getRange(1)[1] // 2, 1)
        self.parent_frame.splitter_preview.setHandleWidth(self.handle_width)
        # self.parent.splitter_preview_log.moveSplitter(
        # self.parent.splitter_preview_log.getRange(1)[1] // 2, 1)

    # # ----------------------------------------------------------------------
    # def save_script(self):
        # """"""
        # editor = self.parent.textEdit
        # script = editor.toPlainText()

        # if editor.path:
        # with open(editor.path, 'w') as file:
        # file.write(script)

    # ----------------------------------------------------------------------
    def run_preview(self):
        """"""
        self.save_all_files()
        self.stop_preview()
        # module = os.path.join(self.parent.treeWidget_project.path, os.path.split(
        # self.parent.treeWidget_project.path)[1])
        module = os.path.join(
            self.parent_frame.treeWidget_project.path, 'main.py')
        # self.parent.plainTextEdit_preview_log.hide()
        self.parent_frame.plainTextEdit_preview_log.setPlainText('')
        self.parent_frame.pushButton_stop_preview.show()
        self.parent_frame.pushButton_script_preview.hide()

        self.preview_stream = LoadSubprocess(
            self.parent_frame, module, debug=True, web_view='gridLayout_webview', endpoint='delivery')
        self.timer.singleShot(100, self.update_log)
        self.show_preview()

        current_process = psutil.Process()
        children = current_process.children(recursive=True)
        for child in children:
            print('Child pid is {}'.format(child.pid))

    # ----------------------------------------------------------------------
    def stop_preview(self):
        """"""
        if hasattr(self, 'preview_stream'):
            self.preview_stream.stop_preview()

        self.parent_frame.pushButton_stop_preview.hide()
        self.parent_frame.pushButton_script_preview.show()
        self.hide_preview()

    # ----------------------------------------------------------------------
    def update_log(self):
        """"""
        if not hasattr(self.preview_stream, 'stdout'):
            return
        if line := self.preview_stream.stdout.readline(timeout=0.01):
            self.parent_frame.plainTextEdit_preview_log.moveCursor(
                QTextCursor.End)
            self.parent_frame.plainTextEdit_preview_log.insertPlainText(
                line.decode())
        self.timer.singleShot(1000 / 60, self.update_log)

    # ----------------------------------------------------------------------
    def save_all_files(self):
        """"""
        for i, tab_text in enumerate(map(self.parent_frame.tabWidget_project.tabText, range(self.parent_frame.tabWidget_project.count()))):
            if tab_text.endswith('*'):
                editor = self.parent_frame.tabWidget_project.widget(i)

                with open(editor.path, 'w') as file:
                    file.write(editor.toPlainText())

                    self.parent_frame.tabWidget_project.setTabText(
                        i, tab_text.strip('*'))

        self.timer_autosave.singleShot(10000, self.save_all_files)
