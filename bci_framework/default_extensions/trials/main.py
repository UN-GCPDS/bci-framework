from bci_framework.extensions.visualizations import EEGStream
from bci_framework.extensions.data_analysis import marker_slicing
from bci_framework.extensions import properties as prop

import logging
import numpy as np
from datetime import datetime
import seaborn as snb

from scipy.signal import savgol_filter

from simple_pid import PID

MAX_LATENCY = 150
BUFFER = 15

pid = PID(Kp=0.5, Ki=0.07, Kd=0.0001, setpoint=0,
          sample_time=None, output_limits=(-MAX_LATENCY, MAX_LATENCY))
# pid = PID(Kp=1, Ki=0.07, Kd=0.0001, setpoint=0,
          # sample_time=None, output_limits=(-MAX_LATENCY, MAX_LATENCY))
# pid = PID(Kp=1, Ki=0.4, Kd=0.05, setpoint=0,
          # sample_time=None, output_limits=(-MAX_LATENCY, MAX_LATENCY))
# pid = PID(Kp=1, Ki=0.07, Kd=0.01, setpoint=0,
          # sample_time=None, output_limits=(-MAX_LATENCY, MAX_LATENCY))


########################################################################
class Stream(EEGStream):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """"""
        super().__init__(enable_produser=True)

        # self.N = int(prop.SAMPLE_RATE / prop.STREAMING_PACKAGE_SIZE)

        self.axis_wave = self.add_subplot(221)
        self.axis_hist = self.add_subplot(223)
        self.axis_log = self.add_subplot(222)
        self.axis_time = self.add_subplot(224)

        self.subplots_adjust(hspace=0.3)

        # self.wave_line = self.axis_wave.plot([0], [0])[0]
        # self.wave_line2 = self.axis_wave.vline()[0]

        self.latency_time = self.axis_time.plot(
            [0], [0], linewidth=3, linestyle='', marker='x', color='k')[0]
        self.latency_time_filtered = self.axis_time.plot([0], [0], color='C0')[
            0]

        self.timestamp_rises = np.array([])

        self.markers_timestamps = []

        self.latencies = [0]
        self.latency_correction = 0

        self.create_buffer(BUFFER, resampling=1000, fill=-1, aux_shape=2)

        self.stream()

    # ----------------------------------------------------------------------

    @marker_slicing(['MARKER'], t0=-3, t1=3)
    def stream(self, aux, marker, marker_datetime):
        """"""

        logging.warning('OK')

        self.axis_wave.clear()
        # t = np.linspace(-1, 1, aux.shape[1])

        logging.warning(f'AUX: {aux[0].shape}')
        # logging.warning(f'EEG: {eeg.shape}')

        self.axis_wave.plot(aux[0])
        self.feed()


if __name__ == '__main__':
    Stream()






















