from .properties import properties
from .utils import loop_consumer, fake_loop_consumer, timeit
from .figure import Figure

import sys
import os


Tone = None
Widgets = None

sys.path.append(os.path.join(os.path.dirname(__file__), 'fake_modules'))

