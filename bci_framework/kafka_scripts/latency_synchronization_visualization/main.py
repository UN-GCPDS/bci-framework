from bci_framework.extensions.visualizations import EEGStream, loop_consumer, fake_loop_consumer
from bci_framework.extensions import properties as prop

import logging
import numpy as np
from datetime import datetime
import seaborn as snb

from simple_pid import PID

pid = PID(Kp=2, Ki=0.5, Kd=0.07, setpoint=0,
          sample_time=1, output_limits=(-300, 300))

BUFFER = 15


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
        self.latency_correction = 0

        # self.create_boundary(self.axis, -0.5, 1.5)

        # self.axis_wave.set_title('Synchronizations')
        # self.axis_wave.set_xlabel('Elapsed time [s]')
        # self.axis_wave.set_ylabel('Amplitude')
        # self.axis_wave.grid(True)

        self.frames_names()

        # self.axis_time.spines['right'].set_visible(False)
        # self.axis_time.spines['top'].set_visible(False)

        # self.axis.set_ylim(-0.5, 1.5)

        self.create_buffer(BUFFER, resampling=1000, fill=-1)

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

    def frames_names(self):
        """"""
        self.axis_wave.set_title('Event synchronization')
        self.axis_wave.set_xlabel('Time [ms]')
        self.axis_wave.set_ylabel('Amplitude')
        self.axis_wave.grid(True)

        self.axis_time.set_title('Latency timeline')
        self.axis_time.set_xlabel('Samples analyzed')
        self.axis_time.set_ylabel('Latency (ms)')
        self.axis_time.grid(True)

        self.axis_log.axis('off')

        self.axis_hist.set(
            xlabel='Latency [ms]', ylabel='Count', title='Latency histogram')
        self.axis_hist.grid(True)

    # ----------------------------------------------------------------------
    @loop_consumer('eeg', 'marker')
    def stream(self, data, topic, frame, latency):
        """"""

        if topic != 'marker':
            if len(self.latencies) <= 1 and (frame % 3) == 0:
                self.feed()
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

        latencies = latencies[-60:]
        # LATENCY = np.mean(latencies)

        # Rise plot
        self.axis_wave.clear()
        aux = self.buffer_aux[0]
        aux[aux == -1] = aux[-1]
        aux = aux - aux.min()
        aux = aux / aux.max()
        self.axis_wave.set_ylim(-0.1, 1.1)
        self.axis_wave.set_xlim(-1, 1)

        self.axis_wave.set(
            xlabel='Time [ms]', ylabel='Amplitude', title='Event synchronization')

        # self.axis_wave.set_title('Event synchronization')
        # self.axis_wave.set_xlabel('Time [ms]')
        # self.axis_wave.set_ylabel('Amplitude')
        self.axis_wave.grid(True)

        self.timestamp_rises, diff = self.get_rises(aux, self.buffer_timestamp)

        if len(self.timestamp_rises) > BUFFER * 1.5:
            return

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
            self.axis_wave.vlines([np.mean(latencies)], -1, 2, color='r', linestyle='--',
                                  label='mean latency')
            self.axis_wave.vlines([latencies[-1]], -1, 2, color='g', linestyle='--',
                                  label='last latency')
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
            self.axis_time.set_ylim(
                min([latencies.min(), -50]), max([latencies.max(), 50]))

        self.axis_log.clear()
        self.axis_log.axis('off')

        if latencies.size > 1:

            for i, text in enumerate([
                ('count', f'{len(self.latencies)}'),
                ('mean', f'{np.mean(latencies):.3f} ms'),
                ('median', f'{np.median(latencies):.3f} ms'),
                # ('std', f'{np.std(latencies):.3f}'),
                ('range', f'{latencies.max()-latencies.min():.3f} ms'),
                ('var', f'{latencies.var():.3f}'),
                ('min', f'{latencies.max():.3f} ms'),
                ('max', f'{latencies.min():.3f} ms'),
                ('latency correction', f'{self.latency_correction:.3f} ms'),
                ('error',
                 f'$\pm${abs(latencies.max()-latencies.min()/2):.3f} ms'),
            ]):

                self.axis_log.text(
                    10, 25 - 2 * i, f'{text[0]}:', fontdict={'weight': 'bold', 'size': 16, 'ha': 'right'})

                self.axis_log.text(
                    11, 25 - 2 * i, text[1], fontdict={'size': 16, })

        self.axis_log.set_xlim(0, 30)
        self.axis_log.set_ylim(0, 30)

    # elif topic == 'marker' and self.timestamp_rises.size > 0:

        # self.markers_timestamps.append(
            # datetime.fromtimestamp(data.timestamp / 1000))
        self.markers_timestamps.append(
            datetime.fromtimestamp(data.value['datetime']))
        if len(self.markers_timestamps) > 7:
            self.markers_timestamps.pop(0)

        # if len(self.markers_timestamps) < 3:
            # return

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

        self.latency_correction = -pid(np.mean(self.latencies[-6:]))

        # if abs(self.latency_correction) == 400:
            # self.latency_correction = -self.latency_correction

        # self.latency_correction = -pid(LATENCY)
        self.send_feedback({'name': 'set_latency',
                            'value': self.latency_correction,
                            })


if __name__ == '__main__':
    Stream()
