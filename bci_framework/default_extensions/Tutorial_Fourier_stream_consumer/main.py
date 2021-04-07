"""
=================
Analysis Consumer
=================
"""

from bci_framework.extensions.data_analysis import DataAnalysis, loop_consumer
from typing import TypeVar

KAFKA_STREAM = TypeVar('Kafka')


########################################################################
class AnalysisConsumer(DataAnalysis):
    """Analysis Consumer."""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        self.stream()

    # ----------------------------------------------------------------------
    @loop_consumer('spectrum')  # consume only the `spectrum` topic
    def stream(self, data: KAFKA_STREAM):
        """"""
        data = data.value['data']

        # read the data
        EEG = data['amplitude']
        W = data['frequency']


if __name__ == '__main__':
    AnalysisConsumer()
