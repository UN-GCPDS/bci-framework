"""
=====
Utils
=====

This module define usefull decorators to use with data analysis.
"""

import os
import json
import time
import logging
import random
from datetime import datetime, timedelta
from multiprocessing import Process
from threading import Thread
from typing import Callable
import re

import numpy as np
from openbci_stream.acquisition import OpenBCIConsumer

from ...extensions import properties as prop


class data:
    value = {
        'context': {},
    }


data_tmp_aux_ = None
data_tmp_eeg_ = None


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
def loop_consumer(*topics, package_size=None) -> Callable:
    """Decorator to iterate methods with new streamming data.

    This decorator will call a method on every new data streamming input.
    """
    global data_tmp_eeg_, data_tmp_aux_

    if json.loads(os.getenv('BCISTREAM_RASPAD')):
        package_size = 1000

    def wrap_wrap(fn: Callable) -> Callable:
        global data_tmp_eeg_, data_tmp_aux_

        arguments = fn.__code__.co_varnames[1:fn.__code__.co_argcount]

        def wrap(cls):
            global data_tmp_eeg_, data_tmp_aux_

            with OpenBCIConsumer(host=prop.HOST, topics=topics) as stream:
                frame = 0

                for data in stream:

                    if data.topic == 'eeg':
                        frame += 1
                        if hasattr(cls, 'buffer_eeg_'):
                            cls.update_buffer(
                                eeg=data.value['data'], timestamp=min(data.value['context']['timestamp.binary']) - prop.OFFSET)
                        data_ = data.value['data']
                    elif data.topic == 'aux':
                        frame += 1
                        if hasattr(cls, 'buffer_aux_'):
                            cls.update_buffer(
                                aux=data.value['data'], timestamp=min(data.value['context']['timestamp.binary']) - prop.OFFSET)
                        data_ = data.value['data']
                    else:
                        data_ = data.value

                    # latency calculated with `timestamp.binary`
                    if data.topic in ['eeg', 'aux']:
                        latency = (datetime.now() - datetime.fromtimestamp(
                            min(data.value['context']['timestamp.binary']) - prop.OFFSET)).total_seconds() * 1000
                    else:
                        # latency calculated with kafka timestamp
                        latency = (datetime.now(
                        ) - datetime.fromtimestamp(data.timestamp / 1000)).total_seconds() * 1000

                    if package_size and (data.topic in ['eeg', 'aux']):

                        if data.topic == 'eeg':
                            if data_tmp_eeg_ is None:
                                data_tmp_eeg_ = np.zeros(
                                    (data_.shape[0], 0))
                            data_tmp_eeg_ = np.concatenate(
                                [data_tmp_eeg_, data_], axis=1)
                            d = data_tmp_eeg_
                        elif data.topic == 'aux':
                            if data_tmp_aux_ is None:
                                data_tmp_aux_ = np.zeros((data_.shape[0], 0))
                            data_tmp_aux_ = np.concatenate(
                                [data_tmp_aux_, data_], axis=1)
                            d = data_tmp_aux_

                        kwargs = {'data': d,
                                  'kafka_stream': data,
                                  'topic': data.topic,
                                  'frame': frame,
                                  'latency': latency,
                                  }
                        n = (package_size // prop.STREAMING_PACKAGE_SIZE)
                        if frame % n == 0:
                            fn(*[cls] + [kwargs[v] for v in arguments])
                        # else:
                            if data.topic == 'eeg':
                                data_tmp_eeg_ = np.zeros((data_.shape[0], 0))
                            elif data.topic == 'aux':
                                data_tmp_aux_ = np.zeros((data_.shape[0], 0))
                    else:
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

                eeg = 150 * np.random.normal(0, 0.2, size=(
                    len(prop.CHANNELS), num_data))

                if prop.BOARDMODE == 'default':
                    aux = np.random.normal(0, 0.2, size=(3, num_data))
                elif prop.BOARDMODE == 'analog':
                    if prop.CONNECTION == 'wifi':
                        aux = np.random.normal(0, 0.07, size=(3, num_data))

                        if (frame // 10) % 2:
                            aux += 100

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
                # data.value['data'] = eeg, aux

                if 'eeg' in topics:
                    if hasattr(cls, 'buffer_eeg'):
                        cls.update_buffer(
                            eeg=eeg, timestamp=data.value['timestamp'].timestamp())

                    kwargs = {'data': eeg,
                              'kafka_stream': data,
                              'topic': 'eeg',
                              'frame': frame,
                              'latency': 0,
                              }
                    fn(*[cls] + [kwargs[v] for v in arguments])

                if 'aux' in topics:
                    if hasattr(cls, 'buffer_aux'):
                        cls.update_buffer(
                            aux=aux, timestamp=data.value['timestamp'].timestamp())

                    kwargs = {'data': aux,
                              'kafka_stream': data,
                              'topic': 'eeg',
                              'frame': frame,
                              'latency': 0,
                              }
                    fn(*[cls] + [kwargs[v] for v in arguments])

                if 'marker' in topics:
                    if np.random.random() > 0.9:
                        data.value['timestamp'] = datetime.now()
                        # data.value['datetime'] = datetime.now()
                        data.value['context']['timestamp.binary'] = datetime.now()
                        # data.value['data'] = chr(
                            # np.random.choice(range(ord('A'), ord('Z') + 1)))
                        # data.value['data'] = random.choice(
                            # ['Right', 'Left', 'Up', 'Bottom'])
                        data.value['marker'] = random.choice(['MARKER'])

                        kwargs = {'data': data.value,
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
def marker_slicing(markers, t0, t1):
    """"""
    if isinstance(markers, str):
        markers = [markers]

    def wrap_wrap(fn):

        arguments = fn.__code__.co_varnames[1:fn.__code__.co_argcount]

        def wrap(cls):
            cls._target_marker = []

            @loop_consumer('aux', 'marker')
            def marker_slicing_(cls, topic, data, kafka_stream, latency):

                if topic == 'marker':
                    # if data['marker'] in markers:
                        # cls._target_marker.append(
                            # [data['marker'], kafka_stream.value['datetime']])

                    if any([bool(re.match(mkr, data['marker'])) for mkr in markers]):
                        cls._target_marker.append(
                            [data['marker'], kafka_stream.value['datetime']])

                if len(cls._target_marker) < 3:
                    return

                if target := getattr(cls, '_target_marker', False):

                    # marker, target = target

                    last_buffer_timestamp = cls.buffer_aux_timestamp[-1] - prop.OFFSET
                    last_target_timestamp = (datetime.fromtimestamp(
                        target[0][1]) + timedelta(seconds=t1)).timestamp()

                    if last_buffer_timestamp > last_target_timestamp:
                    # if True:

                        _marker, _target = target.pop(0)

                        argmin = np.abs(
                            cls.buffer_aux_timestamp - _target).argmin()

                        start = int((prop.SAMPLE_RATE) * t0)
                        stop = int((prop.SAMPLE_RATE) * t1)

                        t = cls.buffer_aux_timestamp[argmin +
                                                     start: argmin + stop]
                        eeg = cls.buffer_eeg_[
                            :, argmin + start: argmin + stop]
                        aux = cls.buffer_aux_[
                            :, argmin + start: argmin + stop]

                        kwargs = {'eeg': eeg,
                                  'aux': aux,
                                  'timestamp': t,
                                  'marker_datetime': _target,
                                  'marker': _marker,
                                  'latency': latency,
                                  }

                        fn(*[cls] + [kwargs[v] for v in arguments])

                    else:
                        logging.warning('Date too old to synchronize')
                        logging.warning(f'Offset: {prop.OFFSET}')
                        logging.warning(
                            f'{datetime.fromtimestamp(last_buffer_timestamp), datetime.fromtimestamp(last_target_timestamp)}')

            marker_slicing_(cls)
        return wrap
    return wrap_wrap
