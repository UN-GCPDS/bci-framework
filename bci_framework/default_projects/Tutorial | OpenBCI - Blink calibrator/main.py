from bci_framework.extensions.stimuli_delivery import StimuliServer, StimuliAPI, DeliveryInstance
# from bci_framework.extensions.stimuli_delivery.utils import Widgets, Tone


from browser import document, timer, html

from mdc.MDCComponent import MDCComponent
from mdc.MDCButton import MDCButton    
from mdc.MDCFormField import MDCForm
# from datetime import datetime


########################################################################
class DigitalInput(StimuliAPI):

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        """"""
        self.add_stylesheet('styles.css')

        # Properties constructors
        self.stimuli_area
        self.dashboard

        self.build_dashboard()

        # The interval will start automatically
        self.duty_cycle_value = 1000  # Global variable
        self.interval = timer.set_timeout(
            self.toggle, self.duty_cycle_value * 2)

    # ----------------------------------------------------------------------
    def build_dashboard(self):
        """"""
        form = MDCForm()

        # Labels
        label = MDCComponent(html.SPAN('Duty Cycle: '))
        label.mdc.typography('subtitle1')
        form <= label
        sublabel = MDCComponent(
            html.SPAN('1000 ms', id='duty_cycle')).mdc.typography('caption')
        form <= sublabel

        # Slider
        self.duty_cycle = form.mdc.Slider(
            'Slider', min=0, max=3000, step=1, valuenow=1000, continuous=True)
        self.dashboard <= form

        # Events
        self.duty_cycle.mdc.listen(
            'MDCSlider:change', self.change_duty_cycle)  # single shot update
        self.duty_cycle.mdc.listen(
            'MDCSlider:input', self.input_duty_cycle)  # continuos update

        b = MDCButton('Marker')
        b.bind('click', self.marker)
        self.dashboard <= b

    # @stimulus
    def marker(self, event=None):
        """"""
        self.send_marker('MANUAL')

    # ----------------------------------------------------------------------
    def change_duty_cycle(self, evt=None):
        """"""
        duty_cycle_value = int(self.duty_cycle.mdc.getValue())
        self.set_duty_cycle(duty_cycle_value)

    # ----------------------------------------------------------------------
    def input_duty_cycle(self, evt=None):
        """"""
        duty_cycle_value = int(self.duty_cycle.mdc.getValue())
        document.select_one('#duty_cycle').text = f'{duty_cycle_value} ms'

    # ----------------------------------------------------------------------
    def set_level(self, level):
        """"""
        self.send_marker({'#ffffff': 'HIGH-PRE',
                          '#000000': 'LOW-PRE', }[level])

        self.stimuli_area.style = {'background-color': level, }

        self.send_marker({'#ffffff': 'HIGH-POST',
                          '#000000': 'LOW-POST', }[level])

    # ----------------------------------------------------------------------
    # @delivery
    def toggle(self):
        """"""
        self.set_level('#ffffff')
        timer.set_timeout(lambda: self.set_level(
            '#000000'), self.duty_cycle_value)
        self.interval = timer.set_timeout(
            self.toggle, self.duty_cycle_value * 2)

   # ----------------------------------------------------------------------
    @DeliveryInstance.both
    def set_duty_cycle(self, value):
        """"""
        # Propagate global variable to all clients
        self.duty_cycle_value = value


if __name__ == '__main__':
    StimuliServer('DigitalInput')


