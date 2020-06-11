from configparser import ConfigParser
import os
import shutil

from PySide2 import QtWidgets


########################################################################
class ConfigManager(ConfigParser):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, filename='.bciframework'):
        """Constructor"""
        super().__init__()

        self.filename = os.path.abspath(filename)
        self.load()

    # ----------------------------------------------------------------------
    def load(self):
        """"""
        if os.path.exists(self.filename):
            self.read(self.filename)
        else:
            shutil.copyfile('bciframework.default', self.filename)
        self.read(self.filename)

    # ----------------------------------------------------------------------
    def set(self, section, option, value=''):
        """"""
        if not self.has_section(section):
            self.add_section(section)

        return super().set(section, option, value)

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



