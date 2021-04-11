import os
import json
import random
import logging
from browser import timer, html, document
from datetime import datetime

from radiant.utils import WebSocket

from bci_framework.extensions.stimuli_delivery.utils import Widgets as w

StimuliServer = None

logging.root.name = "StimuliDelivery:Brython"
logging.getLogger().setLevel(logging.WARNING)


########################################################################
class DeliveryInstance_:
    """"""

    # ----------------------------------------------------------------------
    @classmethod
    def both(cls, method):
        """Decorator for execute method in both environs, dashboard and delivery.

        This decorator only works from dashboard calls.
        """

        def wrap(self, *args, **kwargs):

            if self._bci_mode == 'dashboard':
                try:  # To call as decorator and as function
                    method(self, *args, **kwargs)
                except TypeError:
                    method(*args, **kwargs)
                self.ws.send({'action': 'feed',
                              'method': method.__name__,
                              'args': list(args),  # prevent ellipsis objects
                              'kwargs': dict(kwargs),
                              })

        wrap.no_decorator = method
        return wrap

    # ----------------------------------------------------------------------
    @classmethod
    def rboth(cls, method):
        """Decorator for execute method in both environs, dashboard and delivery.

        This decorator only works from remote calls.
        """

        def wrap(self, *args, **kwargs):

            if self._bci_mode == 'stimuli':
                try:  # To call as decorator and as function
                    method(self, *args, **kwargs)
                except TypeError:
                    method(*args, **kwargs)
                self.ws.send({'action': 'feed',
                              'method': method.__name__,
                              'args': list(args),  # prevent ellipsis objects
                              'kwargs': dict(kwargs),
                              })

        wrap.no_decorator = method
        return wrap

    # ----------------------------------------------------------------------
    @classmethod
    def remote(cls, method):
        """Decorator for execute methon only in delivery environ.

        This decorator only works from dashboard calls.
        """

        def wrap(self, *args, **kwargs):

            if self._bci_mode == 'dashboard':
                self.ws.send({'action': 'feed',
                              'method': method.__name__,
                              'args': list(args),  # prevent ellipsis objects
                              'kwargs': dict(kwargs),
                              })

        wrap.no_decorator = method
        return wrap

    # ----------------------------------------------------------------------
    @classmethod
    def local(cls, method):
        """Decorator for execute methon only in dashboard environ.

        This decorator only works from dashboard calls.
        """

        def wrap(self, *args, **kwargs):
            if self._bci_mode == 'dashboard':
                try:  # To call as decorator and as function
                    method(self, *args, **kwargs)
                except TypeError:
                    method(*args, **kwargs)

        wrap.no_decorator = method
        return wrap

    # ----------------------------------------------------------------------
    @classmethod
    def event(cls, method):
        """Decorator for execute method in both environs, dashboard and delivery.


        This decorator only works in both environs.
        """

        def wrap(self, *args, **kwargs):

            if hasattr(method, 'no_decorator'):
                method_ = method.no_decorator
            else:
                method_ = method

            if self._bci_mode == 'dashboard':
                try:
                    cls.both(method_)(self, *args, **kwargs)
                except TypeError:
                    cls.both(method_)(*args, **kwargs)
            else:
                try:
                    cls.rboth(method_)(self, *args, **kwargs)
                except:
                    cls.rboth(method_)(*args, **kwargs)

        wrap.no_decorator = method
        return wrap


DeliveryInstance = DeliveryInstance_()


########################################################################
class BCIWebSocket(WebSocket):
    """"""

    # ----------------------------------------------------------------------
    def on_open(self, evt):
        """"""
        self.send({'action': 'register'})

    # ----------------------------------------------------------------------
    def on_message(self, evt):
        """"""
        data = json.loads(evt.data)
        if 'method' in data:
            try:
                getattr(self.main, data['method']).no_decorator(
                    self.main, *data['args'], **data['kwargs'])
            except:
                getattr(self.main, data['method'])(
                    *data['args'], **data['kwargs'])

    # ----------------------------------------------------------------------
    def on_close(self, evt):
        """"""
        getattr(self.main, 'stop', lambda: None)()
        # print('on_close', self.ip_)
        timer.set_timeout(lambda: self.__init__(self.ip_), 1000)


########################################################################
class Pipeline:
    """"""

    # ----------------------------------------------------------------------
    def _build_pipeline(self, pipeline):
        """"""
        explicit_pipeline = []
        for method, var in pipeline:
            if isinstance(var, str):
                var = w.get_value(var)
            if isinstance(var, [list, tuple, set]):
                var = random.randint(*var)
            explicit_pipeline.append([method, var])

        return explicit_pipeline

    # ----------------------------------------------------------------------
    def run_pipeline(self, pipeline, trials, callback=None):
        """"""
        self._callback = callback
        self.show_progressbar(len(trials) * len(pipeline))
        self._run_pipeline(pipeline, trials)

    # ----------------------------------------------------------------------
    def _run_pipeline(self, pipeline, trials):
        """"""
        pipeline_m, timeouts = zip(*self._build_pipeline(pipeline))
        trial = trials.pop(0)

        self.wrap_fn(pipeline_m[0], trial)()  # First pipeline
        self._timeouts = []
        for i in range(1, len(pipeline_m)):

            # Others pipelines
            t = timer.set_timeout(self.wrap_fn(
                pipeline_m[i], trial), sum(timeouts[:i]))
            self._timeouts.append(t)

            if t_ := timer.set_timeout(self.increase_progress, sum(timeouts[:i])):
                self._timeouts.append(t_)

        if trials:
            t = timer.set_timeout(lambda: self._run_pipeline(
                pipeline, trials), sum(timeouts))
            self._timeouts.append(t)
            if t_ := timer.set_timeout(self.increase_progress, sum(timeouts)):
                self._timeouts.append(t_)

        elif self._callback:
            t = timer.set_timeout(lambda: DeliveryInstance.both(
                self._callback)(self), sum(timeouts))
            self._timeouts.append(t)

    # ----------------------------------------------------------------------
    def wrap_fn(self, fn, trial):
        """"""
        fn_ = fn
        trial_ = trial

        def inner():
            if isinstance(trial, list):
                DeliveryInstance.both(fn_)(self, *trial_)
            elif isinstance(trial, dict):
                DeliveryInstance.both(fn_)(self, **trial_)
            else:
                DeliveryInstance.both(fn_)(self, trial_)

        return inner

    # ----------------------------------------------------------------------
    def stop_pipeline(self):
        """"""
        for t in self._timeouts:
            timer.clear_timeout(t)
        self.set_progress(0)
        if self._callback:
            self.call_callback()

    # ----------------------------------------------------------------------
    def call_callback(self):
        """"""
        DeliveryInstance.both(self._callback)(self)


########################################################################
class StimuliAPI(Pipeline):
    """"""
    listen_feedback_ = False

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        self._latency = 0
        self.build_areas()

    # ----------------------------------------------------------------------
    def connect(self, port=5000):
        """"""
        self.ws = BCIWebSocket(f'ws://localhost:{port}/ws')
        self.ws.main = self

        if self.listen_feedback_:
            print('CONSUMMING')
            timer.set_timeout(lambda: self.ws.send(
                {'action': 'consumer', }), 1000)

    # ----------------------------------------------------------------------
    @property
    def mode(self):
        """"""
        return getattr(self, '_bci_mode', None)

    # ----------------------------------------------------------------------
    @DeliveryInstance.both
    def send_marker(self, marker, blink=100, force=False):
        """"""
        marker = {
            'marker': marker,
            'latency': self._latency,
            # 'datetime': datetime.now().timestamp(),
        }

        if self.mode == 'stimuli' or force:
            self.ws.send({
                'action': 'marker',
                'marker': marker,
            })
        self._blink(blink)

        # print(f'MARKER: {marker["marker"]}')

    # ----------------------------------------------------------------------
    # @DeliveryInstance.remote
    def start_record(self):
        """"""
        self.send_annotationn('start_record')

    # ----------------------------------------------------------------------
    # @DeliveryInstance.remote
    def stop_record(self):
        """"""
        self.send_annotationn('stop_record')

    # ----------------------------------------------------------------------
    def send_annotationn(self, description, duration=0):
        """"""
        self.ws.send({
            'action': 'annotation',
            'annotation': {'duration': duration,
                           # 'onset': datetime.now().timestamp(),
                           'description': description,
                           'latency': self._latency,
                           },
        })

    # ----------------------------------------------------------------------
    def listen_feedbacks(self, handler):
        """"""
        self.feedback_listener_ = handler
        self.listen_feedback_ = True

    # ----------------------------------------------------------------------
    def _on_feedback(self, *args, **kwargs):
        """"""
        self.feedback_listener_(**kwargs)

    # ----------------------------------------------------------------------
    # @DeliveryInstance.both
    def _blink(self, time=100):
        """"""
        if blink := getattr(self, '_blink_area', False):
            blink.style = {'background-color': blink.color_on, }
            timer.set_timeout(lambda: setattr(
                blink, 'style', {'background-color': blink.color_off}), time)

    # ----------------------------------------------------------------------
    def add_stylesheet(self, file):
        """"""
        document.select_one('head') <= html.LINK(
            href=os.path.join('root', file), type='text/css', rel='stylesheet')

    # ----------------------------------------------------------------------
    @property
    def dashboard(self):
        """"""
        if not hasattr(self, 'bci_dashboard'):
            self.bci_dashboard = html.DIV(Class='bci_dashboard')
            document <= self.bci_dashboard
        return self.bci_dashboard

    # ----------------------------------------------------------------------
    @property
    def stimuli_area(self):
        """"""
        if not hasattr(self, 'bci_stimuli'):
            self.bci_stimuli = html.DIV(Class='bci_stimuli')
            document <= self.bci_stimuli
        return self.bci_stimuli

    # ----------------------------------------------------------------------
    @DeliveryInstance.both
    def set_seed(self, seed):
        """"""
        random.seed(seed)
        print(f"SEED: {seed}")

    # ----------------------------------------------------------------------
    @DeliveryInstance.local
    def propagate_seed(self):
        """"""
        seed = random.randint(0, 99999)
        self.set_seed(seed)

    # ----------------------------------------------------------------------
    def show_cross(self):
        """"""
        self.hide_cross()
        self.stimuli_area <= html.DIV(Class='bci_cross cross_contrast')
        self.stimuli_area <= html.DIV(Class='bci_cross cross')

    # ----------------------------------------------------------------------
    def hide_cross(self):
        """"""
        for element in document.select('.bci_cross'):
            element.remove()

    # ----------------------------------------------------------------------
    @DeliveryInstance.both
    def show_progressbar(self, steps=100):
        """"""
        from mdc.MDCLinearProgress import MDCLinearProgress
        if progressbar := getattr(self, 'run_progressbar', False):
            progressbar.remove()

        self.run_progressbar = MDCLinearProgress(Class='run_progressbar')
        self.run_progressbar.style = {
            'position': 'absolute',
            'bottom': '0px',
            'z-index': 999,
        }
        document <= self.run_progressbar

        self._progressbar_increment = 1 / (steps - 1)
        self.set_progress(0)
        return self.run_progressbar

    # ----------------------------------------------------------------------
    @DeliveryInstance.both
    def set_progress(self, p=0):
        """"""
        if not hasattr(self, 'run_progressbar'):
            self.show_progressbar()
        self.run_progressbar.mdc.set_progress(p)
        self._progressbar_value = p

    # ----------------------------------------------------------------------
    def increase_progress(self):
        """"""
        if hasattr(self, 'run_progressbar'):
            self._progressbar_value += self._progressbar_increment
            self.set_progress(self._progressbar_value)

    # ----------------------------------------------------------------------
    def show_synchronizer(self, color_on='#000000', color_off='#ffffff', size=150, position='lower left'):
        """"""
        self.hide_synchronizer()
        if 'upper' in position:
            top = '15px'
        elif 'lower' in position:
            top = f'calc(100% - {size}px - 15px)'

        if 'left' in position:
            left = '15px'
        elif 'right' in position:
            left = f'calc(100% - {size}px - 15px)'

        self._blink_area = html.DIV('', style={

            'width': f'{size}px',
            'height': f'{size}px',
            'background-color': color_off,
            'position': 'absolute',
            'top': top,
            'left': left,
            'border-radius': '100%',
            'border': '3px solid #00bcd4',
            'z-index': 999,
        })

        self.stimuli_area <= self._blink_area

        self._blink_area.color_on = color_on
        self._blink_area.color_off = color_off

        return self._blink_area

    # ----------------------------------------------------------------------
    def hide_synchronizer(self):
        """"""
        if element := getattr(self, '_blink_area', None):
            element.remove()

    # ----------------------------------------------------------------------
    def build_areas(self, stimuli=True, dashboard=True):
        """"""
        if stimuli:
            self.stimuli_area
        if dashboard:
            self.dashboard

    # ----------------------------------------------------------------------
    def _last_init(self):
        """"""

