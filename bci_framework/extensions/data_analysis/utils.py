"""
=====
Utils
=====

This module define usefull decorators to use with data analysis.
"""

import time
import random
from datetime import datetime, timedelta
from multiprocessing import Process
from threading import Thread
from typing import Callable, Union, List

import numpy as np
from openbci_stream.acquisition import OpenBCIConsumer

from ...extensions import properties as prop


class data:
    value = {
        'context': {},
    }


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

    def wraper(self, *args, **kwargs):
        t0 = time.time()
        r = fn(self, *args, **kwargs)
        t1 = time.time()
        print(f"[timeit] {fn.__name__}: {(t1-t0)*1000:.2f} ms")
        return r
    return wraper


# ----------------------------------------------------------------------
def loop_consumer(*topics) -> Callable:
    """Decorator to iterate methods with new streamming data.

    This decorator will call a method on every new data streamming input.
    """
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
                        # latency calculated with `binary_created`
                        latency = (datetime.now() - datetime.fromtimestamp(
                            data.value['context']['binary_created'])).total_seconds() * 1000
                        data_ = data.value['data']
                    else:
                        # latency calculated with kafka timestamp
                        latency = (datetime.now(
                        ) - datetime.fromtimestamp(data.timestamp / 1000)).total_seconds() * 1000

                        data_ = data.value

                    kwargs = {'data': data_,
                              'kafka_stream': data,
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
                    aux = np.random.normal(0, 0.2, size=(3, num_data))
                elif prop.BOARDMODE == 'analog':
                    if prop.CONNECTION == 'wifi':
                        aux = np.random.normal(0, 0.07, size=(2, num_data))
                    else:
                        aux = np.random.normal(0, 0.07, size=(3, num_data))

                    if (time.time() // 1) % 2:
                        aux += 1

                elif prop.BOARDMODE == 'digital':
                    if prop.CONNECTION == 'wifi':
                        aux = np.random.normal(0, 0.2, size=(3, num_data))
                    else:
                        aux = np.random.normal(0, 0.2, size=(5, num_data))
                else:
                    aux = None

                data.timestamp = datetime.now().timestamp() * 1000
                data.value['timestamp'] = datetime.now()
                data.value['data'] = eeg, aux

                if 'eeg' in topics:
                    if hasattr(cls, 'buffer_eeg'):
                        cls.update_buffer(
                            *data.value['data'], data.value['timestamp'].timestamp())

                    kwargs = {'data': data.value['data'],
                              'kafka_stream': data,
                              'topic': 'eeg',
                              'frame': frame,
                              'latency': 0,
                              }
                    fn(*[cls] + [kwargs[v] for v in arguments])

                if 'marker' in topics:
                    if np.random.random() > 0.9:
                        data.value['timestamp'] = datetime.now()
                        data.value['context']['binary_created'] = datetime.now()
                        # data.value['data'] = chr(
                            # np.random.choice(range(ord('A'), ord('Z') + 1)))
                        data.value['data'] = random.choice(
                            ['Right', 'Left', 'Up', 'Bottom'])

                        kwargs = {'data': data.value['data'],
                                  'kafka_stream': data,
                                  'topic': 'marker',
                                  'frame': frame,
                                  'latency': 0,
                                  }
                        fn(*[cls] + [kwargs[v] for v in arguments])

                while time.time() < (t0 + 1 / (prop.SAMPLE_RATE / prop.STREAMING_PACKAGE_SIZE)):
                    time.sleep(0.0001)

        return wrap
    return wrap_wrap


# ----------------------------------------------------------------------
def marker_slicing(marker, t0, duration):
    """"""
    if isinstance(marker, str):
        marker = [marker]

    def wrap_wrap(fn):

        arguments = fn.__code__.co_varnames[1:fn.__code__.co_argcount]

        def wrap(cls):
            cls._target_marker = []

            @loop_consumer('eeg', 'marker')
            def marker_slicing_(cls, topic, data, kafka_stream, latency):

                if topic == 'marker':
                    if data['marker'] in marker:
                        cls._target_marker.append(
                            [data['marker'], kafka_stream.value['datetime']])

                if target := getattr(cls, '_target_marker', False):

                    # marker, target = target
                    if cls.buffer_timestamp[-1] > (datetime.fromtimestamp(target[0][1]) + timedelta(seconds=duration - t0)).timestamp():

                        _marker, _target = target.pop(0)

                        argmin = np.abs(cls.buffer_timestamp - _target).argmin()

                        start = int((prop.SAMPLE_RATE) * t0)
                        stop = int((prop.SAMPLE_RATE) * (duration + t0))

                        t = cls.buffer_timestamp[argmin + start:argmin + stop]
                        eeg = cls.buffer_eeg[:, argmin + start:argmin + stop]
                        aux = cls.buffer_aux[:, argmin + start:argmin + stop]

                        kwargs = {'eeg': eeg,
                                  'aux': aux,
                                  'timestamp': t,
                                  'marker_datetime': _target,
                                  'marker': _marker,
                                  'latency': latency,
                                  }

                        fn(*[cls] + [kwargs[v] for v in arguments])

            marker_slicing_(cls)
        return wrap
    return wrap_wrap
