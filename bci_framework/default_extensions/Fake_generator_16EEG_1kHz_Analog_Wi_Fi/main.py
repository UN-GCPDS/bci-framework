from bci_framework.extensions.data_analysis import DataAnalysis, loop_consumer
import logging
import pickle
from kafka import KafkaProducer
from bci_framework.extensions import properties as prop
import time
import numpy as np
from datetime import datetime, timedelta


CHANNELS = 16
SAMPLE_RATE = 1000
STREAMING_PACKAGE_SIZE = 100


prop.HOST = 'localhost'
prop.CHANNELS = {i + 1: f'ch-{i+1}' for i in range(CHANNELS)}
prop.SAMPLE_RATE = SAMPLE_RATE
prop.STREAMING_PACKAGE_SIZE = STREAMING_PACKAGE_SIZE
prop.BOARDMODE = 'analog'
prop.CONNECTION = 'wifi'
prop.SYNCLATENCY = 0
prop.OFFSET = 0
prop.DAISY = [True]
prop.RASPAD = False
prop.CHANNELS_BY_BOARD = [CHANNELS]


########################################################################
class Analysis(DataAnalysis):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        
        self.kafka_producer = KafkaProducer(
                bootstrap_servers=[f'{prop.HOST}:9092'],
                compression_type='gzip',
                value_serializer=pickle.dumps,
            )
        
        self.producer()
        

    # ----------------------------------------------------------------------
    def producer(self):
        """"""
        t = prop.STREAMING_PACKAGE_SIZE / prop.SAMPLE_RATE
        t0 = time.time()
        
        while True:
            
        
            while time.time() > t0 + t:
                
                match prop.BOARDMODE:
                    
                    case 'analog':
                        aux_shape = 2
                        
                    case 'digital':
                        aux_shape = 3
                        
                    case 'default':
                        aux_shape = 3
                
                eeg = 100*np.random.normal(0, 1, size=(sum(prop.CHANNELS_BY_BOARD), prop.STREAMING_PACKAGE_SIZE))
                aux = 100*np.random.normal(0, 1, size=(aux_shape, (sum(prop.CHANNELS_BY_BOARD)//8)*prop.STREAMING_PACKAGE_SIZE))
                
                context = {
                
                    'timestamp.binary': [datetime.now().timestamp()],
                    'timestamp.binary.consume': [(datetime.now() + timedelta(milliseconds=100)).timestamp()],
                    'timestamp.eeg': (datetime.now() + timedelta(milliseconds=200)).timestamp(),
                    
                    'samples': [prop.STREAMING_PACKAGE_SIZE],
                    'connection': 'wifi',
                    'daisy': [True],
                    }
                
                
                self.kafka_producer.send('eeg', {'context': context,
                                                 'data': eeg,
                                                })
                self.kafka_producer.send('aux', {'context': context,
                                                 'data': aux,
                                                })
                
                t0 = time.time()
        
        
        
        
        
if __name__ == '__main__':
    Analysis()
