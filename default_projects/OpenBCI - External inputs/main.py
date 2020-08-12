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
        super().__init__(figsize=(16, 9), dpi=60)

        self.channels = 5
        self.T = 5

        self.axis = self.add_subplot(1, 1, 1)
        self.lines = [self.axis.plot(np.zeros(prop.SAMPLE_RATE * self.T), np.zeros(prop.SAMPLE_RATE * self.T), '-')[0] for i
                      in range(self.channels)]
        self.lines = np.array(self.lines)
                      
        self.axis.set_xlim(-self.T, 0)
        self.stream()

    # ----------------------------------------------------------------------
    @loop_consumer
    def stream(self, data, topic):
        """"""
        boardmode = data.value['context']['boardmode']
        connection = data.value['context']['connection']
        
        logging.warning(f"Boarmode: {boardmode} over {connection}")
        
        if topic != 'eeg':
            return 

        _, aux = data.value['data']
        N = aux.shape[1]
        
        if not N:
            logging.warning(aux.shape)
            return
            
        if boardmode == 'analog':
            self.axis.set_ylim(0, 255)
            if connection == 'wifi':
                self.axis.legend(['A5(D11)', 'A6(D12)'])
                index = [0, 1]
            else:
                self.axis.legend(['A5(D11)', 'A6(D12)', 'A7(D13)'])
                index = [0, 1, 2]
       
        elif boardmode == 'digital':
            self.axis.set_ylim(0, 1.2)
            if connection == 'wifi':
                self.axis.legend(['D11', 'D12', 'D17'])
                index = [0, 1, 2]
            else:
                self.axis.legend(['D11', 'D12', 'D13', 'D17', 'D18'])
                index = [0, 1, 2, 3, 4]
            
        for i, line in enumerate(self.lines[index]):            
            y_data = line.get_ydata()
            y_data = np.roll(y_data, -N)
            y_data[-N:] = aux[i]
            line.set_ydata(y_data)
            line.set_xdata(np.linspace(-self.T, 0, y_data.shape[0]))
            
        self.feed()


if __name__ == '__main__':
    Stream()
