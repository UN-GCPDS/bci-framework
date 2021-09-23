"""
================================
Data Analysis and Visualizations
================================

Kafka consumers and transformers with data processing and outputs.
"""

import os
import sys

import psutil
from PySide2.QtCore import QTimer, Qt
from PySide2.QtGui import QColor, QBrush
from PySide2.QtWidgets import QTableWidgetItem

from ..config_manager import ConfigManager
from ..extensions_handler import ExtensionWidget
from ..subprocess_handler import run_subprocess


########################################################################
class Visualization:
    """Real-time data analysis and visualizations."""

    # ----------------------------------------------------------------------
    def __init__(self, core):
        """"""
        self.parent_frame = core.main
        self.core = core
        self.config = ConfigManager()

        self.process_status_timer = QTimer()
        self.process_status_timer.timeout.connect(self.update_data_analysis)
        self.process_status_timer.setInterval(1000)

        self.on_focus()
        self.add_subwindow()
        self.connect()
        # self.build_analysis()

    # ----------------------------------------------------------------------
    def connect(self) -> None:
        """Connect events."""
        self.parent_frame.pushButton_load_visualizarion.clicked.connect(
            self.add_subwindow)
        self.parent_frame.pushButton_visualizations_remove_all.clicked.connect(
            self.remove_all)
        self.parent_frame.pushButton_visualizations_reload_all.clicked.connect(
            self.reload_all)
        self.parent_frame.tableWidget_anlaysis.itemChanged.connect(
            self.analisys_status_update)
        self.parent_frame.pushButton_visualizations_stop_all.clicked.connect(
            self.stop_all_scripts)
        self.parent_frame.pushButton_visualizations_restart_all.clicked.connect(
            self.restart_running_scripts)

    # ----------------------------------------------------------------------
    def on_focus(self) -> None:
        """Update mdiAreas."""
        self.parent_frame.mdiArea.tileSubWindows()

        self.visualizations_list = []
        for i in range(self.parent_frame.listWidget_projects_visualizations.count()):
            item = self.parent_frame.listWidget_projects_visualizations.item(
                i)
            if item.text().startswith('_'):
                continue
            if item.text().startswith('Tutorial :'):
                continue
            self.visualizations_list.append([item.text(), item.path])
        self.build_analysis()

    # ----------------------------------------------------------------------
    def reload_all(self) -> None:
        """Reload all patitions."""
        for sub in self.parent_frame.mdiArea.subWindowList():
            sub.reload()

    # ----------------------------------------------------------------------
    def remove_all(self) -> None:
        """Remove all patitions."""
        for sub in self.parent_frame.mdiArea.subWindowList():
            sub.remove()
        QTimer().singleShot(100, self.widgets_set_enabled)

    # ----------------------------------------------------------------------
    def add_subwindow(self) -> None:
        """Add new patition."""
        sub = ExtensionWidget(
            self.parent_frame.mdiArea, mode='visualization', extensions_list=self.visualizations_list)
        self.parent_frame.mdiArea.addSubWindow(sub)
        sub.show()
        self.parent_frame.mdiArea.tileSubWindows()
        sub.update_menu_bar()
        sub.loaded = self.widgets_set_enabled

        sub.destroyed.connect(self.widgets_set_enabled)
        self.widgets_set_enabled()

    # ----------------------------------------------------------------------
    def widgets_set_enabled(self) -> None:
        """Update action buttons."""
        subwindows = len(self.parent_frame.mdiArea.subWindowList()) != 0
        self.parent_frame.pushButton_visualizations_remove_all.setEnabled(
            subwindows)

        self.parent_frame.pushButton_visualizations_reload_all.setEnabled(
            False)

        for sub in self.parent_frame.mdiArea.subWindowList():
            if getattr(sub, 'stream_subprocess', False):
                self.parent_frame.pushButton_visualizations_reload_all.setEnabled(
                    True)
                break

    # ----------------------------------------------------------------------
    def build_analysis(self) -> None:
        """"""
        columns = ['Data analisys',
                   'PID',
                   'CPU%',
                   'Memory',
                   'Status',
                   ]

        start_index = self.parent_frame.tableWidget_anlaysis.rowCount() - 1
        if self.parent_frame.tableWidget_anlaysis.rowCount() == 0:
            self.parent_frame.tableWidget_anlaysis.clear()
            self.parent_frame.tableWidget_anlaysis.setRowCount(0)
            self.parent_frame.tableWidget_anlaysis.setColumnCount(
                len(columns))
            self.parent_frame.tableWidget_anlaysis.setHorizontalHeaderLabels(
                columns)
            already_items = []

            to_remove = []
            to_add = [self.parent_frame.listWidget_projects_analysis.item(i).text(
            ) for i in range(self.parent_frame.listWidget_projects_analysis.count())]

        else:
            # start_index = 0
            already_items = [self.parent_frame.tableWidget_anlaysis.item(
                i, 0).text() for i in range(self.parent_frame.tableWidget_anlaysis.rowCount())]
            new_ones = [self.parent_frame.listWidget_projects_analysis.item(
                i).text() for i in range(self.parent_frame.listWidget_projects_analysis.count())]

            to_remove = set(already_items) - set(new_ones)
            to_add = set(new_ones) - set(already_items)

        for i, script_name in enumerate(to_add):

            if script_name.startswith('_'):
                continue

            if script_name in already_items:
                continue

            # if item.text().startswith('Tutorial |'):
                # continue

            self.parent_frame.tableWidget_anlaysis.insertRow(start_index + i)
            for j in range(len(columns)):

                if j == 0:
                    item = QTableWidgetItem(script_name)
                    item.setCheckState(Qt.Unchecked)
                    item.is_running = False
                    item.path = self.core.projects.normalize_path(
                        item.text())
                else:
                    item = QTableWidgetItem()

                if 0 < j < 4:
                    item.setTextAlignment(Qt.AlignCenter)

                item.setFlags(item.flags() & ~Qt.ItemIsEditable
                              & ~Qt.ItemIsSelectable)
                self.parent_frame.tableWidget_anlaysis.setItem(
                    start_index + i, j, item)

                self.parent_frame.tableWidget_anlaysis.cellWidget(
                    start_index + i, j)

        for script_name in to_remove:
            for i in range(self.parent_frame.tableWidget_anlaysis.rowCount()):
                item = self.parent_frame.tableWidget_anlaysis.item(i, 0)
                if item.text() == script_name:
                    if not item.checkState() == Qt.Checked:
                        self.parent_frame.tableWidget_anlaysis.removeRow(i)
                    else:
                        item.to_remove = True
                    break

        self.parent_frame.tableWidget_anlaysis.sortByColumn(0)

    # ----------------------------------------------------------------------
    def analisys_status_update(self, item) -> None:
        """"""
        if item.column() != 0:
            return

        if item.checkState() == Qt.Checked:
            self.start_script(item)
        else:
            self.stop_script(item)

    # ----------------------------------------------------------------------
    def stop_script(self, item) -> None:
        """"""
        if hasattr(item, 'subprocess'):
            item.subprocess.terminate()
            del item.subprocess
            item.setCheckState(Qt.Unchecked)
            self.update_row_information(item.row(), '', '', '', 'Terminated')

            if hasattr(item, 'to_remove'):
                self.parent_frame.tableWidget_anlaysis.removeRow(item.row())

    # ----------------------------------------------------------------------
    def start_script(self, item) -> None:
        """"""
        script = item.path
        item.setCheckState(Qt.Checked)
        item.subprocess = run_subprocess([sys.executable, os.path.join(
            self.core.projects.projects_dir, script, 'main.py')])
        if not self.process_status_timer.isActive():
            self.process_status_timer.start()

    # ----------------------------------------------------------------------
    def update_data_analysis(self) -> None:
        """"""
        running = 0
        for row in range(self.parent_frame.tableWidget_anlaysis.rowCount()):
            item = self.parent_frame.tableWidget_anlaysis.item(row, 0)
            if hasattr(item, 'subprocess'):

                try:
                    process = psutil.Process(item.subprocess.pid)
                    pid = str(item.subprocess.pid)
                    memory = f"{process.memory_info().vms / (1024):.0f} K"
                    cpu = f"{process.cpu_percent()}%"
                    status = 'Running...'
                    running += 1
                except:
                    item.setCheckState(Qt.Unchecked)
                    pid = ''
                    memory = ""
                    cpu = ""
                    status = 'Finalized'

                if process.memory_info().vms == 0:
                    pid = ''
                    memory = ""
                    cpu = ""
                    status = 'Finalized'
                    self.stop_script(item)

                self.update_row_information(row, pid, cpu, memory, status)

        if not running:
            self.process_status_timer.stop()

        enable = self.process_status_timer.isActive()
        self.parent_frame.pushButton_visualizations_stop_all.setEnabled(
            enable)
        self.parent_frame.pushButton_visualizations_restart_all.setEnabled(
            enable)

    # ----------------------------------------------------------------------
    def update_row_information(self, row, pid: str, cpu: str, memory: str, status: str) -> None:
        """"""
        item1 = self.parent_frame.tableWidget_anlaysis.item(row, 1)
        item1.setText(pid)
        item2 = self.parent_frame.tableWidget_anlaysis.item(row, 2)
        item2.setText(cpu)
        item2 = self.parent_frame.tableWidget_anlaysis.item(row, 3)
        item2.setText(memory)
        item3 = self.parent_frame.tableWidget_anlaysis.item(row, 4)
        item3.setText(status)

        if status in ['Terminated', 'Finalized']:
            item3.setBackgroundColor(QColor(220, 53, 69, 30))
        elif status in ['Running...']:
            item3.setBackgroundColor(QColor(63, 197, 94, 30))

    # ----------------------------------------------------------------------
    def stop_all_scripts(self) -> None:
        """"""
        for row in range(self.parent_frame.tableWidget_anlaysis.rowCount()):
            item = self.parent_frame.tableWidget_anlaysis.item(row, 0)
            if hasattr(item, 'subprocess'):
                self.stop_script(item)

    # ----------------------------------------------------------------------
    def restart_running_scripts(self) -> None:
        """"""
        for row in range(self.parent_frame.tableWidget_anlaysis.rowCount()):
            item = self.parent_frame.tableWidget_anlaysis.item(row, 0)
            if hasattr(item, 'subprocess'):
                self.stop_script(item)
                self.start_script(item)



