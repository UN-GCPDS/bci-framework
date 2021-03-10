from bci_framework.extensions.visualizations import EEGStream, loop_consumer, fake_loop_consumer
from bci_framework.extensions import properties as prop

import logging
import numpy as np
from datetime import datetime


########################################################################
class Stream(EEGStream):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """"""
        super().__init__(enable_produser=True)

        self.axis, self.time, self.lines = self.create_lines(
            mode='analog', time=-30, window=1000)

        self.timestamp_rises = np.array([])
        # self.create_boundary(self.axis, -0.5, 1.5)

        self.axis.set_title('Raw External inputs')
        self.axis.set_xlabel('Time')
        self.axis.set_ylabel('Inputs')
        self.axis.grid(True)

        self.axis.set_ylim(-0.5, 1.5)

        self.create_buffer(30, resampling=1000)
        self.stream()

    # ----------------------------------------------------------------------
    def get_rises(self, data, timestamp):
        """"""
        data = data.copy()

        data[data > data.mean()] = 1
        data[data < data.mean()] = 0

        diff = np.diff(data, prepend=0)
        diff[diff < 0] = 0
        diff[0] = 0

        return timestamp[np.nonzero(diff)[0]], diff

    # ----------------------------------------------------------------------
    @fake_loop_consumer('eeg', 'marker')
    def stream(self, data, topic, frame):
        """"""

        # if frame % 10 > 0:
            # return

        # logging.warning(f"L: {latency:.2f}")

        if topic == 'eeg':
            aux = -self.buffer_aux_resampled[0]

            aux = aux - aux.min()
            aux = aux / aux.max()

            self.lines[0].set_data(self.time, aux)

            self.timestamp_rises, diff = self.get_rises(
                aux, self.buffer_timestamp_resampled)
            self.lines[1].set_data(self.time, diff)

            # self.plot_boundary(eeg=False, aux=True)
            self.feed()

        elif topic == 'marker' and self.timestamp_rises.size > 0:
            recent = min([abs((datetime.fromtimestamp(t) - datetime.fromtimestamp(
                data.timestamp / 1000)).total_seconds()) for t in self.timestamp_rises])
            logging.warning(f"Latency: {recent}")
            self.send_annotation(f'Latency: {recent:.2f}')
            


if __name__ == '__main__':
    Stream()
