from bci_pacman.layouts import get_layouts

from gym.envs.registration import register

register(
    id='BerkeleyPacman-v0',
    entry_point='bci_pacman.envs:PacmanEnv',
)
