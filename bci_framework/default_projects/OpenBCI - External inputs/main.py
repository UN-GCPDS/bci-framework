from bci_framework.projects.figure import FigureStream
from bci_framework.projects import properties as prop
from bci_framework.projects.utils import loop_consumer, fake_loop_consumer

import logging
import numpy as np


########################################################################
class Stream(FigureStream):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """"""
        super().__init__()
        
        self.subsample = 25
        t = 30
        
        # self.tight_layout(rect=[0.03, 0.03, 1, 0.95])

        self.axis, self.time, self.lines = self.create_lines(prop.BOARDMODE, t) 
        # self.time = np.linspace(-t, 0, self.lines[0].get_ydata().shape[0])
        
        self.axis.set_title('External inputs')
        self.axis.set_xlabel('Time [s]')   
        self.axis.set_ylabel('Amplitude')        
        
        self.stream()

    # ----------------------------------------------------------------------
    @loop_consumer
    def stream(self, data, topic, frame):
        """"""
        if topic != 'eeg':
            return

        if prop.BOARDMODE not in ['analog', 'digital']:
            logging.warning(f"The 'boardmode' configuration must be 'ANALOG' or 'DIGITAL' for this visualization")
            return

        _, aux = data.value['data'] 
        
        if len(aux)==0:
            logging.warning(f"NONEN")
            return 
    
        N = aux.shape[1]
        logging.warning(f"Shape: {N}")

        for i, line in enumerate(self.lines):
            y_data = line.get_ydata()
            y_data = np.roll(y_data, -N)
            y_data[-N:] = aux[i]
            line.set_data(self.time, y_data)

        self.feed()


if __name__ == '__main__':
    Stream()
