# from PySide2.QtCore import QTimer
from .visualization_widget import VisualizationWidget

# # from datetime import datetime
# # import time
# # import sys
# # import os

# # from bci_framework.subprocess_script import run_subprocess

########################################################################


class Visualization:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, parent, core):
        """Constructor"""

        self.parent = parent
        # self.core = core
        self.connect()
        # self.hide_preview()

    # ----------------------------------------------------------------------

    def connect(self):
        """"""
        self.parent.pushButton_add_visualizarion.clicked.connect(
            self.add_subwindow)
        # self.parent.pushButton_record.toggled.connect(self.record_signal)

    # # ----------------------------------------------------------------------
    # def record_signal(self, toggled):
        # """"""
        # if toggled:
            # self.start_record = datetime.now()
            # self.timer = QTimer()
            # self.timer.setInterval(1000 / 1)
            # self.timer.timeout.connect(self.update_timer)
            # self.timer.start()
            # self.subprocess_script = run_subprocess(
                # [sys.executable, os.path.join('transformers', 'record.py')])

        # else:
            # self.timer.stop()
            # self.parent.pushButton_record.setText(f"Record")
            # self.subprocess_script.kill()

    # # ----------------------------------------------------------------------
    # def update_timer(self):
        # """"""
        # now = datetime.now()
        # delta = now - self.start_record

        # n_time = datetime.strptime(str(delta), '%H:%M:%S.%f').time()

        # self.parent.pushButton_record.setText(
            # f"Recording [{n_time.strftime('%H:%M:%S')}]")

    # ----------------------------------------------------------------------
    def add_subwindow(self):
        """"""

        sub = VisualizationWidget(self.parent)
        sub.update_visualizations_list()

        self.parent.mdiArea.addSubWindow(sub)
        sub.show()

        # # sub.moveToThread(self.my_thread)
        # # self.my_thread.start()

        self.parent.mdiArea.tileSubWindows()

