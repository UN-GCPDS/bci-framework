from bci_framework.extensions.stimuli_delivery import StimuliServer, StimuliAPI
from bci_framework.extensions.stimuli_delivery.utils import Widgets

from browser import document, timer, html, window


########################################################################
class TutorialWidgets(StimuliAPI):

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)

        self.build_areas()
        self.add_cross()

        flex = {'margin-bottom': '15px', 'display': 'flex', }
        flex_title = {'margin-top': '50px', 'margin-bottom': '10px', 'display': 'flex', }

        self.widgets = Widgets()

        self.dashboard <= self.widgets.label('MDC components', typo='headline3', style=flex_title)

        # Buttons
        self.dashboard <= self.widgets.label('Buttons', typo='headline4', style=flex_title)
        self.dashboard <= self.widgets.button('Button 1', style=flex, on_click=lambda: setattr(document.select_one('#for_button'), 'html', 'Button 1 pressed!'))
        self.dashboard <= self.widgets.button('Button 2', style=flex, on_click=self.on_button2)
        self.dashboard <= self.widgets.label(f'', id='for_button', typo=f'body1', style=flex)

        # Switch
        self.dashboard <= self.widgets.label('Switch', typo='headline4', style=flex_title)
        self.dashboard <= self.widgets.switch('Switch 1', checked=True, on_change=self.on_switch, id='my_swicth')
        self.dashboard <= self.widgets.label(f'', id='for_switch', typo=f'body1', style=flex)

        # Checkbox
        self.dashboard <= self.widgets.label('Checkbox', typo='headline4', style=flex_title)
        self.dashboard <= self.widgets.checkbox('Checkbox', [[f'chb-{i}', False] for i in range(4)], on_change=self.on_checkbox, id='my_checkbox')
        self.dashboard <= self.widgets.label(f'', id='for_checkbox', typo=f'body1', style=flex)

        # Radios
        self.dashboard <= self.widgets.label('Radios', typo='headline4', style=flex_title)
        self.dashboard <= self.widgets.radios('Radios', [[f'chb-{i}', f'chb-{i}'] for i in range(4)], on_change=self.on_radios, id='my_radios')
        self.dashboard <= self.widgets.label(f'', id='for_radios', typo=f'body1', style=flex)

        # Select
        self.dashboard <= self.widgets.label('Select', typo='headline4', style=flex)
        self.dashboard <= self.widgets.select('Select', [[f'sel-{i}', f'sel-{i}'] for i in range(4)], on_change=self.on_select, id='my_select')
        self.dashboard <= self.widgets.label(f'', id='for_select', typo=f'body1', style=flex)

        # Slider
        self.dashboard <= self.widgets.label('Slider', typo='headline4', style=flex)
        self.dashboard <= self.widgets.slider('Slider', min=1, max=10, step=0.1, value=5, on_change=self.on_slider, id='my_slider')
        self.dashboard <= self.widgets.label(f'', id='for_slider', typo=f'body1', style=flex)

        # Slider range
        self.dashboard <= self.widgets.label('Slider range', typo='headline4', style=flex)
        self.dashboard <= self.widgets.range_slider('Slider range', min=0, max=20, value_lower=5, value_upper=15, step=1, on_change=self.on_slider_range, id='my_range')
        self.dashboard <= self.widgets.label(f'', id='for_range', typo=f'body1', style=flex)

        # Typography
        for i in range(1, 7):
            self.dashboard <= self.widgets.label(f'headline{i}', typo=f'headline{i}', style=flex)
        for i in range(1, 3):
            self.dashboard <= self.widgets.label(f'body{i}', typo=f'body{i}', style=flex)
        for i in range(1, 3):
            self.dashboard <= self.widgets.label(f'subtitle{i}', typo=f'subtitle{i}', style=flex)
        for typo in ['caption', 'button', 'overline']:
            self.dashboard <= self.widgets.label(typo, typo=typo, style=flex)

    # ----------------------------------------------------------------------
    def on_button2(self):
        document.select_one('#for_button').html = 'Button 2 pressed!'

    # ----------------------------------------------------------------------
    def on_switch(self, value):
        # value = self.widgets.get_value('my_swicth')
        document.select_one('#for_switch').html = f'Switch Changed: {value}'

    # ----------------------------------------------------------------------
    def on_checkbox(self):
        value = self.widgets.get_value('my_checkbox')
        document.select_one('#for_checkbox').html = f'Checkbox Changed: {value}'

    # ----------------------------------------------------------------------
    def on_radios(self):
        value = self.widgets.get_value('my_radios')
        document.select_one('#for_radios').html = f'Radios Changed: {value}'

    # ----------------------------------------------------------------------
    def on_select(self, value):
        # value = self.widgets.get_value('my_select')
        document.select_one('#for_select').html = f'Select Changed: {value}'

    # ----------------------------------------------------------------------
    def on_slider(self, value):
        # value = self.widgets.get_value('my_slider')
        document.select_one('#for_slider').html = f'Slider Changed: {value}'

    # ----------------------------------------------------------------------
    def on_slider_range(self, value):
        # value = self.widgets.get_value('my_slider')
        document.select_one('#for_range').html = f'Range Changed: {value}'


if __name__ == '__main__':
    StimuliServer('TutorialWidgets')


