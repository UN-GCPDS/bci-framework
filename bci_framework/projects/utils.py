from openbci_stream.consumer import OpenBCIConsumer
from bci_framework.projects import properties as prop


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
