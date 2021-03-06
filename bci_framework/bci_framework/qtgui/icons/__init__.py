import os
from qt_material.resources import ResourseGenerator

from PySide2.QtCore import QDir


# ----------------------------------------------------------------------
def generate_icons():
    """"""
    source = os.path.join(os.path.dirname(__file__), 'source')
    resources = ResourseGenerator(primary=os.getenv('QTMATERIAL_PRIMARYCOLOR'),
                                  secondary=os.getenv('QTMATERIAL_SECONDARYCOLOR'),
                                  disabled=os.getenv('QTMATERIAL_SECONDARYLIGHTCOLOR'),
                                  source=source,
                                  parent='bci_framework',
                                  )
    resources.generate()

    QDir.addSearchPath('bci', resources.index)
    QDir.addSearchPath('icons-dark', os.path.join(os.path.dirname(__file__), 'icons-dark'))
