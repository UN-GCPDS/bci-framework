import numpy as np
from typing import Literal
import random
import logging

actions = ['up', 'bottom', 'right', 'left']

# ----------------------------------------------------------------------
def classify(data:np.ndarray) -> Literal[actions]:
    """"""
    logging.warning(f'Input: {data.shape}')
    ######
    

    action = random.choice(actions)
    return action
