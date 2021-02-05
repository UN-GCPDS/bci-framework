import signal
import atexit
import os
import sys

sys.stderr = open(os.path.join(os.getenv('BCISTREAM_HOME'),
                               'records', 'log.stderr'), 'w')
sys.stdout = open(os.path.join(os.getenv('BCISTREAM_HOME'),
                               'records', 'log.stdout'), 'w')

# from datetime import datetime
from openbci_stream.utils import HDF5Writer

from bci_framework.extensions import properties as prop
from bci_framework.extensions.visualizations.utils import loop_consumer


########################################################################
class RecordTransformer:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

        now = datetime.now()

        filename = now.strftime('%x-%X').replace('/', '_').replace(':', '_')
        records_dir = os.path.join(os.getenv('BCISTREAM_HOME'), 'records')
        os.makedirs(records_dir, exist_ok=True)
        self.writer = HDF5Writer(os.path.join(
            records_dir, f'record-{filename}.h5'))

        header = {'sample_rate': prop.SAMPLE_RATE,
                  'streaming_sample_rate': prop.STREAMING_PACKAGE_SIZE,
                  'datetime': now.timestamp(),
                  'montage': prop.MONTAGE_NAME,
                  'channels': prop.CHANNELS,
                  }
        self.writer.add_header(header, prop.HOST)

        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)
        atexit.register(self.stop)

        self.save_data()

    # ----------------------------------------------------------------------
    @loop_consumer
    def save_data(self, data, topic, **kwargs):
        """"""
        # os.environ['BCI_RECORDING'] = 'True'

        if not self.writer.f.isopen:
            return

        if topic == 'eeg':
            dt = data.value['context']['binary_created']
            # dt = data.value['context']['created']
            # dt = data.timestamp / 1000
            eeg, aux = data.value['data']
            self.writer.add_eeg(eeg, dt)
            self.writer.add_aux(aux)
            # print(dt)

        elif topic == 'marker':
            dt = data.timestamp / 1000
            # dt = data.value['datetime']
            marker = data.value['marker']
            self.writer.add_marker(marker, dt)

        elif topic == 'annotation':
            onset = data.timestamp / 1000
            # onset = data.value['onset']
            duration = data.value['duration']
            description = data.value['description']
            self.writer.add_annotation(onset, duration, description)

    # ----------------------------------------------------------------------
    def stop(self, *args, **kwargs):
        """"""
        self.writer.close()


if __name__ == '__main__':
    RecordTransformer()

