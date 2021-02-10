import os

from PySide2.QtCore import QDir
from qt_material.resources import ResourseGenerator


# ----------------------------------------------------------------------
def generate_icons() -> None:
    """"""
    source = os.path.join(os.path.dirname(__file__), 'source')
    resources = ResourseGenerator(primary=os.getenv('QTMATERIAL_PRIMARYCOLOR'),
                                  secondary=os.getenv(
                                      'QTMATERIAL_SECONDARYCOLOR'),
                                  disabled=os.getenv(
                                      'QTMATERIAL_SECONDARYLIGHTCOLOR'),
                                  source=source,
                                  parent='bci_framework',
                                  )
    resources.generate()

    QDir.addSearchPath('bci', resources.index)
    QDir.addSearchPath(
        'icons-dark', os.path.join(os.path.dirname(__file__), 'icons-dark'))
