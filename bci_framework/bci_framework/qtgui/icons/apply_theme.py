import os
from pyside_material import set_icons_theme

QRC_FILE = 'resource.qrc'


# # create_qrc(qrc)
# RCC = '/usr/lib/python3.8/site-packages/PySide2/rcc'
RCC = 'rcc -g python --no-compress --verbose'
command = f"{RCC} {QRC_FILE}  -o {QRC_FILE.replace('.qrc', '_rc.py')}"
os.system(command)

set_icons_theme(theme='dark_cyan.xml',
                resource=f"{QRC_FILE.replace('.qrc', '_rc.py')}",
                output='resource_rc.py')
