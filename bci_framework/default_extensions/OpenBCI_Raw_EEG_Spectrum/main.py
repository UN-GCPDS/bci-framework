"""
=======
Raw EEG
=======
"""

from bci_framework.extensions.visualizations import EEGStream, Widgets, interact
from bci_framework.extensions.data_analysis import loop_consumer, fake_loop_consumer
from bci_framework.extensions import properties as prop
import numpy as np
from scipy.fftpack import fft, fftfreq, fftshift
from scipy.signal import welch

from gcpds.filters import frequency as flt
import logging


########################################################################
class RawEEG(EEGStream, Widgets):

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        BUFFER = 2
        
        self.enable_widgets('BandPass', 'Notch', 'Mode', 'Channels')
    
        self.mode = 'Fourier'

        self.axis = self.add_subplot(111)
        self.create_buffer(BUFFER, aux_shape=3, fill=0)

        window = BUFFER * prop.SAMPLE_RATE
        self.W = fftshift(fftfreq(window, 1 / prop.SAMPLE_RATE))

        a = np.empty(window)
        a.fill(0)
        self.lines = [self.axis.plot(self.W, a.copy(), '-',)[0]
                      for i in range(len(prop.CHANNELS))]

        self.axis.set_xlim(0, 100)
        self.axis.set_ylim(0, 1)
        self.axis.set_xlabel('Frequency [Hz]')
        self.axis.set_ylabel('Amplitude')

        self.stream()


    # ----------------------------------------------------------------------
    @loop_consumer('eeg')
    def stream(self, frame):

        if frame % 3:
            return
            
        channels = self.widget_value['Channels']
        
        logging.warning(str(channels))

        eeg = self.buffer_eeg
        self.axis.collections.clear()

        if self.mode == 'Fourier':
            EEG = fftshift(np.abs(fft(eeg, axis=1)))
            self.W = fftshift(fftfreq(EEG.shape[1], 1 / prop.SAMPLE_RATE))

        elif self.mode == 'Welch':
            EEG, self.W = welch(eeg, prop.SAMPLE_RATE, window='flattop',
                                nperseg=100, scaling='spectrum', axis=-1)

        EEG = EEG / EEG.max()
        for i, line in enumerate(self.lines):
            
            if channels != 'All' and not i in channels:
                line.set_data([], [])
                continue
            
            if self.mode == 'Fourier':
                line.set_data(self.W, EEG[i])
                self.axis.fill_between(
                    self.W, EEG[i], 0, facecolor=f'C{i}', alpha=0.1)

            elif self.mode == 'Welch':
                line.set_data(self.W, EEG[i])

        self.axis.set_xlim(0, 100)

        self.feed()

  
    # ----------------------------------------------------------------------
    @interact('Mode', ('Fourier', 'Welch'), 'Fourier')
    def interact_mode(self, mode):
        """"""
        self.mode = mode


if __name__ == '__main__':
    RawEEG()
