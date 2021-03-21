from bci_framework.extensions.stimuli_delivery import StimuliServer, StimuliAPI, DeliveryInstance
from bci_framework.extensions.stimuli_delivery.utils import Widgets

from browser import timer
import logging


########################################################################
class StimuliDelivery(StimuliAPI):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)

        self.listen_feedbacks(self.on_feedback)

        self.build_areas()

        self.add_stylesheet('styles.css')

        self.add_cross()
        self.add_blink_area()

        self.widgets = Widgets()

        self.dashboard <= self.widgets.label(
            'Latency measurement<br><br>', typo='headline4')

        self.dashboard <= self.widgets.slider(
            'Delay', min=1000, max=10000, step=100, value=1000, on_change=self.run, unit='ms', id='delay')
        self.dashboard <= self.widgets.slider(
            'Pulse duration', min=100, max=5000, step=100, value=500, on_change=self.run, unit='ms', id='pulse')
        self.dashboard <= self.widgets.switch(
            'Record EEG', checked=False, on_change=None, id='record')
        self.dashboard <= self.widgets.button(
            'Start run', on_click=self.start, style={'margin': '0 15px'})
        self.dashboard <= self.widgets.button(
            'Stop run', on_click=self.stop, style={'margin': '0 15px'})

        self.start()

    # ----------------------------------------------------------------------
    def _last_init(self):
        """"""
        self._bci_mode = 'dashboard'

    # ----------------------------------------------------------------------
    def on_feedback(self, name, value):
        """"""
        if name == 'set_latency':
            self._latency = value

    # ----------------------------------------------------------------------
    def start(self):
        """"""
        if self.widgets.get_value('record'):
            self.start_record()
        timer.set_timeout(self.run, 2000)

    # ----------------------------------------------------------------------
    def stop(self):
        """"""
        timer.clear_interval(self.timer_cue)
        if self.widgets.get_value('record'):
            timer.set_timeout(self.stop_record, 2000)

    # ----------------------------------------------------------------------
    def trial(self, pulse):
        """"""
        self.send_marker('MARKER', blink=pulse, force=True)

    # ----------------------------------------------------------------------
    def run(self, *args, **kwargs):
        """"""
        delay = self.widgets.get_value('delay')
        pulse = self.widgets.get_value('pulse')

        if hasattr(self, 'timer_cue'):
            timer.clear_interval(self.timer_cue)
        self.timer_cue = timer.set_interval(lambda: self.trial(pulse), delay)


if __name__ == '__main__':
    StimuliServer('StimuliDelivery')

