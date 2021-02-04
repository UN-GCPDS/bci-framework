import os
import shutil

from PySide2.QtWidgets import QDesktopWidget, QMainWindow
from PySide2.QtUiTools import QUiLoader

from .config_manager import ConfigManager


########################################################################
class ConfigurationFrame(QMainWindow):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        frame = os.path.join(
            os.environ['BCISTREAM_ROOT'], 'bci_framework', 'qtgui', 'configurations.ui')
        self.main = QUiLoader().load(frame)
        self.main.widget_restart.hide()

        self.config = ConfigManager()
        self.original_config = ConfigManager(os.path.join(
            os.environ['BCISTREAM_ROOT'], 'assets', 'bciframework.default'))

        theme = self.config.get('framework', 'theme')
        self.main.radioButton_light.setChecked(theme == 'light')
        self.main.radioButton_dark.setChecked(theme == 'dark')

        self.connect()

    # ----------------------------------------------------------------------
    def show(self):
        """"""
        center = QDesktopWidget().availableGeometry().center()
        geometry = self.main.frameGeometry()
        geometry.moveCenter(center)
        self.main.move(geometry.topLeft())
        self.main.show()

    # ----------------------------------------------------------------------
    def connect(self):
        """"""
        self.main.lineEdit_user_directory.setText(os.environ['BCISTREAM_HOME'])
        self.main.lineEdit_projects_directory.setText(
            os.path.join(os.environ['BCISTREAM_HOME'], 'projects'))
        self.main.lineEdit_records_directory.setText(
            os.path.join(os.environ['BCISTREAM_HOME'], 'records'))

        self.main.radioButton_light.clicked.connect(
            lambda: self.config.set('framework', 'theme', 'light', save=True))
        self.main.radioButton_dark.clicked.connect(
            lambda: self.config.set('framework', 'theme', 'dark', save=True))

        self.main.pushButton_restore_projects.clicked.connect(
            self.restore_projects)
        self.main.pushButton_reset_projects.clicked.connect(self.reset_projects)
        self.main.pushButton_remove_records.clicked.connect(self.remove_records)
        self.main.pushButton_reset_montages.clicked.connect(self.reset_montages)
        self.main.pushButton_reset_connections.clicked.connect(
            self.reset_connections)

    # ----------------------------------------------------------------------
    def restore_projects(self, *args, **kwargs):
        """"""
        shutil.copytree(os.path.join(os.environ['BCISTREAM_ROOT'], 'default_projects'),
                        os.path.join(os.environ['BCISTREAM_HOME'], 'projects'), dirs_exist_ok=True)

    # ----------------------------------------------------------------------
    def reset_projects(self, *args, **kwargs):
        """"""
        shutil.rmtree(os.path.join(os.environ['BCISTREAM_HOME'], 'projects'))
        shutil.copytree(os.path.join(os.environ['BCISTREAM_ROOT'], 'default_projects'),
                        os.path.join(os.environ['BCISTREAM_HOME'], 'projects'))

    # ----------------------------------------------------------------------
    def remove_records(self, *args, **kwargs):
        """"""
        shutil.rmtree(os.path.join(os.environ['BCISTREAM_HOME'], 'records'))

    # ----------------------------------------------------------------------
    def reset_montages(self, *args, **kwargs):
        """"""
        self.reset_section('montages')

    # ----------------------------------------------------------------------
    def reset_connections(self):
        """"""
        self.reset_section('connection')

    # ----------------------------------------------------------------------
    def reset_section(self, section):
        """"""
        self.config.remove_section(section)
        for option in self.original_config.options(section):
            self.config.set(section, option,
                            self.original_config.get(section, option))
        self.config.save()

