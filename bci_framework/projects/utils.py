from openbci_stream.consumer import OpenBCIConsumer
from bci_framework.projects import properties as prop
import numpy as np
import time


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
                fn(cls, data, *args, **kwargs)
                cls.feed()
    return wrap


# ----------------------------------------------------------------------
def fake_loop_consumer(fn):
    """"""
    def wrap(cls, *args, **kwargs):
        while True:
            t0 = time.time()

            data = np.random.normal(0, 1, size=(16, 1000))
            fn(cls, data, *args, **kwargs)
            cls.feed()

            while time.time() < (t0 + 1):
                time.sleep(0.01)

    return wrap
