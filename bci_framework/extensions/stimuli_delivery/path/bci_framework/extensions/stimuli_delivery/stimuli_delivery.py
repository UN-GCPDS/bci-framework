import os
import json
import time
import random
import logging
from browser import timer, html, document, window
from datetime import datetime
import copy
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

            # if self._bci_mode == 'dashboard':
            if getattr(self, '_bci_mode', None) == 'dashboard':
                self.ws.send({'action': 'feed',
                              'method': method.__name__,
                              'args': list(args),  # prevent ellipsis objects
                              'kwargs': dict(kwargs),
                              })
                try:  # To call as decorator and as function
                    method(self, *args, **kwargs)
                except TypeError:
                    method(*args, **kwargs)

        wrap.no_decorator = method
        return wrap

    # ----------------------------------------------------------------------
    @classmethod
    def rboth(cls, method):
        """Decorator for execute method in both environs, dashboard and delivery.

        This decorator only works from remote calls.
        """

        def wrap(self, *args, **kwargs):

            # if self._bci_mode == 'stimuli':
            if getattr(self, '_bci_mode', None) == 'stimuli':
                # First the remote call, because the local call could modify the arguments
                self.ws.send({'action': 'feed',
                              'method': method.__name__,
                              'args': list(args),  # prevent ellipsis objects
                              'kwargs': dict(kwargs),
                              })
                try:  # To call as decorator and as function
                    method(self, *args, **kwargs)
                except TypeError:
                    method(*args, **kwargs)

        wrap.no_decorator = method
        return wrap

    # ----------------------------------------------------------------------
    @classmethod
    def remote(cls, method):
        """Decorator for execute methon only in delivery environ.

        This decorator only works from dashboard calls.
        """

        def wrap(self, *args, **kwargs):

            # if self._bci_mode == 'dashboard':
            if getattr(self, '_bci_mode', None) == 'dashboard':
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
            # if self._bci_mode == 'dashboard':
            if getattr(self, '_bci_mode', None) == 'dashboard':
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


        This decorator works in both environs.
        """

        def wrap(self, *args, **kwargs):

            if hasattr(method, 'no_decorator'):
                method_ = method.no_decorator
            else:
                method_ = method

            # try:
            if self._bci_mode == 'dashboard':
                try:
                    cls.both(method_)(self, *args, **kwargs)
                except TypeError:
                    cls.both(method_)(*args, **kwargs)
            else:
                try:
                    cls.rboth(method_)(self, *args, **kwargs)
                except TypeError:
                    cls.rboth(method_)(*args, **kwargs)
            # except Exception as e:
                # logging.warning(e)
                # logging.warning('#' * 15)
                # logging.warning(f'Method: {method_}')
                # logging.warning(f'args: {args}')
                # logging.warning(f'kwargs: {kwargs}')
                # logging.warning('#' * 15)

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
        print('Connected with dashboard.')

        if on_connect := getattr(self.main, 'on_connect', False):
            on_connect()

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
        window.location.replace(self.ip_.replace(
            '/ws', '').replace('ws', 'http'))

    # ----------------------------------------------------------------------
    def on_error(self, evt):
        """"""
        window.location.replace(self.ip_.replace(
            '/ws', '').replace('ws', 'http'))


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

            if isinstance(method, str):
                explicit_pipeline.append([getattr(self, method), var])
            else:
                explicit_pipeline.append([method, var])

        return explicit_pipeline

    # ----------------------------------------------------------------------
    def run_pipeline(self, pipeline, trials, callback=None, show_progressbar=True):
        """"""
        # self._callback = callback
        if show_progressbar:
            self.show_progressbar(len(trials) * len(pipeline))
        # self.set_autoprogress(show_progressbar)

        if self.DEBUG:
            self.set_autoprogress.no_decorator(self, show_progressbar)
            self._prepare.no_decorator(self, callback)
            self._run_pipeline.no_decorator(self, pipeline, trials)
        else:
            self.set_autoprogress(show_progressbar)
            self._prepare(callback)
            self._run_pipeline(pipeline, trials)

    # ----------------------------------------------------------------------
    @DeliveryInstance.both
    def set_autoprogress(self, value):
        """"""
        self._autoprogress = value

    # ----------------------------------------------------------------------
    @DeliveryInstance.both
    def _prepare(self, callback):
        """"""
        self.iteration = 0
        if callback:
            self._callback = getattr(self, callback)
        else:
            self._callback = None

    # ----------------------------------------------------------------------
    @DeliveryInstance.remote
    def _run_pipeline(self, pipeline, trials):
        """"""
        pipeline_m, timeouts = zip(*self._build_pipeline(pipeline))
        trial = trials.pop(0)
        trial['trial_n'] = self.iteration

        timer.set_timeout(self.wrap_fn(
            pipeline_m[0], trial), 0)  # First pipeline

        self._timeouts = []
        for i in range(1, len(pipeline_m)):

            # Others pipelines
            t = timer.set_timeout(self.wrap_fn(
                pipeline_m[i], trial), sum(timeouts[:i]))
            self._timeouts.append(t)

            if t_ := timer.set_timeout(self.increase_progress, sum(timeouts[:i])):
                self._timeouts.append(t_)

        if trials:
            t = timer.set_timeout(lambda: self._run_pipeline.no_decorator(self,
                                                                          pipeline, trials), sum(timeouts))
            self._timeouts.append(t)
            if t_ := timer.set_timeout(self.increase_progress, sum(timeouts)):
                self._timeouts.append(t_)

        elif getattr(self, '_callback', None):
            t = timer.set_timeout(self.on_callback, sum(timeouts))
            self._timeouts.append(t)

        self.iteration += 1

    # ----------------------------------------------------------------------
    def wrap_fn(self, fn, trial):
        """"""
        fn_ = fn
        trial_ = trial
        arguments = fn.__code__.co_varnames[1:fn.__code__.co_argcount]

        def inner():
            if self.DEBUG:
                DeliveryInstance.both(fn_)(
                    self, *[trial_[v] for v in arguments])
            else:
                DeliveryInstance.rboth(fn_)(
                    self, *[trial_[v] for v in arguments])
        return inner

    # ----------------------------------------------------------------------
    def stop_pipeline(self):
        """"""
        if self.DEBUG:
            self._stop_pipeline()  # kill timed trials
        else:
            DeliveryInstance.remote(self._stop_pipeline)(
                self)  # kill timed trials

    # ----------------------------------------------------------------------
    def _stop_pipeline(self):
        """"""
        if hasattr(self, '_timeouts'):
            for t in self._timeouts:
                timer.clear_timeout(t)
        self.on_callback()

    # ----------------------------------------------------------------------
    def on_callback(self):
        """"""
        if self._autoprogress:
            DeliveryInstance.event(self.set_progress)(self, 0)
        if getattr(self, '_callback', None):
            DeliveryInstance.event(self._callback)(self)


########################################################################
class StimuliAPI(Pipeline):
    """"""
    listen_feedback_ = False

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        self._latency = 0
        self.build_areas()
        self.listen_feedbacks(self.latency_feedback_)

    # ----------------------------------------------------------------------
    def connect(self, ip='localhost', port=5000):
        """"""
        self.ws = BCIWebSocket(f'ws://{ip}:{port}/ws')
        self.ws.main = self

        if self.listen_feedback_:
            timer.set_timeout(lambda: self.ws.send(
                {'action': 'consumer', }), 1000)

    # ----------------------------------------------------------------------
    @property
    def mode(self):
        """"""
        return getattr(self, '_bci_mode', None)

    # ----------------------------------------------------------------------
    # @DeliveryInstance.event
    def send_marker(self, marker, blink=100, force=False):
        """"""
        marker = {
            'marker': marker,
            'latency': self._latency,
            # 'datetime': datetime.now().timestamp(),
        }

        if self.mode == 'stimuli' or force or self.DEBUG:
            self.ws.send({
                'action': 'marker',
                'marker': marker,
            })

        if blink:
            if force:
                DeliveryInstance.both(self._blink)(self, blink)
            else:
                self._blink(blink)

        # print(f'MARKER: {marker["marker"]}')

    # ----------------------------------------------------------------------
    @DeliveryInstance.event
    def start_record(self):
        """"""
        self.send_annotation('start_record')
        timer.set_timeout(self._send_custom_annotations, 15000)

    # ----------------------------------------------------------------------
    def _send_custom_annotations(self):
        """"""
        prefix = 'annotation-'
        data = w.get_prefix(prefix)
        for k in data:
            description = f'{k.replace(prefix, "").capitalize()}: {data[k]}'
            self.send_annotation(description)

    # ----------------------------------------------------------------------
    @DeliveryInstance.event
    def stop_record(self):
        """"""
        self.send_annotation('stop_record')

    # ----------------------------------------------------------------------
    def send_annotation(self, description, duration=0, force=False):
        """"""
        logging.warning(f'Annotation: {description}')
        if self.mode == 'stimuli' or force or self.DEBUG:
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
    @DeliveryInstance.both
    def show_cross(self):
        """"""
        self.hide_cross.no_decorator(self)
        self.stimuli_area <= html.DIV(Class='bci_cross cross_contrast')
        self.stimuli_area <= html.DIV(Class='bci_cross cross')

    # ----------------------------------------------------------------------
    @DeliveryInstance.both
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
        # return self.run_progressbar

    # ----------------------------------------------------------------------
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
            if self.DEBUG:
                DeliveryInstance.both(self.set_progress)(
                    self, self._progressbar_value)
            else:
                DeliveryInstance.rboth(self.set_progress)(
                    self, self._progressbar_value)

    # ----------------------------------------------------------------------
    @DeliveryInstance.both
    def show_synchronizer(self, color_on='#000000', color_off='#ffffff', size=150, position='lower left', type='round'):
        """"""
        self.hide_synchronizer.no_decorator(self)

        if type == 'round':
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
                'position': 'fixed',
                'top': top,
                'left': left,
                'border-radius': '100%',
                'border': '3px solid #00bcd4',
                'z-index': 999,
            })
        elif type == 'square':
            if 'upper' in position:
                top = '0'
            elif 'lower' in position:
                top = f'calc(100% - {size}px)'
            if 'left' in position:
                left = '0'
            elif 'right' in position:
                left = f'calc(100% - {size}px)'

            self._blink_area = html.DIV('', style={
                'width': f'{size}px',
                'height': f'{size}px',
                'background-color': color_off,
                'position': 'fixed',
                'top': top,
                'left': left,
                'z-index': 999,
            })

        self.stimuli_area <= self._blink_area
        self._blink_area.color_on = color_on
        self._blink_area.color_off = color_off

        # return self._blink_area

    # ----------------------------------------------------------------------
    @DeliveryInstance.both
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

    # ----------------------------------------------------------------------
    def start_marker_synchronization(self, blink=250, pause=1000):
        """"""
        if hasattr(self, '_timer_marker_synchronization'):
            timer.clear_interval(self._timer_marker_synchronization)
            del self._timer_marker_synchronization
            return
        self._timer_marker_synchronization = timer.set_interval(
            lambda: self.send_marker('MARKER', blink=blink, force=True), pause)

    # ----------------------------------------------------------------------
    def latency_feedback_(self, name, value):
        """"""
        if name == 'set_latency':
            self._latency = value

    # ----------------------------------------------------------------------
    @DeliveryInstance.both
    def show_counter(self, start=5):
        """"""
        if not document.select('#bci-counter-frame'):
            document.select_one('.bci_stimuli') <= html.DIV(
                html.SPAN(' ', id='bci-counter'), id='bci-counter-frame')
        else:
            document.select_one(
                '#bci-counter-frame').style = {'display': 'block'}

        def hide():
            document.select_one(
                '#bci-counter-frame').style = {'display': 'none'}

        def set_counter(n):
            def inset():
                counter = document.select_one('#bci-counter')
                counter.html = f'{n}'
            return inset

        for i in range(start):
            if i < (start - 1):
                timer.set_timeout(set_counter(start - i), 1000 * (i + 1))
            else:
                timer.set_timeout(set_counter(''), 1000 * (i + 1))
                timer.set_timeout(hide, 1000 * start)

