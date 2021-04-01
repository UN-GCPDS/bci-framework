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
    @fake_loop_consumer('eeg')
    def stream(self, frame):
        """"""
        logging.debug(frame)
        logging.info(frame)
        logging.warning(frame)
        logging.error(frame)
        logging.critical(frame)
        
if __name__ == '__main__':
    Analysis()
