import pickle
from typing import Optional

import numpy as np
from kafka import KafkaProducer

from ...extensions import properties as prop
from .utils import loop_consumer, fake_loop_consumer

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
        self.boundary = False
        if enable_produser:
            self._enable_commands()

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
    def send_command(self, command):
        """"""
        if hasattr(self, 'kafka_producer'):

            if self.kafka_producer is None:
                logging.error('Kafka not available!')
            else:
                data = {'command': command}
                self.kafka_producer.send('command', data)
        else:
            logging.error(
                "To send commands add the argument 'enable_produser=True' on the declaration of EEGStream")

    # ----------------------------------------------------------------------
    def send_annotationn(self, description, duration=0):
        """"""
        self.kafka_producer.send({
            'action': 'annotation',
            'annotation': {'duration': duration,
                           # 'onset': datetime.now().timestamp(),
                           'description': description},
        })

    # ----------------------------------------------------------------------
    def update_buffer(self, eeg: np.ndarray, aux: np.ndarray):
        """Uppdate the buffers.

        Parameters
        ----------
        eeg
            The new EEG array
        aux
            The new AUX array
        """

        c = eeg.shape[1]

        if self.boundary is False:
            self.buffer_eeg = np.roll(self.buffer_eeg, -c, axis=1)
            self.buffer_eeg[:, -c:] = eeg

            if hasattr(self, 'buffer_eeg_split'):
                self.buffer_eeg_split = np.roll(self.buffer_eeg_split, -c)

            if not aux is None:
                d = aux.shape[1]
                self.buffer_aux = np.roll(self.buffer_aux, -d, axis=1)
                self.buffer_aux[:, -d:] = aux

        else:
            roll = 0
            if self.boundary + c >= self.buffer_eeg.shape[1]:
                roll = self.buffer_eeg.shape[1] - (self.boundary + c)
                self.buffer_eeg = np.roll(self.buffer_eeg, -roll, axis=1)
                self.buffer_eeg[:, -eeg.shape[1]:] = eeg
                self.buffer_eeg = np.roll(self.buffer_eeg, roll, axis=1)

            else:
                self.buffer_eeg[:, self.boundary:self.boundary + c] = eeg

            self.boundary += c
            self.boundary = self.boundary % self.buffer_eeg.shape[1]

            if not aux is None:
                d = aux.shape[1]

                roll = 0
                if self.boundary_aux + d >= self.buffer_aux.shape[1]:
                    roll = self.boundary_aux + d

                if roll:
                    self.buffer_aux = np.roll(self.buffer_aux, -roll, axis=1)

                if (self.buffer_aux[:, self.boundary_aux:self.boundary_aux + d]).shape != aux.shape:
                    l = self.buffer_aux[:,
                                        self.boundary_aux:self.boundary_aux + d].shape[1]
                    logging.warning([l, aux.shape[1]])

                    self.buffer_aux[:,
                                    self.boundary_aux:self.boundary_aux + d] = aux[:, :l]
                else:
                    self.buffer_aux[:,
                                    self.boundary_aux:self.boundary_aux + d] = aux

                if roll:
                    self.buffer_aux = np.roll(self.buffer_aux, roll, axis=1)

                self.boundary_aux += d
                self.boundary_aux = self.boundary_aux % self.buffer_aux.shape[1]

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
        a = np.array([(x) / np.arange(max(1, (x // n) - 10), (x // n) + 10)])[0]
        a[a % 1 != 0] = 0
        return int(a[np.argmin(np.abs(a - n))])

    # ----------------------------------------------------------------------
    def _create_resampled_buffer(self, x: int, samples: Optional[int] = 1000) -> np.ndarray:
        """"""
        f = self._get_factor_near_to(x, samples)
        self.buffer_eeg_split = np.zeros(x)
        index = np.linspace(0, x, f + 1).astype(int)[:-1]
        self.buffer_eeg_split[index] = 1

    # ----------------------------------------------------------------------
    def create_buffer(self, seconds: Optional[int] = 30, aux_shape: Optional[int] = 3, fill: Optional[int] = 0, samples: Optional[int] = 1000):
        """Create a buffer with fixed time length.

        Since the `loop_consumer` iteraror only return the last data package, the
        object `buffer_eeg` and `buffer_aux` will retain a longer (in time) data.

        Parameters
        ----------
        seconds
            How many seconds will content the buffer.
        aux_shape
            Define the shape of aux array.
        fill
            Initialize buffet with this value
        """

        chs = len(prop.CHANNELS)
        time = prop.SAMPLE_RATE * seconds

        self._create_resampled_buffer(
            prop.SAMPLE_RATE * np.abs(seconds), samples=samples)

        self.buffer_eeg = np.empty((chs, time))
        self.buffer_eeg.fill(fill)
        self.buffer_aux = np.empty((aux_shape, time))
        self.buffer_aux.fill(fill)

    # ----------------------------------------------------------------------
    @property
    def buffer_eeg_resampled(self):
        """"""
        return self.buffer_eeg[:, np.argwhere(self.buffer_eeg_split == 1)]

    # ----------------------------------------------------------------------
    @property
    def buffer_aux_resampled(self):
        """"""
        return self.buffer_aux[:, np.argwhere(self.buffer_eeg_split == 1)]




