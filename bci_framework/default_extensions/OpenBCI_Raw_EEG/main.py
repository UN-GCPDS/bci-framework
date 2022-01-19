"""
=======
Raw EEG
=======
"""

from bci_framework.extensions.visualizations import EEGStream, Widgets
from bci_framework.extensions.data_analysis import loop_consumer, fake_loop_consumer
from bci_framework.extensions import properties as prop

import numpy as np
import logging


########################################################################
class RawEEG(EEGStream, Widgets):

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        DATAWIDTH = 1000
        BUFFER = 30

        self.enable_widgets('BandPass',
                            'Notch',
                            'Scale',
                            'Channels',
                            'Substract',
                            'Window time',
                            )

        self.axis, self.time, self.lines = self.create_lines(
            time=-BUFFER, window=DATAWIDTH)
        self.axis.set_title('Raw EEG')
        self.axis.set_xlabel('Time')
        self.axis.set_ylabel('Channels')
        self.axis.grid(True)
        self.axis.set_ylim(0, len(prop.CHANNELS) + 1)
        self.axis.set_yticklabels(prop.CHANNELS.values())

        self.create_buffer(BUFFER, aux_shape=3, resampling=DATAWIDTH, fill=0)

        self.stream()

    # ----------------------------------------------------------------------
    @loop_consumer('eeg')
    def stream(self, latency):
        """"""
        scale = self.widget_value['Scale']
        substract = self.widget_value['Substract']
        channels = self.widget_value['Channels']
        window_time = self.widget_value['Window time']

        logging.warning(f'Latency: {latency}')

        eeg = self.buffer_eeg[:, -window_time * prop.SAMPLE_RATE:]
        t = np.linspace(-window_time, 0, eeg.shape[1])
        self.axis.set_xlim(-window_time, 0)

        for i, line in enumerate(self.lines):

            if channels != 'All' and not i in channels:
                line.set_data([], [])
                continue

            if substract == 'none':
                line.set_data(t, (eeg[i]) + scale * i)
            elif substract == 'channel mean':
                line.set_data(t, (eeg[i] - np.mean(eeg[i])) + scale * i)
            elif substract == 'global mean':
                line.set_data(t, (eeg[i] - np.mean(eeg)) + scale * i)
            elif (substract == 'Cz') and ('Cz' in prop.CHANNELS.values()):
                index = list(prop.CHANNELS.values()).index('Cz')
                line.set_data(t, (eeg[i] - eeg[index - 1]) + scale * i)

        self.feed()


if __name__ == '__main__':
    RawEEG()
