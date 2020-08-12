from bci_framework.projects.server import StimuliServer, StimuliAPI, stimulus
from browser import document, timer, html
from mdc import MDCForm, MDCComponent


########################################################################
class DigitalInput(StimuliAPI):

    # ----------------------------------------------------------------------
    def __init__(self):
        """"""
        self.add_stylesheet('styles.css')

        # Properties constructors
        self.stimuli_area
        self.dashboard
        
        self.build_dashboard()
        
        # The interval will start automatically
        self.duty_cycle_value = 500  # Global variable
        self.interval = timer.set_timeout(self.toggle, self.duty_cycle_value*2)

    # ----------------------------------------------------------------------
    def build_dashboard(self):
        """"""
        form = MDCForm()
        
        # Labels
        label = MDCComponent(html.SPAN('Duty Cycle: '))
        label.mdc.typography('subtitle1')
        form <= label
        sublabel = MDCComponent(html.SPAN('500 ms', id='duty_cycle')).mdc.typography('caption')
        form <= sublabel
        
        # Slider
        self.duty_cycle = form.mdc.Slider('Slider', min=0, max=3000, step=1, valuenow=500, continuous=True)
        self.dashboard <= form
        
        # Events
        self.duty_cycle.mdc.listen('MDCSlider:change', self.change_duty_cycle) # single shot update
        self.duty_cycle.mdc.listen('MDCSlider:input', self.input_duty_cycle)  # continuos update

    # ----------------------------------------------------------------------
    def change_duty_cycle(self, evt=None):
        """"""
        duty_cycle_value = int(self.duty_cycle.attrs["aria-valuenow"])
        self.set_duty_cycle(duty_cycle_value)
       
    # ----------------------------------------------------------------------
    def input_duty_cycle(self, evt=None):
        """"""
        duty_cycle_value = int(self.duty_cycle.attrs["aria-valuenow"])
        document.select_one( '#duty_cycle').text = f'{duty_cycle_value} ms'
       
    # ----------------------------------------------------------------------
    def set_level(self, level):
        """"""
        self.stimuli_area.style = {'background-color': level, }
            
    # ----------------------------------------------------------------------
    def toggle(self):
        """"""
        self.set_level('#ffffff')
        timer.set_timeout(lambda :self.set_level('#000000'), self.duty_cycle_value)
        self.interval = timer.set_timeout(self.toggle, self.duty_cycle_value*2)

   # ----------------------------------------------------------------------        
    @stimulus
    def set_duty_cycle(self, value):
        """"""
        # Propagate global variable to all clients
        self.duty_cycle_value = value


if __name__ == '__main__':
    StimuliServer('DigitalInput')


