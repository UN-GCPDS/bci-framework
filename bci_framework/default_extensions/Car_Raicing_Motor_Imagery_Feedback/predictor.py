import numpy as np
from typing import Literal
import random
import logging
import joblib
import os

actions = ['right', 'left']


model = joblib.load(os.path.join(os.path.abspath(os.path.dirname(__file__)),'models', 'model_yn.pkl'))

# ----------------------------------------------------------------------
def predict(data:np.ndarray) -> Literal[actions]:
    """"""
    logging.warning(f'Input: {data.shape}')
    ######
    
    match model.predict(data):
        
        case 1:
            return 'right'
        case 2:
            return 'left'
            
    
    loging.warning(f'Action: {action}')
    
    return action 
