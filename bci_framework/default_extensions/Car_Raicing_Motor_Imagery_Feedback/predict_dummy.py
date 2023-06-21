import numpy as np


class Predict_Dummy:

  def __init__(self):
      """"""

  def predict(self, X):
      
    y = np.random.choice([0, 1])
      
    print(y)
    return y