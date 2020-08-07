from datetime import datetime

from openbci_stream.handlers import HDF5_Writer
from bci_framework.projects import properties as prop
from bci_framework.projects.utils import loop_consumer, fake_loop_consumer

import signal
import atexit
import os


########################################################################
class RecordTransformer:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

        now = datetime.now()

        filename = now.strftime('%x%X').replace('/', '_').replace(':', '_')

        self.writer = HDF5_Writer(os.path.join(
            'records', f'record-{filename}.h5'))
        # self.writer = HDF5_Writer(f'{filename}.h5')

        header = {'sample_rate': prop.SAMPLE_RATE,
                  'streaming_sample_rate': prop.STREAMING_SAMPLE_RATE,
                  'datetime': now.timestamp(),
                  'montage': prop.MONTAGE_NAME,
                  'channels': prop.MONTAGE,
                  }
        self.writer.add_header(header)

        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)
        atexit.register(self.stop)

        self.save_data()

    # ----------------------------------------------------------------------
    # @loop_consumer

    @fake_loop_consumer
    def save_data(self, data):
        """"""
        # self.writer.add_eeg(data.value['data'], data.timestamp / 1000)
        self.writer.add_eeg(data.T, datetime.now().timestamp())

    # ----------------------------------------------------------------------
    def stop(self, *args, **kwargs):
        """"""
        self.writer.close()


if __name__ == '__main__':
    RecordTransformer()

