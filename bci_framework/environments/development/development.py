import os
# import traceback
# from importlib import reload
import psutil

from PySide2.QtCore import QTimer, Qt
from PySide2.QtGui import QTextCursor

from bci_framework.subprocess_script import LoadSubprocess


########################################################################
class Development:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, core):
        """Constructor"""

        self.parent = core.main
        self.core = core

        self.parent.pushButton_stop_preview.hide()

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

        self.parent.textEdit_linenumber.setStyleSheet("""
        QTextEdit {
        background-color: #263238;
        color: white;
        font-weight: normal;
        font-family: 'monospace';
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

        self.parent.pushButton_script_preview.clicked.connect(
            self.run_preview)
        self.parent.pushButton_stop_preview.clicked.connect(
            self.stop_preview)
        self.parent.tabWidget_project.currentChanged.connect(self.check_tabs)

    # ----------------------------------------------------------------------
    def check_tabs(self, event=None):
        """"""
        if self.parent.tabWidget_project.count():
            self.parent.tabWidget_project.show()
            self.parent.textEdit_linenumber.show()
            self.parent.widget_new_project.hide()
        else:
            self.parent.tabWidget_project.hide()
            self.parent.textEdit_linenumber.hide()
            self.parent.widget_new_project.show()

    # ----------------------------------------------------------------------
    def hide_preview(self):
        """"""
        self.parent.splitter_preview.moveSplitter(
            self.parent.splitter_preview.getRange(1)[1], 1)
        self.handle_width = self.parent.splitter_preview.handleWidth()
        self.parent.splitter_preview.setHandleWidth(0)

    # ----------------------------------------------------------------------
    def show_preview(self):
        """"""
        self.parent.splitter_preview.moveSplitter(
            self.parent.splitter_preview.getRange(1)[1] // 2, 1)
        self.parent.splitter_preview.setHandleWidth(self.handle_width)
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
        module = os.path.join(self.parent.treeWidget_project.path, os.path.split(
            self.parent.treeWidget_project.path)[1])
        # self.parent.plainTextEdit_preview_log.hide()
        self.parent.plainTextEdit_preview_log.setPlainText('')
        self.parent.pushButton_stop_preview.show()
        self.parent.pushButton_script_preview.hide()

        self.preview_stream = LoadSubprocess(
            self.parent, f'{module}.py', debug=True, web_view='gridLayout_webview', endpoint='delivery')
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

        self.parent.pushButton_stop_preview.hide()
        self.parent.pushButton_script_preview.show()
        self.hide_preview()

    # ----------------------------------------------------------------------
    def update_log(self):
        """"""
        if line := self.preview_stream.stdout.readline(timeout=0.01):
            self.parent.plainTextEdit_preview_log.moveCursor(QTextCursor.End)
            self.parent.plainTextEdit_preview_log.insertPlainText(
                line.decode())
        self.timer.singleShot(1000 / 60, self.update_log)

    # ----------------------------------------------------------------------
    def save_all_files(self):
        """"""
        for i, tab_text in enumerate(map(self.parent.tabWidget_project.tabText, range(self.parent.tabWidget_project.count()))):
            if tab_text.endswith('*'):
                editor = self.parent.tabWidget_project.widget(i)

                with open(editor.path, 'w') as file:
                    file.write(editor.toPlainText())

                    self.parent.tabWidget_project.setTabText(
                        i, tab_text.strip('*'))

        self.timer_autosave.singleShot(10000, self.save_all_files)
