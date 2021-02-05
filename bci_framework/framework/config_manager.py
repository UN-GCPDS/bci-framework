import os
from configparser import ConfigParser

from PySide2 import QtWidgets


########################################################################
class ConfigManager(ConfigParser):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, filename='.bciframework'):
        """Constructor"""
        super().__init__()

        if os.path.isabs(filename):
            self.filename = filename
        else:
            user_dir = os.path.join(os.getenv('BCISTREAM_HOME'))
            os.makedirs(user_dir, exist_ok=True)
            self.filename = os.path.join(user_dir, filename)

        self.load()

    # ----------------------------------------------------------------------
    def load(self):
        """"""
        assert os.path.exists(
            self.filename), f'"{self.filename} does not exist!"'

        self.read(self.filename)

    # ----------------------------------------------------------------------
    def set(self, section, option, value='', save=False):
        """"""
        if not self.has_section(section):
            self.add_section(section)
        super().set(section, option, value)
        if save:
            self.save()

    # ----------------------------------------------------------------------
    def get(self, section, option, default=None, *args, **kwargs):
        """"""
        if self.has_option(section, option):
            return super().get(section, option, *args, **kwargs)
        else:
            self.set(section, option, default)
            return default

    # ----------------------------------------------------------------------
    def save(self):
        """"""
        with open(self.filename, 'w') as configfile:
            self.write(configfile)

    # ----------------------------------------------------------------------
    def save_widgets(self, section, config):
        """"""
        for option in config:
            widget = config[option]

            # QComboBox
            if isinstance(widget, QtWidgets.QComboBox):
                self.set(section, option, widget.currentText())

            # QCheckBox
            elif isinstance(widget, QtWidgets.QCheckBox):
                self.set(section, option, str(widget.isChecked()))

            else:
                widget

        self.save()

    # ----------------------------------------------------------------------
    def load_widgets(self, section, config):
        """"""
        for option in config:
            widget = config[option]

            if not (self.has_section(section) and self.has_option(section, option)):
                return

            # QComboBox
            if isinstance(widget, QtWidgets.QComboBox):
                widget.setCurrentText(self.get(section, option))
            # QCheckBox
            elif isinstance(widget, QtWidgets.QCheckBox):
                widget.setChecked(self.getboolean(section, option))

            else:
                widget

    # ----------------------------------------------------------------------
    def connect_widgets(self, method, config):
        """"""
        for option in config:
            widget = config[option]

            # QComboBox
            if isinstance(widget, QtWidgets.QComboBox):
                widget.activated.connect(method)
            # QCheckBox
            elif isinstance(widget, QtWidgets.QCheckBox):
                widget.clicked.connect(method)

            else:
                widget



