"""
=====================
OpenBCI auxiliar data
=====================
"""

from bci_framework.extensions.visualizations import EEGStream, Widgets
from bci_framework.extensions.data_analysis import loop_consumer, fake_loop_consumer
from bci_framework.extensions import properties as prop
import numpy as np

import logging


########################################################################
class OpenBCIAuxiliarData(EEGStream, Widgets):

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        DATAWIDTH = 1000
        WINDOW = 30
        
        self.enable_widgets(
                            'Window time',
                            )
    

        axis, self.time, self.lines = self.create_lines(
            time=-DATAWIDTH, mode=prop.BOARDMODE, window=DATAWIDTH)

        axis.set_title(f'Raw - {prop.BOARDMODE}')
        axis.set_xlabel('Time')
        
        axis.set_xlim(-WINDOW, 0)
        self.axis = axis

   
        self.create_buffer(WINDOW, resampling=DATAWIDTH, fill=0, aux_shape=len(self.lines))
        self.stream()
        
    
    # ----------------------------------------------------------------------
    @loop_consumer('aux')
    def stream(self):
        
        
        t = self.widget_value['Window time']
        
        aux = self.buffer_aux[:,-t*prop.SAMPLE_RATE:]
        
        time = np.linspace(-t, 0, aux.shape[1])        
        self.axis.set_xlim(-t, 0)
         
        for i, line in enumerate(self.lines):
            line.set_data(time, aux[i])
            
        self.feed()


if __name__ == '__main__':
    OpenBCIAuxiliarData()
