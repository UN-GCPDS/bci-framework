from openbci_stream.consumer import OpenBCIConsumer
from ..projects import properties as prop
import numpy as np
import time
from datetime import datetime

# from scipy.signal import resample

import logging

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
def fast_resample(x, num, axis=-1):
    """"""
    ndim = x.shape[axis] // num
    return x[:, :ndim * num].reshape(x.shape[0], num, ndim).mean(axis=-1)


# ----------------------------------------------------------------------
def loop_consumer(fn):
    """"""
    def wrap(cls, **kwargs):
        with OpenBCIConsumer(host=prop.HOST) as stream:
            frame = 0
            for data in stream:

                if data.topic == 'eeg':
                    frame += 1
                    kwargs['frame'] = frame

                    if hasattr(cls, 'buffer_eeg'):
                        cls.update_buffer(*data.value['data'])

                fn(cls, data, data.topic, **kwargs)
    return wrap


# # ----------------------------------------------------------------------
# def loop_buffer(fn):
    # """"""
    # def wrap(cls, *args, **kwargs):
    # with OpenBCIConsumer(host=prop.HOST) as stream:
    # for data in stream:
    # if data.topic == 'eeg':
    # cls.update_buffer(*data.value['data'])
    # fn(cls, *args, **kwargs)
    # return wrap


# ----------------------------------------------------------------------
def fake_loop_consumer(fn):
    """"""
    def wrap(cls, *args, **kwargs):
        frame = 0
        while True:
            t0 = time.time()

            eeg = np.random.normal(0, 0.2, size=(
                len(prop.CHANNELS), int(prop.STREAMING_PACKAGE_SIZE)))

            if prop.BOARDMODE == 'default':
                aux = np.random.normal(0, 0.2, size=(
                    3, prop.SAMPLE_RATE))
            elif prop.BOARDMODE == 'analog':
                aux = np.random.normal(0, 0.2, size=(
                    3, prop.SAMPLE_RATE))
            elif prop.BOARDMODE == 'digital':
                aux = np.random.normal(0, 0.2, size=(
                    5, prop.SAMPLE_RATE))
            else:
                aux = None

            class data:
                """"""
                value = {}

            frame += 1
            kwargs['frame'] = frame

            data.value['timestamp'] = datetime.now()
            data.value['data'] = eeg, aux

            if hasattr(cls, 'buffer_eeg'):
                cls.update_buffer(*data.value['data'])

            fn(cls, data, 'eeg', *args, **kwargs)

            if np.random.random() > 0.9:
                data.value['timestamp'] = datetime.now()
                data.value['data'] = chr(
                    np.random.choice(range(ord('A'), ord('Z') + 1)))
                fn(cls, data, 'marker', *args, **kwargs)

            # while time.time() < (t0 + (prop.STREAMING_PACKAGE_SIZE / 1000)):
            while time.time() < (t0 + (prop.SAMPLE_RATE / prop.STREAMING_PACKAGE_SIZE)):
                time.sleep(0.01)

    return wrap


def timeit(fn):
    def wrap(self, *args, **kwargs):
        t0 = time.time()
        r = fn(self, *args, **kwargs)
        t1 = time.time()
        print(f"[timeit] {fn.__name__}: {(t1-t0)*1000:.2f} ms")
        return r
    return wrap
