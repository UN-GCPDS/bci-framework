"""
======
Record
======

Kafka consumer to save EEG streamings into HDF5 format using the `Data storage
handler <https://openbci-stream.readthedocs.io/en/latest/notebooks/07-data_storage_handler.html>`_
defined in `OpenBCI-Stream <https://openbci-stream.readthedocs.io/en/latest/index.html>`_.
"""

import signal
import atexit
import os
import sys
from typing import TypeVar

if home := os.getenv('BCISTREAM_HOME'):
    sys.stderr = open(os.path.join(home, 'records', 'log.stderr'), 'w')
    sys.stdout = open(os.path.join(home, 'records', 'log.stdout'), 'w')

from datetime import datetime, timedelta
from openbci_stream.utils import HDF5Writer
from openbci_stream.utils.pid_admin import autokill_process
import numpy as np

from bci_framework.extensions.data_analysis import DataAnalysis
from bci_framework.extensions import properties as prop
from bci_framework.extensions.data_analysis.utils import loop_consumer

KafkaStream = TypeVar('kafka-stream')

autokill_process(name=f'bci-framework_records')


########################################################################
class RecordTransformer(DataAnalysis):
    """This consumer is basically an extension."""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)

        now = datetime.now()

        filename = now.strftime('%x-%X').replace('/', '_').replace(':', '_')
        records_dir = os.path.join(
            os.environ.get(
                'BCISTREAM_HOME', os.path.expanduser('~/.bciframework')
            ),
            'records',
        )
        os.makedirs(records_dir, exist_ok=True)
        filename = os.path.join(records_dir, f'record-{filename}.h5')
        self.writer = HDF5Writer(filename)

        header = {
            'sample_rate': prop.SAMPLE_RATE,
            'streaming_sample_rate': prop.STREAMING_PACKAGE_SIZE,
            'datetime': now.timestamp(),
            'montage': prop.MONTAGE_NAME,
            'channels': prop.CHANNELS,
            'channels_by_board': prop.CHANNELS_BY_BOARD,
        }
        self.writer.add_header(header, prop.HOST)

        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)
        atexit.register(self.stop)

        self.save_data()

    # ----------------------------------------------------------------------
    def get_timestamps(self, size, timestamps, topic):
        """"""
        timestamp = []

        for dt in timestamps:

            if prop.CONNECTION == 'wifi' and prop.DAISY and topic == 'aux':
                end_dt = (
                    datetime.fromtimestamp(dt)
                    - timedelta(seconds=size / (prop.SAMPLE_RATE * 2))
                ).timestamp()
            else:
                end_dt = (
                    datetime.fromtimestamp(dt)
                    - timedelta(seconds=size / prop.SAMPLE_RATE)
                ).timestamp()

            timestamp.append(np.linspace(end_dt, dt, size, endpoint=False))

        return np.array(timestamp)

    # ----------------------------------------------------------------------
    @loop_consumer('eeg', 'aux', 'marker', 'annotation')
    def save_data(
        self, data, kafka_stream: KafkaStream, topic: str, **kwargs
    ) -> None:
        """Write data on every strem package.

        Parameters
        ----------
        kafka_stream
            Kafka stream with deserialized data.
        topic
            The topic of the stream.
        """

        if not self.writer.f.isopen:
            return

        if topic in ['eeg', 'aux']:
            timestamp = self.get_timestamps(
                data.shape[1],
                kafka_stream.value['context']['timestamp.binary'],
                topic,
            )
            getattr(self.writer, f'add_{topic}')(
                data, timestamp - prop.OFFSET
            )

            if topic == 'eeg':
                self.writer.add_sampleid(
                    np.array(kafka_stream.value['context']['sample_ids'])
                )

        elif topic == 'marker':
            dt = kafka_stream.value['datetime']
            marker = kafka_stream.value['marker']
            self.writer.add_marker(marker, dt)

        elif topic == 'annotation':
            onset = kafka_stream.value['onset']
            duration = kafka_stream.value['duration']
            description = kafka_stream.value['description']
            self.writer.add_annotation(onset, duration, description)

    # ----------------------------------------------------------------------
    def stop(self, *args, **kwargs) -> None:
        """"""
        self.writer.close()


if __name__ == '__main__':
    RecordTransformer()
