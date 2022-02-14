import numpy as np
from typing import Literal
import random
import logging

actions = ['up', 'bottom', 'right', 'left']

# ----------------------------------------------------------------------
def predict(data:np.ndarray) -> Literal[actions]:
    """"""
    logging.warning(f'Input: {data.shape}')
    ######
    

    action = random.choice(actions)
    return action
0..........................