"""
=======
Raw EEG
=======
"""

from bci_framework.extensions.visualizations import EEGStream, Filters, interact
from bci_framework.extensions.data_analysis import loop_consumer, fake_loop_consumer
from bci_framework.extensions import properties as prop
from gcpds.filters import frequency as flt
import numpy as np

import logging


time = ('30 s', '15 s', '10 s', '1 s')



########################################################################
class RawEEG(EEGStream, Filters):
    
    t_ = 30
    

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        
        self.create_buffer(self.t_+2, aux_shape=3, resampling=1000, fill=0)
        
        self.axis = self.add_subplot(111)
        
        
        self.band_2737 = flt.GenericButterBand(27, 37, fs=250)


        self.stream()


    # ----------------------------------------------------------------------
    @loop_consumer('eeg')
    def stream(self):
        eeg = self.buffer_eeg
        self.axis.cla()
        
         
        
        
        for i in range(3):
            signal = eeg[i][-self.t_*prop.SAMPLE_RATE:]
            
            
            signal = flt.notch60(signal, fs=250)
            signal = self.band_2737(signal, fs=250)
            
            
            t = np.linspace(-self.t_, 0, signal.shape[0])  
            self.axis.plot(t, signal-signal.mean(), label=f'CH{i+1}')
        
        
        # self.axis.set_ylim(signal.min()*1.5, signal.max()*1.5)
        
        self.axis.legend()
        
        
        self.feed()
        
        
        
        
    # ----------------------------------------------------------------------

    @interact('Time', time, '30 s')
    def interact_time(self, time):
        """"""
        
        self.t_ = int(time.replace(' s', ''))



if __name__ == '__main__':
    RawEEG()
