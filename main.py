# The purpose of this file is works as main entry point for debugger.

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'local'))

from bci_framework.__main__ import main
main()
