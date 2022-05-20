"""
==================================================
Pain quantification - brain connectivity functions
==================================================

Viviana Gomez Orozco, Automatics Research Group
Universidad Tecnológica de Pereira, Pereira - Colombia
vigomez@utp.edu.co

Yeison Nolberto Cardona Alvarez, Signal Processing and Recognition Group
Universidad Nacional de Colombia, Manizales - Colombia
yencardonaal@unal.edu.co
"""

import numpy as np
from scipy.signal import butter, filtfilt
from scipy import signal

# import matplotlib.pyplot as plt
import logging
import sys

from bci_framework.extensions.data_analysis import (
    DataAnalysis,
    Feedback,
    loop_consumer,
)

from bci_framework.extensions import properties as prop

import numpy.typing as npt
from typing import Literal, TypeAlias, Union, Optional

eeg_channels: TypeAlias = list[str]
eeg_signal: TypeAlias = npt.NDArray


########################################################################
class NFB_powerbands:
    """"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        ch_labels: eeg_channels,
        fs: Union[int, float],
        target_ch_labels: eeg_channels,
        method: Literal['fourier', 'welch'],
        bands: dict[str, tuple[list[int], Literal['increase', 'decrease']]],
        baseline_count: int,
    ):
        """Constructor"""

        self.bands = bands
        self.method = method
        self.target_ch_labels = target_ch_labels
        self.fs = fs
        self.ch_labels = ch_labels

        self.historical = {}
        self.baseline_count = baseline_count

    # ----------------------------------------------------------------------
    def add(self, data: np.ndarray) -> None:
        """From a `(channels, time)` array, calculate the connectivity.

        This vector is the historical and wil be used to calculate the baseline.
        """
        value = self.compute(data)

        for k in value:
            self.historical.setdefault(k, []).append(value[k])
            if len(self.historical[k]) > self.baseline_count:
                self.historical[k].pop(0)

    # ---------------------------------------------------------------------
    def compute(self, data: eeg_signal) -> dict[str]:
        """
        Compute the alpha, beta and theta bands power spectral density (PSD) for 2 seconds long EEG trial (epoch).

        Parameters
        ----------
        data (channels,samples):
            Input time series (number of channels x number of samples)
        ch_labels:
            EEG channel labels
        fs:
            Sampling frequency (Hz)
        target_ch_labels:
            Channel combination
        method:
            Method to estimate power spectral density (Fourier or Welch)

        Returns
        -------
        powerband
            Alpha, Beta and Theta PSD
        """
        rhyt = list(self.bands.keys())

        feats = []
        nyq = 0.5 * self.fs
        for k in self.bands:
            band = np.array(self.bands[k][0])
            b, a = butter(
                5, band / nyq, btype='band'
            )  # fast enough to generate parameters each time
            feats.append(filtfilt(b, a, data, axis=-1))

        try:
            target_ch = [
                self.ch_labels.index(ch) for ch in self.target_ch_labels
            ]
        except ValueError:
            logging.error("Error! Required channel not found...")
            sys.exit()

        PSD = {}

        match self.method:

            case 'fourier':
                # Compute and plot the power spectral density (PSD) using Fourier Transform
                freqs = np.fft.rfftfreq(self.fs, 1 / self.fs)
                for r, feat in enumerate(feats):
                    psdr = abs(
                        np.fft.rfft(
                            feat[target_ch, :].flatten(),
                            n=self.fs,
                            axis=-1,
                        )
                    )
                    PSD[rhyt[r]] = psdr

            case 'welch':
                # Compute and plot the power spectral density (PSD) using Welch's method
                for r, feat in enumerate(feats):
                    freqs, psdr = signal.welch(
                        feat[target_ch, :].flatten(),
                        self.fs,
                        nperseg=self.fs,
                        scaling='spectrum',
                    )
                    PSD[rhyt[r]] = psdr

        return PSD

    # ----------------------------------------------------------------------
    def compare(
        self, psd_band: dict[str], psd_baseline: dict[str]
    ) -> list[bool]:
        """"""

        feedback = {}
        for band in self.bands:
            if (
                np.mean(psd_baseline[band]) > np.mean(psd_band[band])
                and self.bands[band][1] == 'increase'
            ):
                feedback[band] = [True, self.bands[band][1]]
            elif (
                np.mean(psd_baseline[band]) < np.mean(psd_band[band])
                and self.bands[band][1] == 'decrease'
            ):
                feedback[band] = [True, self.bands[band][1]]
            else:
                feedback[band] = [False, self.bands[band][1]]

        return feedback

    # ----------------------------------------------------------------------
    def freeze_baseline(self):
        """"""
        # self.baseline_ = np.mean(self.historical)
        self.baseline_ = {
            k: np.mean(self.historical[k], axis=0) for k in self.historical
        }
        # logging.warning(f'Baseline')

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
            return self.compare(
                {k: self.historical[k][-1] for k in self.historical},
                baseline,
            )
        else:
            return None


########################################################################
class PowerBandNeuroFeedback(DataAnalysis):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)

        self.feedback = Feedback(self, 'PowerBandNeuroFeedback')
        self.feedback.on_feedback(self.on_feedback)

        self.configuration = {}

        # Buffer
        self.create_buffer(30, fill=0)
        self.stream()

    # ----------------------------------------------------------------------
    def on_feedback(self, **configuration) -> None:
        """Configure the generator based on the stimuli delivery parameters."""

        if command := configuration.get('command', None):
            getattr(self, command)()
            return

        self.configuration = {
            'status': configuration.get('status', 'off'),
            'method': configuration.get('method', None),
            'window_analysis': configuration.get('window_analysis', None),
            'sliding_data': configuration.get('sliding_data', None),
            'baseline_packages': configuration.get(
                'baseline_packages', None
            ),
            'channels': configuration.get('channels', None),
            'target_channels': configuration.get('target_channels', None),
            'sample_rate': configuration.get('sample_rate', None),
            'bands': configuration.get('bands', '[]'),
        }

        if self.configuration['status'] == 'off':
            return

        self.neurofeedback = NFB_powerbands(
            baseline_count=self.configuration['baseline_packages'],
            ch_labels=self.configuration['channels'],
            target_ch_labels=self.configuration['target_channels'],
            fs=self.configuration['sample_rate'],
            method=self.configuration['method'],
            bands=self.configuration['bands'],
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

        window = self.buffer_eeg[
            :,
            -int(prop.SAMPLE_RATE * self.configuration['window_analysis']) :,
        ]
        self.neurofeedback.add(window)

        if not self.neurofeedback.baseline:
            return

        feedback = {
            'feedback': self.neurofeedback.value,
        }
        self.feedback.write(feedback)


if __name__ == '__main__':
    PowerBandNeuroFeedback(enable_produser=True)
