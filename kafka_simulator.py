from kafka import KafkaProducer
import pickle
from datetime import datetime
import numpy as np
import time

producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                         compression_type='gzip',
                         value_serializer=pickle.dumps,
                         # request_timeout_ms=30000,
                         # heartbeat_interval_ms=10000,
                         )


while True:

    t0 = time.time()
    data = {'context': 'context',
            'data': np.random.normal(0, 0.8, size=(16, 1000)),
            'binary_created': datetime.now().timestamp(),
            'created': datetime.now().timestamp(),
            'samples': 1000,
            }

    producer.send('eeg', data)

    while time.time() < (t0 + 1):
        time.sleep(0.01)

    print('.')
