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
    @marker_slicing("ERP:(.+)*", t0=0, duration=0.3)
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
