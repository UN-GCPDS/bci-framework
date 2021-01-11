
from radiant.utils import WebSocket

from mdc.MDCLinearProgress import MDCLinearProgress

import json
import os
from browser import timer, html, document
from datetime import datetime
from functools import wraps

import random

StimuliServer = None


########################################################################
class DeliveryInstance_:
    """"""

    # ----------------------------------------------------------------------
    @classmethod
    def both(cls, method):
        """Decorator for execute method in both environs, dashboard and delivery."""

        def wrap(self, *args, **kwargs):

            if self._bci_mode == 'dashboard':
                # print('Calling', method.__name__, args, kwargs)
                method(self, *args, **kwargs)

                self.ws.send({'action': 'feed',
                              'method': method.__name__,
                              'args': list(args),  # prevent ellipsis objects
                              'kwargs': dict(kwargs),
                              })
                # print('Called!!')

        wrap.no_decorator = method
        return wrap

    # ----------------------------------------------------------------------
    @classmethod
    def remote(cls, method):
        """Decorator for execute methon only in delivery environ."""

        def wrap(self, *args, **kwargs):

            if self._bci_mode == 'dashboard':
                # print('Calling', method.__name__, args, kwargs)
                # method(self, *args, **kwargs)  # no local
                self.ws.send({'action': 'feed',
                              'method': method.__name__,
                              'args': list(args),  # prevent ellipsis objects
                              'kwargs': dict(kwargs),
                              })
                # print('Called!!')

        wrap.no_decorator = method
        return wrap

    # ----------------------------------------------------------------------
    @classmethod
    def local(cls, method):
        """"""

        def wrap(self, *args, **kwargs):

            if self._bci_mode == 'dashboard':
                method(self, *args, **kwargs)

        wrap.no_decorator = method
        return wrap
    # # ----------------------------------------------------------------------
    # @classmethod
    # def propagate(cls, argument):
        # def inner_function(method):
            # @wraps(method)
            # def wrap(self, *args, **kwargs):

                # if self._bci_mode in ['development', 'dashboard']:
                    # print('Calling', method.__name__, args, kwargs)
                    # method(self, *args, **kwargs)

                    # print(argument, getattr(self, argument))

                    # self.ws.send({'action': 'feed',
                                  # 'method': method.__name__,
                                  # 'args': list(args),  # prevent ellipsis objects
                                  # 'kwargs': dict(kwargs),
                                  # })
                    # print('Called!!')

            # wrap.no_decorator = method
            # return wrap
        # return inner_function


DeliveryInstance = DeliveryInstance_()


########################################################################
class BCIWebSocket(WebSocket):
    """"""

    # ----------------------------------------------------------------------
    def on_open(self, evt):
        """"""
        print('Opened')
        self.send({'action': 'register'})

    # ----------------------------------------------------------------------
    def on_message(self, evt):
        """"""
        data = json.loads(evt.data)
        print("MESSAGE", data, self.main)
        if 'method' in data:
            getattr(self.main, data['method']).no_decorator(
                self.main, *data['args'], **data['kwargs'])

    # ----------------------------------------------------------------------
    def on_close(self, evt):
        """"""
        getattr(self.main, 'stop', lambda: None)()
        print('Closed WS')
        timer.set_timeout(lambda: self.__init__(
            f'ws://localhost:{self.ip_}/ws'), 1000)

    # # ----------------------------------------------------------------------
    # def on_error(self, evt):
        # """"""
        # self.main.stop()
        # print('Error WS')
        # self.__init__(self.ip)


########################################################################
class StimuliAPI:
    """"""

    # ----------------------------------------------------------------------
    def connect(self, ip=5000):
        """"""
        self.ws = BCIWebSocket(f'ws://localhost:{ip}/ws')
        self.ws.main = self

    # ----------------------------------------------------------------------
    @property
    def mode(self):
        """"""
        return getattr(self, '_bci_mode', None)

    # # ----------------------------------------------------------------------
    # @abstractmethod
    # def start(self):
        # """"""

    # # ----------------------------------------------------------------------
    # @abstractmethod
    # def stop(self):
        # """"""

    # ----------------------------------------------------------------------
    @DeliveryInstance.both
    def send_marker(self, marker, blink=100):
        """"""
        marker = {
            'marker': marker,
            # 'datetime': datetime.now().timestamp(),
        }

        if self.mode == 'stimuli':
            self.ws.send({
                'action': 'marker',
                'marker': marker,
            })
        self._blink(blink)

    # ----------------------------------------------------------------------
    @DeliveryInstance.remote
    def start_record(self):
        """"""
        self.annotation_('start_record')

    # ----------------------------------------------------------------------
    @DeliveryInstance.remote
    def stop_record(self):
        """"""
        self.annotation_('stop_record')

    # ----------------------------------------------------------------------
    def annotation_(self, description):
        """"""
        self.ws.send({
            'action': 'annotation',
            'annotation': {'onset': datetime.now().timestamp(),
                           'duration': 0,
                           'description': description},
        })

    # ----------------------------------------------------------------------
    # @DeliveryInstance.both
    def _blink(self, time=100):
        """"""
        if blink := getattr(self, '_blink_area', False):
            blink.style = {'background-color': blink.color_on, }
            timer.set_timeout(lambda: setattr(blink, 'style', {'background-color': blink.color_off}), time)

    # ----------------------------------------------------------------------
    def add_stylesheet(self, file):
        """"""
        document.select('head')[0] <= html.LINK(
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
    def add_cross(self):
        """"""
        self.stimuli_area <= html.DIV(Class='cross_contrast')
        self.stimuli_area <= html.DIV(Class='cross')

    # ----------------------------------------------------------------------
    def add_run_progressbar(self):
        """"""
        self.run_progressbar = MDCLinearProgress(Class='run_progressbar')
        self.run_progressbar.style = {'position': 'absolute', 'bottom': '4px', }
        document <= self.run_progressbar
        return self.run_progressbar

    # ----------------------------------------------------------------------
    @DeliveryInstance.both
    def set_progress(self, p=0):
        """"""
        if not hasattr(self, 'run_progressbar'):
            self.add_run_progressbar()
        self.run_progressbar.mdc.set_progress(p)

    # ----------------------------------------------------------------------
    def add_blink_area(self, color_on='#000000', color_off='#ffffff', size=150, position='lower left'):
        """"""
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
    def build_areas(self, stimuli=True, dashboard=True):
        """"""
        if stimuli:
            self.stimuli_area
        if dashboard:
            self.dashboard

