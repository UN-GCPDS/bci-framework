"""
=====================
OpenBCI auxiliar data
=====================

"""

from bci_framework.extensions.visualizations import EEGStream
from bci_framework.extensions.data_analysis import fake_loop_consumer
from bci_framework.extensions import properties as prop
import numpy as np

import logging


########################################################################
class OpenBCIAuxiliarData(EEGStream):

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        DATAWIDTH = 1000
    
        axis, self.time, self.lines = self.create_lines(time=-30, mode=prop.BOARDMODE, window=DATAWIDTH)
        
        axis.set_title(f'Raw - {prop.BOARDMODE}')
        axis.set_xlabel('Time')
        
        if prop.BOARDMODE == 'default':
            axis.set_ylabel('G')
            axis.legend(['x', 'y', 'z'])
            
        elif prop.BOARDMODE == 'analog': 
            axis.set_ylabel('Analog Read')
            
            if prop.CONNECTION == 'wifi':
                axis.legend(['A5 (D11)', 'A6 (D12)'])  # WiFi shield board use A7
            else:
                axis.legend(['A5 (D11)', 'A6 (D12)', 'A7 (D13)'])
                
        elif prop.BOARDMODE == 'digital': 
            axis.set_ylabel('Digital Read')
            
            if prop.CONNECTION == 'wifi':
                axis.legend(['D11', 'D12', 'D17'])  # WiFi shield board use D13 and D18
            else:
                axis.legend(['D11', 'D12', 'D13', 'D17', 'D18'])


        self.create_buffer(30, resampling=DATAWIDTH, fill=np.nan)
        self.stream()

    # ----------------------------------------------------------------------
    @fake_loop_consumer('eeg')
    def stream(self):
        aux = self.buffer_aux_resampled
        
        for i, line in enumerate(self.lines):
            line.set_data(self.time, aux[i])
        self.feed()


if __name__ == '__main__':
    OpenBCIAuxiliarData()
