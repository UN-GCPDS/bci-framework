from bci_framework.extensions.stimuli_delivery import StimuliAPI, DeliveryInstance
from bci_framework.extensions.stimuli_delivery.utils import Widgets as w

from browser import timer
import logging


########################################################################
class EventMarkerSynchronization(StimuliAPI):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)

        # self.listen_feedbacks(self.on_feedback)
        self.add_stylesheet('styles.css')

        self.dashboard <= w.label(
            'Latency measurement<br><br>', typo='headline4')

        self.dashboard <= w.slider(
            label='Delay',
            min=1000,
            max=10000,
            step=100,
            value=1000,
            on_change=self.run,
            unit='ms',
            id='delay'
        )
        self.dashboard <= w.slider(
            label='Pulse duration',
            min=100,
            max=5000,
            step=100,
            value=500,
            on_change=self.run,
            unit='ms',
            id='pulse',
        )

        self.dashboard <= w.button(label='Start run', on_click=self.start)
        self.dashboard <= w.button(label='Stop run', on_click=self.stop)
        self.stimuli_area <= w.select(label='', hide_label=False,
                                      value='lower left',
                                      on_change=self.move_synchronizer,
                                      id='move_synchronizer',
                                      options=[
                                          ('lower left', 'lower left'),
                                          ('lower right', 'lower right'),
                                          ('upper left', 'upper left'),
                                          ('upper right', 'upper right'),
                                      ])
        # self.start()

    # ----------------------------------------------------------------------
    def _last_init(self):
        """"""

    # ----------------------------------------------------------------------
    def move_synchronizer(self, position):
        """"""
        DeliveryInstance.rboth(self.show_synchronizer.no_decorator)(
            self, position=position)

    # ----------------------------------------------------------------------
    def on_connect(self):
        """"""
        if self._bci_mode == 'stimuli':
            DeliveryInstance.rboth(self.show_synchronizer.no_decorator)(self)
            self.start()

    # ----------------------------------------------------------------------
    def on_feedback(self, name, value):
        """"""
        if name == 'set_latency':
            self._latency = value

    # ----------------------------------------------------------------------
    def start(self):
        """"""
        self.run()

    # ----------------------------------------------------------------------
    def stop(self):
        """"""
        timer.clear_interval(self.timer_cue)

    # ----------------------------------------------------------------------
    def trial(self, pulse):
        """"""
        self.send_marker('MARKER', blink=pulse, force=True)

    # ----------------------------------------------------------------------
    def run(self, *args, **kwargs):
        """"""
        delay = w.get_value('delay')
        pulse = w.get_value('pulse')

        if hasattr(self, 'timer_cue'):
            timer.clear_interval(self.timer_cue)
        self.timer_cue = timer.set_interval(lambda: self.trial(pulse), delay)


if __name__ == '__main__':
    EventMarkerSynchronization()

