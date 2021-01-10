import sys


class fake:
    def __getattr__(self, attr):
        return None


brython = ['Widgets', 'Tone']

for module in brython:
    sys.modules[f"bci_framework.extensions.stimuli_delivery.utils.{module}"] = fake()
