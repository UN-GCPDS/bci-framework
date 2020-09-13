import os

from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QMdiSubWindow, QMenu, QAction
from PySide2.QtCore import QTimer, Qt

from ...subprocess_script import LoadSubprocess


########################################################################
class VisualizationWidget(QMdiSubWindow):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, parent, *args, **kwargs):
        """Constructor"""
        super().__init__(*args, **kwargs)

        self.main = QUiLoader().load('bci_framework/qtgui/visualization_widget.ui', self)
        self.parent = parent
        self.current_viz = None

        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWidget(self.main)

        self.main.setStyleSheet("""
        QWidget.main_frame {
            border: 2px solid red;
        }
        """)

        # self.update_visualizations_list()

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
        QTimer().singleShot(1000 / 50, self.parent.mdiArea.tileSubWindows)

    # ----------------------------------------------------------------------

    def reload(self):
        """"""
        self.stop_preview()
        if self.current_viz:
            self.load_visualization(self.current_viz)

    # # ----------------------------------------------------------------------
    # def update_visualizations_list(self):
        # """"""
        # for i in range(self.parent.listWidget_projects.count()):
            # item = self.parent.listWidget_projects.item(i)
            # if item.icon_name == 'icon_viz':
            # self.main.comboBox_visualizations.addItem(item.text())

        # self.main.pushButton_execute.clicked.connect(lambda evt: self.load_visualization(
            # self.main.comboBox_visualizations.currentText()))

    # ----------------------------------------------------------------------
    def load_visualization(self, visualization):
        """"""
        self.current_viz = visualization
        module = os.path.join('default_projects', visualization, 'main.py')
        self.preview_stream = LoadSubprocess(
            self.main, module, debug=False, web_view='gridLayout_webview')
        # self.main.comboBox_visualizations.hide()
        # self.main.pushButton_execute.hide()
        # self.main.label_stream.show()

    # ----------------------------------------------------------------------
    def stop_preview(self):
        """"""
        if hasattr(self, 'preview_stream'):
            self.preview_stream.stop_preview()

    # # ----------------------------------------------------------------------
    # def update_log(self):
        # """"""
        # if line := self.preview_stream.stdout.readline(timeout=0.01):
            # self.main.plainTextEdit_log.moveCursor(QTextCursor.End)
            # self.main.plainTextEdit_log.insertPlainText(line.decode())
        # self.timer.singleShot(1000 / 60, self.update_log)
