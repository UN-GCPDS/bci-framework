from bci_framework.projects.figure import FigureStream
from bci_framework.projects import properties as prop
from bci_framework.projects.utils import loop_consumer, fake_loop_consumer

import logging
import numpy as np

from gcpds.utils.processing import welch


########################################################################
class Stream(FigureStream):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """"""
        super().__init__()

        self.L = 10
        t = 2
        
        self.create_buffer(t, aux_shape=3, fill=0)

        self.axis, self.time, self.lines = self.create_lines(mode='eeg', time=-t, window=self.L, cmap='cool', fill=0)

        self.axis.set_title('Raw EEG')
        self.axis.set_xlabel('Time [s]')   
        self.axis.set_ylabel('Channel')    
        
        self.axis.set_xlim(0, prop.SAMPLE_RATE/2)
        self.axis.set_ylim(0, 1.2)
        self.stream()
        
    # ----------------------------------------------------------------------
    @loop_consumer
    def stream(self, data, topic, frame):
        """""" 
       
        if topic == "eeg" and frame%1==0:
           
            eeg = self.centralize(self.buffer_eeg)
            w, EEG = welch(eeg, fs=prop.SAMPLE_RATE, axis=1)
            # w, EEG = eeg_features.spectrum(eeg, fs=prop.SAMPLE_RATE, axis=1)
            EEG = EEG/EEG.max()
            
            for i, line in enumerate(self.lines):
                line.set_data(w, EEG[i])
            
            # logging.warning(f'feed! {EEG.max():.5f}, {w.shape}, {EEG.shape}, {self.buffer_eeg.shape}')
            self.feed()
            
            # self.max_f = max(EEG.max(), self.max_f)
            # self.axis.set_ylim(0, EEG.max())
        
        elif topic == "marker":
            data = data.value
            logging.warning(data)
      
      


if __name__ == '__main__':
    Stream()
