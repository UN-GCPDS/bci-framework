"""
=======
Raw EEG
=======
"""

from bci_framework.extensions.visualizations import EEGStream, interact
from bci_framework.extensions.data_analysis import loop_consumer, fake_loop_consumer
from bci_framework.extensions import properties as prop
from gcpds.filters import frequency as flt
import numpy as np

import logging

REVERSE_PLOT = True


notch_filters = ('None', '50 Hz', '60 Hz')

bandpass_filters = ('None', 'delta', 'theta', 'alpha', 'beta', 
                    '5-45 Hz', '3-30 Hz', '4-40 Hz', '2-45 Hz', '1-50 Hz', 
                    '7-13 Hz', '15-50 Hz', '1-100 Hz', '5-50 Hz',)

scale = ('50 µV', '100 µV',  '200 µV', '400 µV', '800 µV')



########################################################################
class RawEEG(EEGStream):

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        DATAWIDTH = 1000
        BUFFER = 30

        if REVERSE_PLOT:
            self.axis, self.time, self.lines = self.create_lines(mode='eeg',
                                                            time=BUFFER, window=DATAWIDTH)
        else:
            self.axis, self.time, self.lines = self.create_lines(
                time=-BUFFER, window=DATAWIDTH)
        self.axis.set_title('Raw EEG')
        self.axis.set_xlabel('Time')
        self.axis.set_ylabel('Channels')
        self.axis.grid(True)
        self.axis.set_ylim(0, len(prop.CHANNELS) + 1)
        self.axis.set_yticklabels(prop.CHANNELS.values())

        self.create_buffer(BUFFER, aux_shape=3, resampling=DATAWIDTH, fill=0)
        
        if REVERSE_PLOT:
            self.reverse_buffer(self.axis)

        self.scale = 100

        self.stream()

    # ----------------------------------------------------------------------
    def autoscale(self, data):
        """"""
        data = data - data.mean()
        data = data / (data.max() - data.min())
        return data

    # ----------------------------------------------------------------------
    @loop_consumer('eeg')
    def stream(self):
        eeg = self.buffer_eeg_resampled
        
        for i, line in enumerate(self.lines):
            line.set_data(self.time, eeg[i] + self.scale*i)
            
        self.feed()

    # ----------------------------------------------------------------------
    @interact('BandPass', bandpass_filters, 'None')
    def interact_bandpass(self, bandpass):
        """"""        
        if bandpass == 'None':
            self.remove_transformers(['bandpass'])
        elif bandpass in ['delta', 'theta', 'alpha', 'beta']:
            bandpass = getattr(flt, bandpass)
            self.add_transformers({'bandpass': bandpass})
        else:
            bandpass = bandpass.replace(' Hz', '').replace('-', '')
            bandpass = getattr(flt, f'band{bandpass}')
            self.add_transformers({'bandpass': bandpass})

    # ----------------------------------------------------------------------
    @interact('Notch', notch_filters, 'None')
    def interact_notch(self, notch):
        """"""
        if notch == 'None':
            self.remove_transformers(['notch'])
        else:
            notch = notch.replace(' Hz', '')
            notch = getattr(flt, f'notch{notch}')
            self.add_transformers({'notch': notch})
            
            
    # ----------------------------------------------------------------------
    @interact('Scale', scale, '100 µV')
    def interact_scale(self, scale):
        """"""
        
        self.scale = int(scale.replace(' µV', ''))
        self.axis.set_ylim(-self.scale, self.scale*len(prop.CHANNELS))
        self.axis.set_yticks(np.linspace(0, (len(prop.CHANNELS) - 1) * self.scale, len(prop.CHANNELS)))
        
        if REVERSE_PLOT:
            self.reverse_buffer(self.axis, min=-self.scale, max=len(prop.CHANNELS) * self.scale)
            
            

if __name__ == '__main__':
    RawEEG()
