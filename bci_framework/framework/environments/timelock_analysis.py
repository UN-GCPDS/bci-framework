
from PySide6.QtCore import QTimer

from ..extensions_handler import ExtensionWidget


########################################################################
class TimeLockAnalysis:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, core):
        """Constructor"""

        self.parent_frame = core.main
        self.core = core

        # self.parent_frame.pushButton_stop_calibration.setVisible(False)
        # self.parent_frame.mdiArea_latency.hide()
        # self.parent_frame.label_calibration_image.show()

        self.connect()

    # ----------------------------------------------------------------------
    def connect(self):
        """"""

    # ----------------------------------------------------------------------
    def show_fullscreen(self):
        """"""
        if self.parent_frame.dockWidget_global.isVisible():
            self.parent_frame.dockWidget_global.hide()
            self.parent_frame.toolBar_Environs.hide()
            self.parent_frame.toolBar_Documentation.hide()
            self.parent_frame.showFullScreen()
            self.parent_frame.statusBar().hide()
        else:
            self.parent_frame.dockWidget_global.show()
            self.parent_frame.toolBar_Environs.show()
            self.parent_frame.toolBar_Documentation.show()
            self.parent_frame.showMaximized()
            self.parent_frame.statusBar().show()

    # ----------------------------------------------------------------------
    def on_focus(self):
        """"""
        self.timelock_list = []
        self.update_timelock_list()

        if not self.parent_frame.mdiArea_timelock.subWindowList():
            self.build_dashboard()
        else:
            QTimer().singleShot(100, self.parent_frame.mdiArea_timelock.tileSubWindows)

    # ----------------------------------------------------------------------
    def update_timelock_list(self):
        """"""
        for i in range(self.parent_frame.listWidget_projects_timelock.count()):
            item = self.parent_frame.listWidget_projects_timelock.item(i)
            if item.text().startswith('__'):
                continue
            if item.text().startswith('Tutorial:'):
                continue
            self.timelock_list.append([item.text(), item.path])

    # ----------------------------------------------------------------------
    def build_dashboard(self) -> None:
        """Create the experiments selector."""
        sub = ExtensionWidget(
            self.parent_frame.mdiArea_timelock, extensions_list=self.timelock_list, mode='timelock')
        self.parent_frame.mdiArea_timelock.addSubWindow(sub)
        sub.show()

        sub.update_menu_bar()
        self.parent_frame.mdiArea_timelock.tileSubWindows()
        # QTimer().singleShot(100, self.parent_frame.mdiArea_timelock.tileSubWindows)

