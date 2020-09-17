from bci_framework.projects.server import StimuliServer, StimuliAPI, stimulus
from bci_framework.projects import properties as prop
from browser import document, timer, html
from mdc import MDCButton, MDCCheckbox, MDCFormField, MDCForm, MDCComponent, MDCLinearProgress

import random
random.seed(8511)

########################################################################
class Arrows(StimuliAPI):

    # ----------------------------------------------------------------------
    def __init__(self):
        """"""
        document.select('head')[0] <= html.LINK(
            href='/root/styles.css', type='text/css', rel='stylesheet')

        self.stimuli_area
        self.dashboard

        self.hint = html.SPAN('', id='hint')
        self.stimuli_area.clear()
        self.stimuli_area <= self.hint

        # self.caption = html.SPAN('1/78', Class='caption')
        # self.stimuli_area <= self.caption

        self.progressbar = MDCLinearProgress()
        self.progressbar.style = {'position': 'relative', 'bottom': '4px', }
        self.stimuli_area <= self.progressbar

        self.stimuli_area <= html.DIV(Class='cross')

        self.build_dashboard()

    # ----------------------------------------------------------------------
    def build_dashboard(self):
        """"""
        # Stimuli set
        label = MDCComponent(html.SPAN('Stimuli set'))
        label.mdc.typography('subtitle1')
        # self.dashboard <= label
        self.checkboxes = []
        form = MDCForm(formfield_style={'width': '100px'})
        form <= label

        self.checkboxes.append(form.mdc.Checkbox(
            'Right', value='&#x1f83a;', checked=True))
        self.checkboxes.append(form.mdc.Checkbox(
            'Left', value='&#x1f838;', checked=True))
        self.checkboxes.append(form.mdc.Checkbox(
            'Up', value='&#x1f839;', checked=False))
        self.checkboxes.append(form.mdc.Checkbox(
            'Down', value='&#x1f83b;', checked=False))
        self.dashboard <= form

        # Repetitions
        label = MDCComponent(html.SPAN('Repetitions'))
        label.mdc.typography('subtitle1')
        # self.dashboard <= label
        form = MDCForm(formfield_style={'width': '100px'})
        form <= label

        self.repetitions = form.mdc.TextField('', value=40, type='number')
        self.dashboard <= form

        # Stimulus duration
        form = MDCForm()
        label = MDCComponent(html.SPAN('Stimulus duration: '))
        label.mdc.typography('subtitle1')
        form <= label
        form <= MDCComponent(
            html.SPAN('4000 ms', id='stimulus_duration')).mdc.typography('caption')
        # form <=
        self.stimulus_duration = form.mdc.Slider(
            'Slider', min=0, max=6000, step=100, valuenow=4000, continuous=True)
        self.dashboard <= form
        self.stimulus_duration.mdc.listen(
            'MDCSlider:input', self.update_times_from_sliders)

        # Stimulus rest
        form = MDCForm()
        label = MDCComponent(html.SPAN('Stimulus rest: '))
        label.mdc.typography('subtitle1')
        form <= label
        form <= MDCComponent(
            html.SPAN('1000 ms', id='stimulus_rest')).mdc.typography('caption')
        self.stimulus_rest = form.mdc.Slider(
            'Slider', min=0, max=6000, step=100, valuenow=1200, continuous=True)
        self.dashboard <= form
        self.stimulus_rest.mdc.listen(
            'MDCSlider:input', self.update_times_from_sliders)

        # Aditional stimulus aleatory rest
        form = MDCForm()
        label = MDCComponent(html.SPAN('Aditional stimulus aleatory rest: '))
        label.mdc.typography('subtitle1')
        form <= label
        form <= MDCComponent(
            html.SPAN('800 ms', id='stimulus_random_rest')).mdc.typography('caption')
        self.stimulus_random_rest = form.mdc.Slider(
            'Slider', min=0, max=1000, step=100, valuenow=800, continuous=True)
        self.dashboard <= form
        self.stimulus_random_rest.mdc.listen(
            'MDCSlider:input', self.update_times_from_sliders)

         # Theme
        form = MDCForm(formfield_style={'width': '100%', 'height': '40px'})
        self.theme = form.mdc.Switch('Dark Theme')
        self.theme.bind('change', lambda evt: self.change_theme(
            self.theme.mdc.checked))
        self.dashboard <= form

        # Start - Stop
        self.button_start = MDCButton(
            'Start', raised=True, style={'margin': '0 15px'})
        self.button_stop = MDCButton(
            'Stop', raised=True, style={'margin': '0 15px'})
        self.button_start.bind('click', self.start)
        self.button_stop.bind('click', self.stop)
        self.dashboard <= self.button_start
        self.dashboard <= self.button_stop

        # progressbar.mdc.set_progress(0.5, buffer=0.6)  #50%

    # ----------------------------------------------------------------------
    def update_times_from_sliders(self, evt=None):
        """"""
        document.select_one(
            '#stimulus_duration').text = f'{self.stimulus_duration.attrs["aria-valuenow"]} ms'
        document.select_one(
            '#stimulus_rest').text = f'{self.stimulus_rest.attrs["aria-valuenow"]} ms'
        document.select_one(
            '#stimulus_random_rest').text = f'0 - {self.stimulus_random_rest.attrs["aria-valuenow"]} ms'

    # ----------------------------------------------------------------------
    def start(self, evt=None):
        """"""
        # Start timer
        self.prepare()
        self.interval = timer.set_timeout(self.random_stimulus, 100)

    # ----------------------------------------------------------------------
    def stop(self, evt=None):
        """"""
        # Kill all timers
        if hasattr(self, 'interval'):
            timer.clear_timeout(self.interval)

    # ----------------------------------------------------------------------
    def random_stimulus(self):
        """"""
        stimuli_list = [
            chb.mdc.value for chb in self.checkboxes if chb.mdc.checked]

        # calculate the aleatory rest time
        aleatory_pause = int(self.stimulus_rest.attrs["aria-valuenow"])
        aleatory_pause += random.randint(
            0, int(self.stimulus_random_rest.attrs["aria-valuenow"]))

        self.show_stimulus(random.choice(stimuli_list), aleatory_pause)

    # ----------------------------------------------------------------------
    @stimulus
    def prepare(self):
        """"""
        self.total_repetition = int(self.repetitions.mdc.value)
        self.actual_repetition = 0

    # ----------------------------------------------------------------------
    @stimulus
    def show_stimulus(self, direction, aleatory_pause):
        """"""
        self.actual_repetition += 1
        self.hint.html = direction  # update stimulus in window
        self.interval = timer.set_timeout(lambda: self.hide_stimulus(
            aleatory_pause), int(self.stimulus_duration.attrs["aria-valuenow"]))  # rest
        self.progressbar.mdc.set_progress(
            self.actual_repetition / self.total_repetition)
        print(f"Progress: {self.actual_repetition / self.total_repetition}")

    # ----------------------------------------------------------------------
    @stimulus
    def hide_stimulus(self, aleatory_pause):
        """"""
        self.hint.html = ''  # clear the stimulusClosed WS
        # show new stimuli after a delay
        self.interval = timer.set_timeout(
            self.random_stimulus, aleatory_pause)
        print(f"Aleatory pause: {aleatory_pause}")

    # ----------------------------------------------------------------------
    @stimulus
    def change_theme(self, dark):
        """"""
        if dark:
            self.stimuli_area.style = {'background-color': '#000a12', }
        else:
            self.stimuli_area.style = {'background-color': '#f5f5f5', }


if __name__ == '__main__':
    StimuliServer('Arrows')


