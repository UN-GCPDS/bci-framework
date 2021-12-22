
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
    def on_focus(self):
        """"""
        self.timelock_list = []
        self.update_timelock_list()

        if not self.parent_frame.mdiArea_timelock.subWindowList():
            self.build_dashboard()

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
        self.parent_frame.mdiArea_timelock.tileSubWindows()

        # sub.update_ip = self.update_ip
        sub.update_menu_bar()
        # sub.loaded = self.widgets_set_enabled

        # QTimer().singleShot(100, self.widgets_set_enabled)
