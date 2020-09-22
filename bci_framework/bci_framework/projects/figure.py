from threading import Thread
from multiprocessing import Process

import time
import threading
import logging
from matplotlib.figure import Figure

from ..projects import properties as prop

from io import BytesIO
from queue import Queue

from flask import Flask, Response, request

import sys

import mne

import matplotlib
from matplotlib import pyplot

from cycler import cycler
import numpy as np

# matplotlib.use('agg')

pyplot.style.use('dark_background')
q = matplotlib.cm.get_cmap('rainbow')
matplotlib.rcParams['axes.prop_cycle'] = cycler(
    color=[q(m) for m in np.linspace(0, 1, 16)]
)

matplotlib.rcParams['figure.dpi'] = 60
matplotlib.rcParams['font.family'] = 'monospace'
matplotlib.rcParams['font.size'] = 15


logger = logging.getLogger("mne")
logger.setLevel(logging.CRITICAL)


# ----------------------------------------------------------------------
def subprocess_this(fn):
    """"""

    def wra(self, *args, **kwargs):
        c = Process(target=fn, args=(self, *args))
        c.start()

    return wra


# ----------------------------------------------------------------------
def thread_this(fn):
    """"""

    def wra(self, *args, **kwargs):
        c = Thread(target=fn, args=(self, *args))
        c.start()

    return wra


########################################################################
class StreamEvent:
    """An Event-like class that signals all active clients when a new frame is
    available.
    """

    # ----------------------------------------------------------------------
    def __init__(self):
        self.events = {}
        logging.debug(f'Instantiate {self!r}')

    # ----------------------------------------------------------------------
    def wait(self):
        """Invoked from each client's thread to wait for the next frame."""
        logging.debug('Waiting...')
        ident = threading.get_ident()
        if ident not in self.events:
            # this is a new client
            # add an entry for it in the self.events dict
            # each entry has two elements, a threading.Event() and a timestamp
            self.events[ident] = [threading.Event(), time.time()]
        return self.events[ident][0].wait()

    # ----------------------------------------------------------------------
    def set(self):
        """Invoked by the stream thread when a new frame is available."""

        logging.debug('Setting...')

        now = time.time()
        to_remove = []
        for ident, event in self.events.items():
            if not event[0].isSet():
                # if this client's event is not set, then set it
                # also update the last set timestamp to now
                event[0].set()
                event[1] = now
            else:
                # if the client's event is already set, it means the client
                # did not process a previous frame
                # if the event stays set for more than 60 seconds, then assume
                # the client is gone and remove it
                if now - event[1] > 60:
                    to_remove.append(ident)

        for remove in to_remove:
            del self.events[remove]

    # ----------------------------------------------------------------------
    def clear(self):
        """Invoked from each client's thread after a frame was processed."""
        logging.debug('Clearing...')
        self.events[threading.get_ident()][0].clear()


########################################################################
class FigureStream(Figure):

    __class_attr = {
        'thread': None,  # background thread that reads frames from stream
        'frame': None,  # current frame is stored here by background thread
        'last_access': 0,  # time of last client access to the source,
        # 'keep_alive': time.time(),
        'event': StreamEvent(),
    }

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """Start the background stream thread if it isn't running yet."""
        # logging.debug(f'Instantiate {self!r}')
        super().__init__(*args, **kwargs)
        self.__output = BytesIO()
        self.__buffer = Queue(maxsize=60)

        self.boundary = False
        self.subsample = None
        self.size = 'auto'
        # self.tight_layout(rect=[0, 0.03, 1, 0.95])

        self.app = Flask(__name__)
        self.app.add_url_rule('/', view_func=self.__video_feed)
        self.app.add_url_rule('/mode', view_func=self.__mode)
        self.app.add_url_rule('/feed', view_func=self.__feed)

        if len(sys.argv) > 1:
            port = sys.argv[1]
        else:
            port = '5000'

        Thread(
            target=self.app.run,
            kwargs={'host': '0.0.0.0', 'port': port, 'threaded': True},
        ).start()

    # ----------------------------------------------------------------------
    def __feed(self):
        """"""
        self.feed()
        return 'true'

    # ----------------------------------------------------------------------
    def __mode(self):
        """"""
        return 'visualization'

    # ----------------------------------------------------------------------
    def __get_frames(self):
        """Return the current stream frame."""

        while True:
            self.__class_attr['last_access'] = time.time()
            self.__class_attr['event'].wait()
            self.__class_attr['event'].clear()
            frame = self.__class_attr['frame']
            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
            )

    # #----------------------------------------------------------------------
    # @staticmethod
    # def frames():
    # """"Generator that returns frames from the stream."""
    # raise RuntimeError('Must be implemented by subclasses.')

    # ----------------------------------------------------------------------
    # @classmethod

    def _thread(self):
        """stream background thread."""
        logging.info('Starting stream thread.')
        # frames_iterator = self.frames()
        # for frame in frames_iterator:
        while True:

            try:
                # frame = self.__buffer.get(timeout=5)
                frame = self.__buffer.get()
            except:
                break

            self.__class_attr['frame'] = frame
            self.__class_attr['event'].set()  # send signal to clients
            time.sleep(0)

            # # if there hasn't been any clients asking for frames in
            # # the last 10 seconds then stop the thread
            # if time.time() - self.__class_attr['last_access'] > 10:
                # # frames_iterator.close()
                # logging.info('Stopping stream thread due to inactivity.')
                # break

        self.__class_attr['thread'] = None

    # ----------------------------------------------------------------------
    def __video_feed(self):
        """"""
        if self.size == 'auto':
            width = request.values.get('width', None)
            height = request.values.get('height', None)
            if (
                width and
                height and
                width.replace('.', '').isdigit() and
                height.replace('.', '').isdigit()
            ):
                self.set_size_inches(float(width), float(height))

            dpi = request.values.get('dpi', None)
            if dpi and dpi.replace('.', '').isdigit():
                self.set_dpi(float(dpi))

        else:
            self.set_size_inches(*self.size)
            dpi = request.values.get('dpi', None)
            if dpi and dpi.replace('.', '').isdigit():
                self.set_dpi(float(dpi))

        if self.__class_attr['thread'] is None:
            self.__class_attr['last_access'] = time.time()
            # self.__class_attr['keep_alive'] = time.time()

            # start background frame thread
            self.__class_attr['thread'] = Thread(target=self._thread)
            self.__class_attr['thread'].start()

            # wait until frames are available
            while self.__get_frames() is None:
                time.sleep(10)

        # stream = Stream()

        # time.sleep(10)
        # self.feed()
        # self.feed()
        # time.sleep(10)
        self.feed()
        return Response(
            self.__get_frames(),
            mimetype='multipart/x-mixed-replace; boundary=frame',
        )

    # ----------------------------------------------------------------------
    def clients(self):
        """"""
        return len(self.__class_attr['event'].events)

    # ----------------------------------------------------------------------
    def buffer_size(self):
        """"""
        return self.__buffer.qsize()

    # ----------------------------------------------------------------------
    def feed(self):
        """"""
        self.__output.truncate(0)
        self.__output.seek(0)
        self.canvas.print_figure(
            self.__output, format='jpeg', dpi=self.get_dpi()
        )

        return self.__buffer.put(self.__output.getvalue())

    # ----------------------------------------------------------------------
    def get_info(self):
        """"""
        info = mne.create_info(
            list(prop.CHANNELS.values()),
            sfreq=prop.SAMPLE_RATE,
            ch_types="eeg",
        )
        info.set_montage(prop.MONTAGE_NAME)
        return info

    # ----------------------------------------------------------------------
    def get_montage(self):
        """"""
        montage = mne.channels.make_standard_montage(prop.MONTAGE_NAME)
        return montage

    # ----------------------------------------------------------------------
    def create_lines(self, mode='eeg', time=-15, window='auto', cmap='cool', fill=np.nan, subplot=[1, 1, 1],):
        """"""
        mode = mode.lower()
        sr = prop.SAMPLE_RATE

        if mode == 'eeg':
            channels = len(prop.CHANNELS)
            labels = None
            ylim = 0, 16
        elif mode == 'accel' or mode == 'default':
            channels = 3
            labels = ['X', 'Y', 'Z']
            ylim = -6, 6
            sr = sr / 10
        elif mode == 'analog' and not prop.CONNECTION == 'wifi':
            channels = 3
            labels = ['A5(D11)', 'A6(D12)', 'A7(D13)']
            ylim = 0, 255
        elif mode == 'analog' and prop.CONNECTION == 'wifi':
            channels = 2
            labels = ['A5(D11)', 'A6(D12)']
            ylim = 0, 255
        elif mode == 'digital' and not prop.CONNECTION == 'wifi':
            channels = 5
            labels = ['D11', 'D12', 'D13', 'D17', 'D18']
            ylim = 0, 1.2
        elif mode == 'digital' and prop.CONNECTION == 'wifi':
            channels = 3
            labels = ['D11', 'D12', 'D17']
            ylim = 0, 1.2

        q = matplotlib.cm.get_cmap(cmap)
        matplotlib.rcParams['axes.prop_cycle'] = cycler(
            color=[q(m) for m in np.linspace(0, 1, channels)]
        )

        axis = self.add_subplot(*subplot)

        # pyplot.set_cmap(q)

        if window == 'auto':
            window = self.get_factor_near_to(prop.SAMPLE_RATE * np.abs(time),
                                             n=1000)

        a = np.empty(window)
        a.fill(fill)

        lines = [
            axis.plot(
                a.copy(),
                a.copy(),
                '-',
                label=(labels[i] if labels else None),
            )[0]
            for i in range(channels)
        ]

        if time > 0:
            axis.set_xlim(0, time)
            time = np.linspace(0, time, window)
        else:
            axis.set_xlim(time, 0)
            time = np.linspace(time, 0, window)
        axis.set_ylim(*ylim)

        if mode != 'eeg':
            axis.legend()

        axis.grid(True, color='#ffffff', alpha=0.25, zorder=0)
        lines = np.array(lines)

        return axis, time, lines

    # ----------------------------------------------------------------------
    def create_buffer(self, seconds=30, aux_shape=3, fill=0):
        """"""
        chs = len(prop.CHANNELS)
        time = prop.SAMPLE_RATE * seconds

        self.buffer_eeg = np.empty((chs, time))
        self.buffer_eeg.fill(fill)

        self.buffer_aux = np.empty((aux_shape, time))
        self.buffer_aux.fill(fill)

    # ----------------------------------------------------------------------
    def create_boundary(self, axis, min=0, max=17):
        """"""
        self.boundary = 0
        self.boundary_aux = 0

        # axis = self.gca()
        self.boundary_line = axis.vlines(
            0, min, max, color='w', zorder=99)
        self.boundary_aux_line = axis.vlines(
            0, max, max, color='w', zorder=99)

    # ----------------------------------------------------------------------
    def plot_boundary(self, eeg=True, aux=False):
        """"""
        if eeg and hasattr(self, 'boundary_line'):
            segments = self.boundary_line.get_segments()
            segments[0][:, 0] = [self.boundary / prop.SAMPLE_RATE,
                                 self.boundary / prop.SAMPLE_RATE]
            self.boundary_line.set_segments(segments)
        elif aux and hasattr(self, 'boundary_aux_line'):
            segments = self.boundary_aux_line.get_segments()
            segments[0][:, 0] = [self.boundary_aux
                                 / prop.SAMPLE_RATE, self.boundary_aux / prop.SAMPLE_RATE]
            self.boundary_aux_line.set_segments(segments)

        else:
            logging.warning('No "boundary" to plot')

    # ----------------------------------------------------------------------
    def update_buffer(self, eeg, aux):
        """"""
        if self.boundary is False:
            c = eeg.shape[1]
            self.buffer_eeg = np.roll(self.buffer_eeg, -c, axis=1)
            self.buffer_eeg[:, -c:] = eeg

            if not aux is None:
                d = aux.shape[1]
                self.buffer_aux = np.roll(self.buffer_aux, -d, axis=1)
                self.buffer_aux[:, -d:] = aux

        else:
            c = eeg.shape[1]

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
                self.buffer_aux[:,
                                self.boundary_aux:self.boundary_aux + d] = aux
                if roll:
                    self.buffer_aux = np.roll(self.buffer_aux, roll, axis=1)

                self.boundary_aux += d
                self.boundary_aux = self.boundary_aux % self.buffer_aux.shape[1]

    # ----------------------------------------------------------------------
    def resample(self, x, num, axis=-1):
        """"""
        ndim = x.shape[axis] // num
        logging.warning([ndim, num, x.shape[axis] % num])
        return (x[:, :ndim * num].reshape(x.shape[0], num, ndim).mean(axis=-1))

    # ----------------------------------------------------------------------
    def centralize(self, x, axis=0):
        """"""
        return np.apply_along_axis(lambda x_: x_ - x_.mean(), axis, x)

    # ----------------------------------------------------------------------
    def get_evoked(self):
        """"""
        comment = "bcistream"
        evoked = mne.EvokedArray(
            self.buffer_eeg, self.get_info(), 0, comment=comment, nave=0
        )
        return evoked

    # ----------------------------------------------------------------------
    def get_factor_near_to(self, x, n=1000):
        a = np.array(
            [(x) / np.arange(max(1, (x // n) - 10), (x // n) + 10)])[0]
        a[a % 1 != 0] = 0
        return int(a[np.argmin(np.abs(a - n))])
