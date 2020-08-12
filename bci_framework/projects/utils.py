from openbci_stream.consumer import OpenBCIConsumer
from bci_framework.projects import properties as prop
import numpy as np
import time
from datetime import datetime


# ----------------------------------------------------------------------
def loop(fn):
    """"""
    def wrap(*args, **kwargs):
        while True:
            fn(*args, **kwargs)
    return wrap


# ----------------------------------------------------------------------
def feed(fn):
    """"""
    def wrap(cls, *args, **kwargs):
        fn(cls, *args, **kwargs)
        cls.feed()
    return wrap


# ----------------------------------------------------------------------
def loop_consumer(fn):
    """"""
    def wrap(cls, *args, **kwargs):
        with OpenBCIConsumer(host=prop.HOST) as stream:
            for data in stream:
                # if data.topic == 'eeg':
                fn(cls, data, data.topic, *args, **kwargs)
                # cls.feed()
    return wrap


# ----------------------------------------------------------------------
def fake_loop_consumer(fn):
    """"""
    def wrap(cls, *args, **kwargs):
        while True:
            t0 = time.time()

            eeg = np.random.normal(0, 0.2, size=(16, 1000))
            aux = np.random.normal(0, 0.2, size=(3, 1000))

            class data:
                """"""
                value = {}

            data.value['timestamp'] = datetime.now()
            data.value['data'] = eeg, aux
            fn(cls, data, 'eeg', *args, **kwargs)

            if np.random.random() > 0.9:
                data.value['timestamp'] = datetime.now()
                data.value['data'] = chr(
                    np.random.choice(range(ord('A'), ord('Z') + 1)))
                fn(cls, data, 'marker', *args, **kwargs)

            while time.time() < (t0 + 1):
                time.sleep(0.01)

    return wrap
