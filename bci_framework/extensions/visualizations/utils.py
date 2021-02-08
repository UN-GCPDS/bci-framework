"""
=====
Utils
=====

This module define usefull decorators to use with data analysis.
"""

import time
from datetime import datetime
from multiprocessing import Process
from threading import Thread
from typing import Callable

import numpy as np
from openbci_stream.acquisition import OpenBCIConsumer

from ...extensions import properties as prop


# ----------------------------------------------------------------------
def subprocess_this(fn: Callable) -> Callable:
    """Decorator to move methods to subprocessing."""

    def wraper(self, *args, **kwargs):
        c = Process(target=fn, args=(self, *args))
        c.start()
    return wraper


# ----------------------------------------------------------------------
def thread_this(fn: Callable) -> Callable:
    """Decorator to move methods to threading."""

    def wraper(self, *args, **kwargs):
        c = Thread(target=fn, args=(self, *args))
        c.start()
    return wraper


# ----------------------------------------------------------------------
def timeit(fn: Callable) -> Callable:
    """Decorator to calculate the execution time of a method."""

    def wrap(self, *args, **kwargs):
        t0 = time.time()
        r = fn(self, *args, **kwargs)
        t1 = time.time()
        print(f"[timeit] {fn.__name__}: {(t1-t0)*1000:.2f} ms")
        return r
    return wrap


# ----------------------------------------------------------------------
def loop_consumer(fn: Callable) -> Callable:
    """Decorator to iterate methods with new streamming data.

    This decorator will call a method on every new data streamming input.
    """

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


# ----------------------------------------------------------------------
def fake_loop_consumer(fn):
    """Decorator to iterate methods with new streamming data.

    This decorator will call a method with fake data.
    """

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

            while time.time() < (t0 + 1 / (prop.SAMPLE_RATE / prop.STREAMING_PACKAGE_SIZE)):
                time.sleep(0.01)

    return wrap
