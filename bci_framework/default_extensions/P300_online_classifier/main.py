"""
======================
P300 online classifier
======================

"""

from bci_framework.extensions.data_analysis import DataAnalysis, loop_consumer, fake_loop_consumer
import logging
from typing import Literal
import numpy as np
import os

CHARACTERS_SRLZ = ["A", "B", "C", "D", "E", "F", "aa",
                   "G", "H", "I", "J", "K", "L", "bb",
                   "M", "N", "O", "P", "Q", "R", "cc",
                   "S", "T", "U", "V", "W", "X", "dd",
                   "Y", "Z", "0", "1", "2", "3", "ee",
                   "4", "5", "6", "7", "8", "9", "ff"]


########################################################################
class OnlineClassifier(DataAnalysis):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)

        # 4 seconds sliding window
        self.create_buffer(4)

        self.stream()

    # ----------------------------------------------------------------------
    @marker_slicing(CHARACTERS_SRLZ, t0=0, duration=0.3)
    def stream(self, eeg, aux, timestamp, marker):
        """"""
        if self.erp_classifier(eeg):
            self.send_feedback(value=marker)

    # ----------------------------------------------------------------------
    def erp_classifier(self, data: np.ndarray) -> bool:
        """"""
        # channels x time
        data

        return True


if __name__ == '__main__':
    OnlineClassifier()
