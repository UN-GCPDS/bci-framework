"""The purpose of this file is works as main entry point for debugger.

This package is a named module, it must be called as `python -m bci_framework`
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'local'))

from bci_framework.__main__ import main
main()
