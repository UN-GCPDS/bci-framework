"""
=====================
Configuration Manager
=====================
"""

import os
from configparser import ConfigParser
from typing import Optional, Dict, TypeVar, Callable

from PySide2 import QtWidgets

WIDGET = TypeVar('QWidget')


########################################################################
class ConfigManager(ConfigParser):
    """File based configurations manager."""

    # ----------------------------------------------------------------------
    def __init__(self, filename='.bciframework'):
        """"""
        super().__init__()

        if os.path.isabs(filename):
            self.filename = filename
        else:
            user_dir = os.path.join(os.getenv('BCISTREAM_HOME'))
            os.makedirs(user_dir, exist_ok=True)
            self.filename = os.path.join(user_dir, filename)

        self.load()

    # ----------------------------------------------------------------------
    def load(self) -> None:
        """Load the filename with configirations."""
        assert os.path.exists(
            self.filename), f'"{self.filename} does not exist!"'

        self.read(self.filename)

    # ----------------------------------------------------------------------
    def set(self, section: str, option: str, value: Optional[str] = '', save: Optional[bool] = False) -> None:
        """Write and save configuration option."""
        if not self.has_section(section):
            self.add_section(section)
        super().set(section, option, value)
        if save:
            self.save()

    # ----------------------------------------------------------------------
    def get(self, section: str, option: str, default: Optional[str] = None, *args, **kwargs) -> None:
        """Read a configuration value, if not exists then save the default."""
        if self.has_option(section, option):
            return super().get(section, option, *args, **kwargs)
        else:
            self.set(section, option, default)
            return default

    # ----------------------------------------------------------------------
    def save(self) -> None:
        """Save configurations."""
        with open(self.filename, 'w') as configfile:
            self.write(configfile)

    # ----------------------------------------------------------------------
    def save_widgets(self, section: str, config: Dict[str, WIDGET]) -> None:
        """Automatically save values from widgets."""
        for option in config:
            widget = config[option]

            # QComboBox
            if isinstance(widget, QtWidgets.QComboBox):
                self.set(section, option, widget.currentText())

            # QCheckBox
            elif isinstance(widget, QtWidgets.QCheckBox):
                self.set(section, option, str(widget.isChecked()))

            # QSpinBox
            elif isinstance(widget, QtWidgets.QSpinBox):
                self.set(section, option, str(widget.value()))

            else:
                widget

        self.save()

    # ----------------------------------------------------------------------
    def load_widgets(self, section: str, config: Dict[str, WIDGET]) -> None:
        """Automatically load values from configurations and set them in widgets."""
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
            # QSpinBox
            elif isinstance(widget, QtWidgets.QSpinBox):
                widget.setValue(int(self.get(section, option)))
            else:
                widget

    # ----------------------------------------------------------------------
    def connect_widgets(self, method: Callable, config: Dict[str, WIDGET]) -> None:
        """Automatically connect widgets with events."""
        for option in config:
            widget = config[option]

            # QComboBox
            if isinstance(widget, QtWidgets.QComboBox):
                widget.activated.connect(method)
            # QCheckBox
            elif isinstance(widget, QtWidgets.QCheckBox):
                widget.clicked.connect(method)
            # QSpinBox
            elif isinstance(widget, QtWidgets.QSpinBox):
                widget.valueChanged.connect(method)
            else:
                widget



