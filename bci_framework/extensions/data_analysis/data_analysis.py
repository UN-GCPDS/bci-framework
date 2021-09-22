import pickle
import logging
import json
from typing import Optional

import numpy as np
from kafka import KafkaProducer
from openbci_stream.utils import interpolate_datetime

from bci_framework.extensions import properties as prop
# from .utils import loop_consumer, fake_loop_consumer, thread_this, subprocess_this, marker_slice

# Set logger
logging.root.name = "DataAnalysis"
logging.getLogger('matplotlib.font_manager').disabled = True
logging.getLogger().setLevel(logging.WARNING)


########################################################################
class Transformers:
    """Used to preprocess EEG streams."""

    # ----------------------------------------------------------------------
    def centralize(self, x: np.array, normalize: bool = False, axis: int = 0) -> np.array:
        """Crentralize array.

        Remove the mean to all axis.

        Parameters
        ----------
        x
            Input array of shape (`channels, time`).
        normalize
            Return array with maximun amplitude equal to 1.
        axis
            Axis to centralize.

        Returns
        -------
        array
            Centralized array.
        """

        cent = np.nan_to_num(np.apply_along_axis(
            lambda x_: x_ - x_.mean(), 1, x))

        if normalize:
            if normalize == True:
                normalize = 1
            return np.nan_to_num(np.apply_along_axis(lambda x_: normalize * (x_ / (x_.max() - x_.min())), 1, cent))

        return cent


########################################################################
class DataAnalysis:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, enable_produser=False):
        """"""
        self._pivot = None
        if enable_produser:
            self._enable_commands()

        self.transformers_ = {}
        self.transformers_aux_ = {}

    # ----------------------------------------------------------------------
    def _enable_commands(self):
        """"""
        try:
            self.kafka_producer = KafkaProducer(
                bootstrap_servers=[f'{prop.HOST}:9092'],
                compression_type='gzip',
                value_serializer=pickle.dumps,
            )
        except:
            logging.error('Kafka not available!')
            self.kafka_producer = None

    # ----------------------------------------------------------------------
    def send_command(self, command: str, value: Optional[dict] = {}) -> None:
        """"""
        if hasattr(self, 'kafka_producer'):

            if self.kafka_producer is None:
                logging.error('Kafka not available!')
            else:
                data = {'command': command,
                        'value': data,
                        }
                self.kafka_producer.send('command', data)
        else:
            logging.error(
                "To send commands add the argument 'enable_produser=True' on the declaration of EEGStream")

    # ----------------------------------------------------------------------
    def send_annotation(self, description: str, duration: Optional[int] = 0) -> None:
        """"""
        if hasattr(self, 'kafka_producer'):
            if self.kafka_producer is None:
                logging.error('Kafka not available!')
            else:
                self.kafka_producer.send('annotation', {
                    'action': 'annotation',
                    'duration': duration,
                    'description': description,
                })
        else:
            logging.error(
                "To send commands add the argument 'enable_produser=True' on the declaration of EEGStream")

    # ----------------------------------------------------------------------
    def send_feedback(self, kwargs) -> None:
        """"""
        self.generic_produser('feedback', kwargs)

    # ----------------------------------------------------------------------
    def generic_produser(self, topic: str, data: str) -> None:
        """"""
        if hasattr(self, 'kafka_producer'):

            if self.kafka_producer is None:
                logging.error('Kafka not available!')
            else:
                self.kafka_producer.send(topic, data)
                # self.kafka_producer.send(topic, 888)
        else:
            logging.error(
                "To send commands add the argument 'enable_produser=True' on the declaration of EEGStream")

    # ----------------------------------------------------------------------
    def update_buffer(self, eeg: np.ndarray = None, aux: np.ndarray = None, timestamp: float = None) -> None:
        """Uppdate the buffers.

        Parameters
        ----------
        eeg
            The new EEG array
        aux
            The new AUX array
        """

        if not eeg is None:

            c = eeg.shape[1]

            self.buffer_eeg_ = np.roll(self.buffer_eeg_, -c, axis=1)
            self.buffer_eeg_[:, -c:] = eeg

            self.buffer_timestamp_ = np.roll(
                self.buffer_timestamp_, -c, axis=0)
            self.buffer_timestamp_[-c:] = np.zeros(eeg.shape[1])
            self.buffer_timestamp_[-1] = timestamp

            if hasattr(self, 'buffer_eeg_split'):
                self.buffer_eeg_split = np.roll(
                    self.buffer_eeg_split, -c)

        if not aux is None:
            d = aux.shape[1]

            self.buffer_aux_ = np.roll(self.buffer_aux_, -d, axis=1)
            self.buffer_aux_[:, -d:] = aux

            self.buffer_aux_timestamp_ = np.roll(
                self.buffer_aux_timestamp_, -d, axis=0)
            self.buffer_aux_timestamp_[-d:] = np.zeros(aux.shape[1])
            self.buffer_aux_timestamp_[-1] = timestamp

            if hasattr(self, 'buffer_aux_split'):
                self.buffer_aux_split = np.roll(
                    self.buffer_aux_split, -d)

    # ----------------------------------------------------------------------
    def _get_factor_near_to(self, x: int, n: Optional[int] = 1000) -> int:
        """Get the integer number factor of `x` nearest to `n`.

        This factor is used to fast resampling.

        Parameters
        ----------
        x
            Samples.
        n
            Near factor

        Returns
        -------
        int
            Factor.
        """
        a = np.array(
            [(x) / np.arange(max(1, (x // n) - 10), (x // n) + 10)])[0]
        a[a % 1 != 0] = 0
        return int(a[np.argmin(np.abs(a - n))])

    # ----------------------------------------------------------------------
    def _create_resampled_buffer(self, x: int, resampling: Optional[int] = 1000) -> np.ndarray:
        """"""
        f = self._get_factor_near_to(x, resampling)
        self.buffer_eeg_split = np.zeros(x)
        index = np.linspace(0, x, f + 1).astype(int)[:-1]
        self.buffer_eeg_split[index] = 1

        if prop.CONNECTION == 'wifi' and prop.DAISY:
            x = x * 2

        f = self._get_factor_near_to(x, resampling)
        self.buffer_aux_split = np.zeros(x)
        index = np.linspace(0, x, f + 1).astype(int)[:-1]
        self.buffer_aux_split[index] = 1

    # ----------------------------------------------------------------------
    def create_buffer(self, seconds: Optional[int] = 30, aux_shape: Optional[int] = 3, fill: Optional[int] = 0, resampling: Optional[int] = 1000):
        """Create a buffer with fixed time length.

        Since the `loop_consumer` iterator only return the last data package, the
        object `buffer_eeg` and `buffer_aux` will retain a old data.

        Parameters
        ----------
        seconds
            How many seconds will content the buffer.
        aux_shape
            Define the shape of aux array.
        fill
            Initialize buffet with this value.
        resampling
            The resampling size.
        """

        chs = len(prop.CHANNELS)
        time = prop.SAMPLE_RATE * seconds

        self._create_resampled_buffer(abs(time), resampling=resampling)

        self.buffer_eeg_ = np.empty((chs, time))
        self.buffer_eeg_.fill(fill)

        if prop.CONNECTION == 'wifi' and prop.DAISY:
            self.buffer_aux_ = np.empty((aux_shape, time * 2))
        else:
            self.buffer_aux_ = np.empty((aux_shape, time))

        self.buffer_aux_.fill(fill)
        self.buffer_timestamp_ = np.zeros(time)
        self.buffer_aux_timestamp_ = np.zeros(time)

    # ----------------------------------------------------------------------
    def set_transformers(self, transformers):
        """"""
        self.transformers_ = transformers

    # ----------------------------------------------------------------------
    def add_transformers(self, transformers):
        """"""
        for name in transformers:
            self.transformers_[name] = transformers[name]

    # ----------------------------------------------------------------------
    def remove_transformers(self, transformers):
        """"""
        for tr in transformers:
            if tr in self.transformers_:
                self.transformers_.pop(tr)

    # ----------------------------------------------------------------------
    def clear_transformers(self):
        """"""
        self.transformers_ = {}

    # ----------------------------------------------------------------------
    def set_transformers_aux(self, transformers):
        """"""
        self.transformers_aux_ = transformers

    # ----------------------------------------------------------------------
    def add_transformes_aux(self, transformers):
        """"""
        self.transformers_aux_.extend(transformers)

    # ----------------------------------------------------------------------
    def clear_transformers_aux(self):
        """"""
        self.transformers_aux_ = []

    # ----------------------------------------------------------------------
    @property
    def buffer_eeg(self):
        """"""
        eeg = self.buffer_eeg_.copy()
        for tr in self.transformers_.copy():

            kwargs = self.transformers_[tr][1]

            if 'pivot' in kwargs:
                kwargs['pivot'] = self._pivot

            eeg = self.transformers_[tr][0](eeg, **kwargs)

            # logging.warning(str(eeg.shape))
            # logging.warning(str(kwargs))
        return eeg

    # ----------------------------------------------------------------------
    @property
    def buffer_aux(self):
        """"""
        aux = self.buffer_aux_.copy()
        for tr in self.transformers_aux_:
            aux = tr(aux)
        return aux

    # ----------------------------------------------------------------------
    @property
    def buffer_eeg_resampled(self):
        """"""
        return self.buffer_eeg[:, np.argwhere(self.buffer_eeg_split == 1)][:, :, 0]

    # ----------------------------------------------------------------------
    @property
    def buffer_aux_resampled(self):
        """"""
        return self.buffer_aux[:, np.argwhere(self.buffer_aux_split == 1)][:, :, 0]

    # ----------------------------------------------------------------------
    @property
    def buffer_timestamp_resampled(self):
        """"""
        t = self.buffer_timestamp
        if t.shape[0]:
            return t[np.argwhere(self.buffer_eeg_split == 1)][:, 0]
        else:
            return np.array([])

    # ----------------------------------------------------------------------
    @property
    def buffer_timestamp(self):
        """"""
        try:
            return interpolate_datetime(self.buffer_timestamp_)
        except:
            return self.buffer_timestamp_

    # ----------------------------------------------------------------------
    @property
    def buffer_aux_timestamp(self):
        """"""
        try:
            return interpolate_datetime(self.buffer_aux_timestamp_)
        except:
            return self.buffer_aux_timestamp_

