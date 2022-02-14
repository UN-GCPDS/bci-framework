"""
============================
Neuropathic Pain - Generator
============================

"""

import logging
from typing import Optional

import numpy as np
from openbci_stream.utils import autokill_process
autokill_process('NeuropathicPain')

from bci_framework.extensions.data_analysis import DataAnalysis, Feedback, loop_consumer
from bci_framework.extensions import properties as prop

import NeuroFeedbackFunctions as nff


########################################################################
class NeuroFeedback:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, baseline_count: int, ch_labels: list[str], fsample: int):
        """"""
        self.ch_labels = ch_labels
        self.fsample = fsample
        self.historical = []
        self.baseline_count = baseline_count

    # ----------------------------------------------------------------------
    def add(self, data: np.ndarray) -> None:
        """From a `(channels, time)` array, calculate the connectivity.

        This vector is the historical and wil be used to calculate the baseline.
        """

        value = self.calcule(data, self.ch_labels, self.fsample)
        self.historical.append(value)
        if len(self.historical) > self.baseline_count:
            self.historical.pop(0)

    # ----------------------------------------------------------------------
    def freeze_baseline(self) -> None:
        """Calculate the baseline from historical data."""

        self.baseline_ = np.mean(self.historical)
        logging.warning(f'Baseline: {len(self.historical)} {self.baseline}')

    @property
    # ----------------------------------------------------------------------
    def baseline(self) -> Optional[float]:
        """Return the baseline if it exists."""

        if baseline := getattr(self, 'baseline_', None):
            return baseline
        else:
            return None

    # ----------------------------------------------------------------------
    @property
    def value(self) -> Optional[float]:
        """Return the baseline if the baseline exists."""

        if baseline := getattr(self, 'baseline_', None):
            return self.compare(self.historical[-1], baseline)
        else:
            return None


########################################################################
class NeuroFeedbackkTE_PAC(NeuroFeedback):
    """"""
    calcule = lambda cls, *args: nff.neurofeedback_kTE_PAC(*args)
    compare = lambda cls, *args: nff.compare_connectivity_kTE(*args)


########################################################################
class NeuroFeedbackCFD(NeuroFeedback):
    """"""
    calcule = lambda cls, *args: nff.neurofeedback_CFD(*args)
    compare = lambda cls, *args: nff.compare_connectivity_CFD(*args)


########################################################################
class NeuroFeedbackAlphaFz(NeuroFeedback):
    """"""
    calcule = lambda cls, *args: nff.neurofeedback_AlphaFz(*args)
    compare = lambda cls, *args: nff.compare_AlphaFz(*args)


########################################################################
class VWMGenerator(DataAnalysis):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)

        self.feedback = Feedback(self, 'NeuropathicPain')
        self.feedback.on_feedback(self.on_feedback)

        self.configuration = {}

        # Buffer
        self.create_buffer(10, aux_shape=3, fill=0)
        self.stream()

    # ----------------------------------------------------------------------
    def on_feedback(self, **configuration) -> None:
        """Configure the generator based on the stimuli delivery parameters."""

        if command := configuration.get('command', None):
            getattr(self, command)()
            return

        self.configuration = {
            'status': configuration.get('status', 'off'),
            'function': configuration.get('function', None),
            'window_analysis': configuration.get('window_analysis', None),
            'sliding_data': configuration.get('sliding_data', None),
            'baseline_packages': configuration.get('baseline_packages', None),
            'channels': configuration.get('channels', None),
            'sample_rate': configuration.get('sample_rate', None),
        }

        if self.configuration['status'] == 'off':
            return

        match self.configuration['function']:
            case 'KTE':
                logging.warning('Using KTE')
                NeuroFeedbackClass = NeuroFeedbackKTE
            case 'CFD':
                logging.warning('Using CFD')
                NeuroFeedbackClass = NeuroFeedbackCFD
            case 'AlphaFz':
                logging.warning('Using AlphaFz')
                NeuroFeedbackClass = NeuroFeedbackAlphaFz

        self.neurofeedback = NeuroFeedbackClass(
            baseline_count=self.configuration['baseline_packages'],
            ch_labels=self.configuration['channels'],
            fsample=self.configuration['sample_rate']
        )

        self.set_package_size(configuration.get('sliding_data', 1000))

    # ----------------------------------------------------------------------
    def freeze_baseline(self) -> None:
        """Calculate the baseline."""

        self.neurofeedback.freeze_baseline()

    # ----------------------------------------------------------------------
    @loop_consumer('eeg')
    def stream(self, frame) -> None:
        """Consume raw EEG and process the data to generate the feedback."""
        if not self.configuration:
            return

        if self.configuration['status'] == 'off':
            return

        window = self.buffer_eeg[:, -int(prop.SAMPLE_RATE *
                                         self.configuration['window_analysis']):]
        self.neurofeedback.add(window)

        if not self.neurofeedback.baseline:
            return

        feedback = {'feedback': self.neurofeedback.value,
                    'baseline': self.neurofeedback.baseline,
                    # 'size': window.shape,
                    # **self.configuration,
                    }
        self.feedback.write(feedback)


if __name__ == '__main__':
    VWMGenerator(enable_produser=True)
