from bci_framework.extensions.data_analysis import DataAnalysis
import logging

########################################################################
class Analysis(DataAnalysis):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
    
        logging.debug('debug')
        logging.info('info')
        logging.warning('warning')
        logging.error('error')
        logging.critical('critical')        
                    
                                    
if __name__ == '__main__':
    Analysis()
