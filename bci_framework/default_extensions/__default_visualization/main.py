from bci_framework.extensions.visualizations import EEGStream, loop_consumer, fake_loop_consumer
from bci_framework.extensions import properties as prop


########################################################################
class Stream(EEGStream):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)

        self.axis, self.time, self.lines = self.create_lines(
            time=-30, window=1000)

        self.axis.set_title('Raw EEG')
        self.axis.set_xlabel('Time')
        self.axis.set_ylabel('Channels')
        self.axis.grid(True)

        self.axis.set_ylim(0, len(prop.CHANNELS) + 1)
        self.axis.set_yticks(range(1, len(prop.CHANNELS) + 1))
        self.axis.set_yticklabels(prop.CHANNELS.values())

        self.create_buffer(30, samples=1000)
        self.stream()

    # ----------------------------------------------------------------------
    @fake_loop_consumer('eeg')
    def stream(self):
        """"""
        eeg = self.buffer_eeg_resampled

        for i, line in enumerate(self.lines):
            line.set_data(self.time, eeg[i] + 1 + i)

        # self.send_command('Q')
        self.feed()


if __name__ == '__main__':
    Stream(enable_produser=False)
