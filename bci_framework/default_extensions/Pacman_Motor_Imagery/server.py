import gym
import bci_pacman
import random
import time

env = gym.make('BerkeleyPacman-v0')
env.reset(chosenLayout='originalClassic', no_ghosts=True)
# env.reset(chosenLayout='testClassic', no_ghosts=True)

PACMAN_ACTIONS = ['up', 'bottom', 'right', 'left']


# ----------------------------------------------------------------------
def bci_pacman_server():
    """"""
    while True:
        action = random.choice(PACMAN_ACTIONS)
        env.step(action)


bci_pacman_server()
