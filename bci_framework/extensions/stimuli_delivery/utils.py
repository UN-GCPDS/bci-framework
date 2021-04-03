"""
=====
Utils
=====

The trick behind `Brython-Radiant <https://radiant-framework.readthedocs.io/en/latest/>`_
is make the same script callable from Python and Brython, so, the Python modules
must be faked.
"""

import sys


class fake:
    def __getattr__(self, attr):
        return None


brython = ['Widgets', 'Tone', 'Units', 'keypress']
for module in brython:
    sys.modules[f"bci_framework.extensions.stimuli_delivery.utils.{module}"] = fake(
    )
