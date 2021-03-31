from bci_framework.extensions.stimuli_delivery import StimuliServer, StimuliAPI, DeliveryInstance
from bci_framework.extensions.stimuli_delivery.utils import Widgets, Tone

from browser import document, timer, html

TASKS = {

    'resting_open': ['Resting with open eyes',
                     '<p>Resting with <b>open</b> eyes</p>',
                     '<p>Press the button and close the eyes, the acquisition begins with the single beep, <b>keep eyes closed until two beeps</b>.</p>'],
                     
    'resting_close': ['Resting with close eyes',
                      '<p>Resting with <b>close</b> eyes</p>',
                      '<p>Press the button and close the eyes, the acquisition begins with the single beep, <b>keep eyes closed until two beeps</b>.</p>'],

    'eye_blinking': ['Eye blinking',
                    '<p>Eyes <b>blinking</b></p>',
                     '<p>Press the button and close the eyes, the acquisition begins with the single beep, <b>keep eyes closed until two beeps</b>.</p>'],

    'eyeball_up_down': ['Eyeball movement up/down',
                        '<p>Eyeball movement <b>Up</b> and <b>Down</b></p>',
                        '<p>Press the button and close the eyes, the acquisition begins with the single beep, <b>keep eyes closed until two beeps</b>.</p>'],

    'eyeball_left_right': ['Eyeball movement left/right',
                           '<p>Eyeball movement <b>Left</b> and <b>Right</b></p>',
                           '<p>Press the button and close the eyes, the acquisition begins with the single beep, <b>keep eyes closed until two beeps</b>.</p>'],

    'head_left_right': ['Head movement left/right',
                        '<p>Head movement <b>Left</b> and <b>Right</b></p>',
                        '<p>Press the button and close the eyes, the acquisition begins with the single beep, <b>keep eyes closed until two beeps</b>.</p>'],

    'jaw_clenching': ['Jaw clenching',
                      '<p>Jaw <b>clenching</b></p>',
                      '<p>Press the button and close the eyes, the acquisition begins with the single beep, <b>keep eyes closed until two beeps</b>.</p>'],

}


########################################################################
class Resting(StimuliAPI):

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)


        self.add_stylesheet('styles.css')

        self.stimuli_area
        self.dashboard

        self.on_trial = False

        self.widgets = Widgets()
        self.tone = Tone()

        self.build_dashboard()

        self.add_cross()
        self.run_progressbar = self.add_run_progressbar()

        self.add_blink_area()

        # self.show_hint('eye')

    # ----------------------------------------------------------------------
    def build_dashboard(self):
        """"""
        self.dashboard <= self.widgets.label('Resting state and noise acquisition', 'headline4', style={'margin-bottom': '15px', 'display': 'flex', })

        for task_id in TASKS:
            title = TASKS[task_id][0]
            self.dashboard <= self.widgets.switch(title, True, id=f'{task_id}_switch')
            self.dashboard <= self.widgets.slider('Duration', min=0.1, max=5, step=0.1, value=1, unit='minutes', id=task_id)
            self.dashboard <= html.BR()

        self.dashboard <= self.widgets.switch('Record EEG', checked=False, on_change=None, id='record')
        self.dashboard <= self.widgets.button('Start run', on_click=self.start, style={'margin': '0 15px'})
        self.dashboard <= self.widgets.button('Stop run', on_click=self.stop, style={'margin': '0 15px'})
        
        self.button_start = self.widgets.button('Start (space)', unelevated=False, outlined=True, id='user-button', on_click=self.execute)
        self.stimuli_area <= self.button_start        
        
        
    # ----------------------------------------------------------------------
    def start(self):
        """"""
        self.tasks = []
        for task_id in TASKS:
            if self.widgets.get_value(f'{task_id}_switch'):
                self.tasks.append(task_id)

        if self.widgets.get_value('record'):
            self.start_record()
        timer.set_timeout(self.show_instructions, 2000)
        
    # ----------------------------------------------------------------------
    def stop(self):
        """"""
        self.clear_hint()
        self.button_start.style = {'display': 'none',}
        [timer.clear_timeout(getattr(self, f't{i}')) for i in range(1, 6)]
        if self.widgets.get_value('record'):
            timer.set_timeout(self.stop_record, 2000)

    # ----------------------------------------------------------------------
    def show_instructions(self):
        """"""
        if len(self.tasks):
            self.button_start.style = {'display': 'block',}
            self.task = self.tasks.pop(0)
            self.show_hint(self.task)
        else:
            self.stop()

    # ----------------------------------------------------------------------
    def execute(self):
        """"""
        duration = self.widgets.get_value(self.task) * 60 * 1000
        self.button_start.style = {'display': 'none',}

        # start
        timer.set_timeout(lambda: self.tone("C#6", 200), 2000)
        timer.set_timeout(lambda: self.send_marker(f'{self.task.upper()}-START', 100), 2000)

        # execution
        self.t1 = timer.set_timeout(lambda: self.tone("C#6", 100), duration + 2000)
        self.t2 = timer.set_timeout(lambda: self.tone("C#6", 100), duration + 2000 + 150)
        self.t3 = timer.set_timeout(self.clear_hint, duration + 2000 + 150)
        self.t4 = timer.set_timeout(lambda: self.send_marker(f'{self.task.upper()}-END', 100), duration + 2000)

        # next
        self.t5 = timer.set_timeout(self.show_instructions, duration + 2250 + 2000)

    # ----------------------------------------------------------------------
    def show_hint(self, task):
        """"""
        label = TASKS[task][1]
        message = TASKS[task][2]

        self.hint = self.widgets.label(label, 'headline2', id='hint')
        self.stimuli_area <= self.hint
        self.hint2 = self.widgets.label(message, 'headline2', id='hint2')
        self.stimuli_area <= self.hint2
        
    # ----------------------------------------------------------------------
    def clear_hint(self):
        """"""
        self.hint.html = ''
        self.hint2.html = ''

if __name__ == '__main__':
    StimuliServer('Resting')


