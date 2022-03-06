from bci_framework.extensions.data_analysis import DataAnalysis, loop_consumer, fake_loop_consumer
import logging

import gym
import bci_pacman
import time

from predictor import predict


BUFFER = 3  # Segundos de analisis de la señal
SLIDING_DATA = 300  # Cantidad de datos que se actualizaran en cada clasificación
PACMAN_ACTIONS = ['up', 'bottom', 'right', 'left']


########################################################################
class Analysis(DataAnalysis):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)

        # Pacman
        self.env = gym.make('BerkeleyPacman-v0')
        self.env.reset(chosenLayout='originalClassic', no_ghosts=True)
        # self.env.reset(chosenLayout='openClassic', no_ghosts=True)

        # Buffer
        self.create_buffer(BUFFER, aux_shape=3, fill=0)
        self.stream()

    # ----------------------------------------------------------------------
    @loop_consumer('eeg', package_size=SLIDING_DATA)
    def stream(self, frame):
        """"""
        action = predict(self.buffer_eeg.reshape(1, 16, -1))

        # Move Pacman
        logging.warning(f'Action: {action}')
        self.env.step(action)


if __name__ == '__main__':
    Analysis()
