from bci_framework.extensions.data_analysis import DataAnalysis, loop_consumer, fake_loop_consumer
import logging
from typing import Literal
import numpy as np

########################################################################
class OnlineClassifier(DataAnalysis):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        self.stream()
        
        # 4 seconds sliding window
        self.create_buffer(4)
        

    # ----------------------------------------------------------------------
    @fake_loop_consumer('eeg')
    def stream(self):
        """"""
        
        direction = self.classifier(self.buffer_eeg)
        self.send_command('pacman', direction)
    
        
    # ----------------------------------------------------------------------
    def classifier(self, data: np.ndarray) -> Literal['right', 'left', 'up', 'botton']:
        """"""
        # channels x time
        data
        
        
        
if __name__ == '__main__':
    OnlineClassifier()
