from bci_framework.extensions.stimuli_delivery import StimuliServer, StimuliAPI
from bci_framework.extensions.stimuli_delivery.utils import Widgets as w

from browser import document, timer, html, window


########################################################################
class TutorialWidgets(StimuliAPI):

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)

        self.show_cross()

        flex = {'margin-bottom': '15px', 'display': 'flex', }
        flex_title = {'margin-top': '50px',
                      'margin-bottom': '10px', 'display': 'flex', }

        self.dashboard <= w.label(
            'MDC components', typo='headline3', style=flex_title)

        # Buttons
        self.dashboard <= w.label('Buttons', typo='headline4', style=flex_title)
        self.dashboard <= w.button('Button 1', style=flex, on_click=lambda: setattr(
            document.select_one('#for_button'), 'html', 'Button 1 pressed!'))
        self.dashboard <= w.button(
            'Button 2', style=flex, on_click=self.on_button2)
        self.dashboard <= w.label(f'', id='for_button', typo=f'body1', style=flex)
            
        # Toggleable buttons
        self.dashboard <= w.label('Toggleable buttons', typo='headline4', style=flex_title)
        self.dashboard <= w.toggle_button([('Start run', self.on_toggle_button1),
                                         ('Stop run', self.on_toggle_button2)],
                                         id='toggle_buttons', style=flex
                                         )
        self.dashboard <= w.label(f'', id='for_toggle_button', typo=f'body1', style=flex)
        

        # Switch
        self.dashboard <= w.label('Switch', typo='headline4', style=flex_title)
        self.dashboard <= w.switch(
            'Switch 1', checked=True, on_change=self.on_switch, id='my_swicth')
        self.dashboard <= w.label(
            f'', id='for_switch', typo=f'body1', style=flex)

        # Checkbox
        self.dashboard <= w.label(
            'Checkbox', typo='headline4', style=flex_title)
        self.dashboard <= w.checkbox('Checkbox', [
                                     [f'chb-{i}', False] for i in range(4)], on_change=self.on_checkbox, id='my_checkbox')
        self.dashboard <= w.label(
            f'', id='for_checkbox', typo=f'body1', style=flex)

        # Radios
        self.dashboard <= w.label('Radios', typo='headline4', style=flex_title)
        self.dashboard <= w.radios('Radios', [
                                   [f'chb-{i}', f'chb-{i}'] for i in range(4)], on_change=self.on_radios, id='my_radios')
        self.dashboard <= w.label(
            f'', id='for_radios', typo=f'body1', style=flex)

        # Select
        self.dashboard <= w.label('Select', typo='headline4', style=flex)
        self.dashboard <= w.select('Select', [
                                   [f'sel-{i}', f'sel-{i}'] for i in range(4)], on_change=self.on_select, id='my_select')
        self.dashboard <= w.label(
            f'', id='for_select', typo=f'body1', style=flex)

        # Slider
        self.dashboard <= w.label('Slider', typo='headline4', style=flex)
        self.dashboard <= w.slider(
            'Slider', min=1, max=10, step=0.1, value=5, on_change=self.on_slider, id='my_slider')
        self.dashboard <= w.label(
            f'', id='for_slider', typo=f'body1', style=flex)

        # Slider range
        self.dashboard <= w.label('Slider range', typo='headline4', style=flex)
        self.dashboard <= w.range_slider('Slider range', min=0, max=20, value_lower=5,
                                         value_upper=15, step=1, on_change=self.on_slider_range, id='my_range')
        self.dashboard <= w.label(
            f'', id='for_range', typo=f'body1', style=flex)

        # Typography
        for i in range(1, 7):
            self.dashboard <= w.label(
                f'headline{i}', typo=f'headline{i}', style=flex)
        for i in range(1, 3):
            self.dashboard <= w.label(f'body{i}', typo=f'body{i}', style=flex)
        for i in range(1, 3):
            self.dashboard <= w.label(
                f'subtitle{i}', typo=f'subtitle{i}', style=flex)
        for typo in ['caption', 'button', 'overline']:
            self.dashboard <= w.label(typo, typo=typo, style=flex)

    # ----------------------------------------------------------------------
    def on_button2(self):
        document.select_one('#for_button').html = 'Button 2 pressed!'
        
    # ----------------------------------------------------------------------
    def on_toggle_button1(self):
        document.select_one('#for_toggle_button').html = 'Toggle button 1 pressed!'
        
    # ----------------------------------------------------------------------
    def on_toggle_button2(self):
        document.select_one('#for_toggle_button').html = 'Toggle button 2 pressed!'

    # ----------------------------------------------------------------------
    def on_switch(self, value):
        # value = w.get_value('my_swicth')
        document.select_one('#for_switch').html = f'Switch Changed: {value}'

    # ----------------------------------------------------------------------
    def on_checkbox(self):
        value = w.get_value('my_checkbox')
        document.select_one('#for_checkbox').html = f'Checkbox Changed: {value}'

    # ----------------------------------------------------------------------
    def on_radios(self):
        value = w.get_value('my_radios')
        document.select_one('#for_radios').html = f'Radios Changed: {value}'

    # ----------------------------------------------------------------------
    def on_select(self, value):
        # value = w.get_value('my_select')
        document.select_one('#for_select').html = f'Select Changed: {value}'

    # ----------------------------------------------------------------------
    def on_slider(self, value):
        # value = w.get_value('my_slider')
        document.select_one('#for_slider').html = f'Slider Changed: {value}'

    # ----------------------------------------------------------------------
    def on_slider_range(self, value):
        # value = w.get_value('my_slider')
        document.select_one('#for_range').html = f'Range Changed: {value}'


if __name__ == '__main__':
    StimuliServer('TutorialWidgets')


