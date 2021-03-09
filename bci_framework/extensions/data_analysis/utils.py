"""
=====
Utils
=====

This module define usefull decorators to use with data analysis.
"""

import time
import random
from datetime import datetime
from multiprocessing import Process
from threading import Thread
from typing import Callable

import numpy as np
from openbci_stream.acquisition import OpenBCIConsumer

from ...extensions import properties as prop


class data:
    value = {}


# ----------------------------------------------------------------------
def subprocess_this(fn: Callable) -> Callable:
    """Decorator to move methods to subprocessing."""

    def wraper(*args, **kwargs):
        c = Process(target=fn, args=args)
        c.start()
    return wraper


# ----------------------------------------------------------------------
def thread_this(fn: Callable) -> Callable:
    """Decorator to move methods to threading."""

    def wraper(*args, **kwargs):
        c = Thread(target=fn, args=args)
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
def loop_consumer(*topics) -> Callable:
    """Decorator to iterate methods with new streamming data.

    This decorator will call a method on every new data streamming input.
    """
    # ----------------------------------------------------------------------
    def wrap_wrap(fn: Callable) -> Callable:

        arguments = fn.__code__.co_varnames[1:fn.__code__.co_argcount]

        def wrap(cls):
            with OpenBCIConsumer(host=prop.HOST, topics=topics) as stream:
                frame = 0
                for data in stream:
                    if data.topic == 'eeg':
                        frame += 1
                        if hasattr(cls, 'buffer_eeg'):
                            cls.update_buffer(
                                *data.value['data'], data.value['context']['binary_created'])
                        latency = (datetime.now() - datetime.fromtimestamp(
                            data.value['context']['binary_created'])).total_seconds() * 1000
                    else:
                        latency = (datetime.now(
                        ) - datetime.fromtimestamp(data.timestamp / 1000)).total_seconds() * 1000

                    kwargs = {'data': data,
                              'topic': data.topic,
                              'frame': frame,
                              'latency': latency,
                              }

                    fn(*[cls] + [kwargs[v] for v in arguments])
        return wrap
    return wrap_wrap


# ----------------------------------------------------------------------
def fake_loop_consumer(*topics) -> Callable:
    """Decorator to iterate methods with new streamming data.

    This decorator will call a method with fake data.
    """

    # ----------------------------------------------------------------------
    def wrap_wrap(fn: Callable) -> Callable:

        arguments = fn.__code__.co_varnames[1:fn.__code__.co_argcount]

        def wrap(cls):
            frame = 0

            while True:
                frame += 1
                t0 = time.time()

                num_data = int(prop.STREAMING_PACKAGE_SIZE)
                num_data = random.randint(num_data - 10, num_data + 10)

                eeg = np.random.normal(0, 0.2, size=(
                    len(prop.CHANNELS), num_data))

                if prop.BOARDMODE == 'default':
                    aux = np.random.normal(0, 0.2, size=(
                        3, num_data))
                elif prop.BOARDMODE == 'analog':
                    aux = np.random.normal(0, 0.07, size=(
                        3, num_data))

                    if (time.time() // 10) % 2:
                        aux += 1

                elif prop.BOARDMODE == 'digital':
                    aux = np.random.normal(0, 0.2, size=(
                        5, num_data))
                else:
                    aux = None

                data.timestamp = datetime.now().timestamp() * 1000
                data.value['timestamp'] = datetime.now()
                data.value['data'] = eeg, aux

                if 'eeg' in topics:
                    if hasattr(cls, 'buffer_eeg'):
                        cls.update_buffer(
                            *data.value['data'], data.value['timestamp'].timestamp())

                    kwargs = {'data': data,
                              'topic': 'eeg',
                              'frame': frame,
                              'latency': 0,
                              }
                    fn(*[cls] + [kwargs[v] for v in arguments])

                if 'marker' in topics:
                    if np.random.random() > 0.9:
                        data.value['timestamp'] = datetime.now()
                        data.value['data'] = chr(
                            np.random.choice(range(ord('A'), ord('Z') + 1)))

                        kwargs = {'data': data,
                                  'topic': 'marker',
                                  'frame': frame,
                                  'latency': 0,
                                  }
                        fn(*[cls] + [kwargs[v] for v in arguments])

                while time.time() < (t0 + 1 / (prop.SAMPLE_RATE / prop.STREAMING_PACKAGE_SIZE)):
                    time.sleep(0.0001)

        return wrap
    return wrap_wrap
