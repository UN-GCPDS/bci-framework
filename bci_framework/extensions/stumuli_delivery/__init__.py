import sys
from .stimuli_delivery import DeliveryInstance, StimuliAPI, StimuliServer


class fake:
    def __getattr__(self, attr):
        return None


brython = ['Widgets', 'Tone']

for module in brython:
    sys.modules[f"bci_framework.extensions.{module}"] = fake()
