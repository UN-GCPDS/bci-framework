from bci_framework.extensions.visualizations import EEGStream
from bci_framework.extensions.visualizations.utils import loop_consumer, fake_loop_consumer
from bci_framework.extensions import properties as prop

import logging


########################################################################
class Stream(EEGStream):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """"""
        super().__init__()

        self.L = 1000
        t = 30

        self.create_buffer(t, aux_shape=3, fill=10)

        self.axis, self.time, self.lines = self.create_lines(mode='eeg', time=-t, window=self.L, cmap='cool')

        self.axis.set_title('Raw EEG')
        self.axis.set_xlabel('Time [s]')
        self.axis.set_ylabel('Channel')

        self.axis.set_ylim(0, len(prop.CHANNELS) + 1)
        self.axis.set_yticks(range(1, len(prop.CHANNELS) + 1))
        self.axis.set_yticklabels(prop.CHANNELS.values())

        self.stream()

    # ----------------------------------------------------------------------
    @fake_loop_consumer
    def stream(self, data, topic: str, frame: int):
        """"""

        if topic == "eeg":

            # eeg = self.buffer_eeg
            eeg = self.resample(self.buffer_eeg, self.L)
            eeg = self.centralize(eeg, normalize=True)

            for i, line in enumerate(self.lines):
                line.set_data(self.time, eeg[i] + 1 + i)

            self.feed()

        elif topic == "marker":
            data = data.value
            logging.warning(data)


if __name__ == '__main__':
    Stream()
