from bci_framework.extensions.visualizations import EEGStream, loop_consumer, fake_loop_consumer
from bci_framework.extensions import properties as prop

import logging
import numpy as np
from datetime import datetime
import seaborn as snb


########################################################################
class Stream(EEGStream):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """"""
        super().__init__(enable_produser=True)

        # self.N = int(prop.SAMPLE_RATE / prop.STREAMING_PACKAGE_SIZE)

        self.axis_wave = self.add_subplot(221)
        self.axis_hist = self.add_subplot(223)
        self.axis_log = self.add_subplot(222)
        self.axis_time = self.add_subplot(224)

        self.subplots_adjust(hspace=0.3)

        # self.wave_line = self.axis_wave.plot([0], [0])[0]
        # self.wave_line2 = self.axis_wave.vline()[0]

        self.latency_time = self.axis_time.plot([0], [0])[0]

        self.timestamp_rises = np.array([])

        self.markers_timestamps = []

        self.latencies = [0]

        # self.create_boundary(self.axis, -0.5, 1.5)

        # self.axis_wave.set_title('Synchronizations')
        # self.axis_wave.set_xlabel('Elapsed time [s]')
        # self.axis_wave.set_ylabel('Amplitude')
        # self.axis_wave.grid(True)

        self.axis_time.set_title('Latency timeline')
        self.axis_time.set_xlabel('Samples analyzed')
        self.axis_time.set_ylabel('Latency (ms)')
        self.axis_time.grid(True)

        # self.axis_time.spines['right'].set_visible(False)
        # self.axis_time.spines['top'].set_visible(False)

        # self.axis.set_ylim(-0.5, 1.5)

        self.create_buffer(10, resampling=1000, fill=-1)

        self.stream()

    # ----------------------------------------------------------------------
    def get_rises(self, data, timestamp):
        """"""
        data = data.copy()

        data[data > data.mean()] = 1
        data[data < data.mean()] = 0

        diff = np.diff(data, prepend=0)
        diff[diff < 0] = 0
        diff[0] = 0
        diff[-1] = 0

        return timestamp[np.nonzero(diff)[0]], diff

    # ----------------------------------------------------------------------
    @loop_consumer('eeg', 'marker')
    def stream(self, data, topic, frame, latency):
        """"""

        if topic != 'marker':
            return

        # logging.warning(f"L: {latency:.2f}")

        latencies = np.array(self.latencies)

        if latencies.size > 5:
            latencies = latencies[3:]

            Q1 = np.quantile(latencies, 0.25)
            Q3 = np.quantile(latencies, 0.75)
            IQR = Q3 - Q1
            latencies = latencies[latencies < (Q3 + 1.5 * IQR)]
            latencies = latencies[latencies > (Q1 - 1.5 * IQR)]

        LATENCY = np.mean(latencies)

        # Rise plot
        self.axis_wave.clear()
        aux = self.buffer_aux[0]
        aux[aux == -1] = aux[-1]
        aux = aux - aux.min()
        aux = aux / aux.max()
        self.axis_wave.set_ylim(-0.1, 1.1)
        self.axis_wave.set_xlim(-1, 1)

        self.axis_wave.set_title('Event synchronization')
        self.axis_wave.set_xlabel('Time [ms]')
        self.axis_wave.set_ylabel('Amplitude')
        self.axis_wave.grid(True)

        self.timestamp_rises, diff = self.get_rises(aux, self.buffer_timestamp)

        # self.wave_line2.set_data(t, diff)

        q = np.argwhere(diff > 0)
        # logging.warning(q)
        if q.size > 3:
            v = q[-3]
            # window = aux.copy()
            window = aux[int(v - prop.SAMPLE_RATE):int(v + prop.SAMPLE_RATE)]
            t = np.linspace(-1, 1, window.shape[0])
            self.axis_wave.plot(t * 1000, window, label='input signal')
            self.axis_wave.vlines([0], -1, 2, color='k',
                                  linestyle='--', label='event')
            self.axis_wave.set_xlim(-250, 250)
            self.axis_wave.vlines([LATENCY], -1, 2,
                                  color='r', linestyle='--', label='latency')
            self.axis_wave.legend(loc=4)

        # Histogram
        if latencies.size > 5:
            self.axis_hist.clear()
            self.axis_hist.grid(True, zorder=0)
            snb.histplot(latencies, kde=True, ax=self.axis_hist, zorder=10)
            self.axis_hist.set(
                xlabel='Latency [ms]', ylabel='Count', title='Latency histogram')

        # Latencies
        if latencies.size > 3:
            t = range(len(latencies))
            self.latency_time.set_data(t, latencies)
            self.axis_time.set_xlim(0, t[-1])
            self.axis_time.set_ylim(latencies.min(), latencies.max())

        self.axis_log.clear()
        self.axis_log.axis('off')

        if latencies.size > 1:

            for i, text in enumerate([
                ('count', len(latencies)),
                ('mean', np.mean(latencies)),
                ('median', np.median(latencies)),
                # ('std', np.std(latencies)),
                ('var', np.var(latencies)),
                ('min', np.min(latencies)),
                ('max', np.max(latencies))
            ]):

                self.axis_log.text(
                    10, 25 - 2 * i, f'{text[0]}:', fontdict={'weight': 'bold', 'size': 16, 'ha': 'right'})

                if i == 0:
                    label = f'{int(text[1])}'
                else:
                    label = f'{text[1]:.3f} ms'
                self.axis_log.text(11, 25 - 2 * i, label,
                                   fontdict={'size': 16, })

        self.axis_log.set_xlim(0, 30)
        self.axis_log.set_ylim(0, 30)

    # elif topic == 'marker' and self.timestamp_rises.size > 0:

        self.markers_timestamps.append(
            datetime.fromtimestamp(data.timestamp / 1000))
        # self.markers_timestamps.append(datetime.fromtimestamp(data.value['datetime']))
        if len(self.markers_timestamps) >= 3:
            self.markers_timestamps.pop(0)

        x = []
        for mt in self.markers_timestamps:
            for rt in self.timestamp_rises:
                x.append((mt - datetime.fromtimestamp(rt)).total_seconds())

        x = np.array(x)
        sg = np.sign(x[np.argmin(abs(x))])
        latency = sg * min(abs(x)) * 1000

        self.latencies.append(latency)

        # if len(self.latencies) >= 20:
            # self.latencies.pop(0)

        self.feed()

        # logging.warning(f"Latency: {latency:.3f} ms")
        self.send_feedback({'command': 'set_latency',
                            'value': np.mean(latencies),
                            })


if __name__ == '__main__':
    Stream()
