from bci_framework.extensions.data_analysis import DataAnalysis, loop_consumer, fake_loop_consumer
import logging

import gym
import numpy as np

from predictor import predict


BUFFER = 3  # Segundos de analisis de la señal
SLIDING_DATA = 300  # Cantidad de datos que se actualizaran en cada clasificación
GAS = 0.01
BREAK_SYSTEM = 0


########################################################################
class Analysis(DataAnalysis):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        
        self.steering_wheel = 0
        
        # Car raicing
        self.env = gym.make('CarRacing-v0')
        self.env.reset()

        # Buffer
        self.create_buffer(BUFFER, aux_shape=3, fill=0)
        self.stream()
        

    # ----------------------------------------------------------------------
    @fake_loop_consumer('eeg', package_size=SLIDING_DATA)
    def stream(self, frame):
        """"""
        action = predict(self.buffer_eeg.reshape(1, 16, -1))
        
        match action:
            
            case 'right':
                self.steering_wheel += 0.1
                
            case 'left':
                self.steering_wheel -= 0.1
        
        # Move Car
        logging.warning(f'Action: {action}')
    
        self.env.render()
        self.env.step([self.steering_wheel, GAS, BREAK_SYSTEM])
        
        
if __name__ == '__main__':
    Analysis()
