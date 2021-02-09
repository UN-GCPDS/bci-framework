"""
============
Environments
============

BCI-Framework includes different environments: (1) An integrated development
environment to create experiments and data analysis, (2) A stimuli delivery
dashboard for performing experiments, and (3) A data analysis with real-time
visualizations and external commands performer.
"""

from .development import Development
from .visualization import Visualization
from .stimuli_delivery import StimuliDelivery
