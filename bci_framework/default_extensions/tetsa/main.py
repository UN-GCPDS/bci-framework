from bci_framework.extensions.data_analysis import DataAnalysis, loop_consumer, fake_loop_consumer
import logging

########################################################################
class Analysis(DataAnalysis):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        self.stream()
        

    # ----------------------------------------------------------------------
    @loop_consumer('eeg')
    def stream(self, frame, kafka_stream):
        """"""
        
        x = f"{kafka_stream.value['context']['sample_ids']}"
        
        logging.warning(x)
        
        
if __name__ == '__main__':
    Analysis()
