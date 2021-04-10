"""
========
P300 GUI
========
"""

from bci_framework.extensions.stimuli_delivery import StimuliAPI
from bci_framework.extensions.stimuli_delivery.utils import Widgets as w

from browser import document, html, timer
import json
import logging
import time
import random

BACK_ARROW = '&#x1f860;'
ADD = '+'
SUB = '-'


########################################################################
class P300GUI(StimuliAPI):
    """"""
    item = False
    stimuli = True

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)

        self.add_stylesheet('styles.css')
        self.build_areas()
        # w. = Widgets()

        self.interface = json.loads(
            open(f'/root/interface.json?foo={time.time()}').read())

        self.build_interface()

    # ----------------------------------------------------------------------

    def build_interface(self):
        """"""
        self.primary_area = html.DIV(Class='area primary-area')
        self.secondary_area = html.DIV(Class='secondary-area')

        for element in self.interface:
            key = element['id']
            button = html.BUTTON(element['label'], Class='cue show primary')
            button.bind('click', self.show_secondary(key))
            self.primary_area <= button

            if element['type'] == 'categorical':

                categorical_area = html.DIV(Class='categorical-area')
                for option in element['options']:
                    categorical_area <= html.BUTTON(
                        option, Class=f'cue show secondary primary-{key}')
                self.secondary_area <= categorical_area

            elif element['type'] == 'slider':

                    increase_area = html.DIV(Class='slider-area')
                    value_area = html.DIV(Class='slider-area')
                    decrease_area = html.DIV(Class='slider-area')

                    for increase in element['increase_modifiers']:
                        increase_area <= html.BUTTON(
                            increase, Class=f'cue show slider secondary primary-{key}')

                    value_area <= html.BUTTON(element['value'], Class=f'secondary gui-value show primary-{key}')

                    for decrease in element['decrease_modifiers']:
                        decrease_area <= html.BUTTON(
                            decrease, Class=f'cue show slider secondary primary-{key}')

                    self.secondary_area <= increase_area + value_area + decrease_area

            elif element['type'] == 'boolean':
                boolean_area = html.DIV(Class='boolean-area')
                
                for label, name, value in element['values']:
                    boolean_row = html.DIV(Class='boolean-row')
                    boolean_row <= html.BUTTON('True', Class=f'cue show boolean secondary primary-{key}')
                    # boolean_row <= w.label(f'{name}: {value}', typo='body1', Class=f'boolean-text cue show secondary primary-{key}')
                    
                    boolean_row <= html.BUTTON(f'{name}: {value}', Class=f'secondary gui-value show primary-{key}')
                    
                    boolean_row <= html.BUTTON('False', Class=f'cue show boolean secondary primary-{key}')
                    boolean_area <= boolean_row
                boolean_area <= boolean_row
                
                self.secondary_area <= boolean_area

        button_back = html.BUTTON(
            BACK_ARROW, Class=f'cue show secondary back-arrow')
        button_back.bind('click', lambda evt: self.show('primary'))
        self.secondary_area <= button_back

        self.stimuli_area <= self.primary_area
        self.stimuli_area <= self.secondary_area

        self.dashboard <= w.label('P300 GUI', typo='headline4')
        self.dashboard <= w.slider(
            'Stimuli duration', min=50, max=300, step=10, value=100, id='stimuli_duration')
        self.dashboard <= w.slider(
            'Stimuli interval', min=100, max=1000, step=10, value=350, id='stimuli_interval')

        self.dashboard <= w.button('Start stimlui', on_click=self.blink)
        self.show('primary')

    # ----------------------------------------------------------------------
    def show(self, frame):
        """"""
        self.stimuli = False

        if frame == 'primary':
            a1, a2 = 'expand', 'contract'
            w1, w2 = '85%', '15%'
            for item in self.secondary_area.select(f'.secondary'):
                item.style = {'opacity': 0.2}
            for item in self.primary_area.select(f'.primary'):
                item.style = {'opacity': 1}

        elif frame == 'secondary':
            a2, a1 = 'expand', 'contract'
            w2, w1 = '85%', '15%'

            for item in self.secondary_area.select(f'.secondary'):
                item.style = {'opacity': 1}
            for item in self.primary_area.select(f'.primary'):
                item.style = {'opacity': 0.2}

        self.frame = frame
        self.primary_area.class_name = f'area primary-area {a1}'
        self.secondary_area.class_name = f'area secondary-area {a2}'
        self.primary_area.style = {'width': w1}
        self.secondary_area.style = {'width': w2}

        timer.set_timeout(lambda: setattr(self, 'stimuli', True), 2000)

    # ----------------------------------------------------------------------
    def show_secondary(self, key):
        def wrap(*args, **kwargs):
            """"""
            self.show('secondary')

            for item in self.secondary_area.select(f'.secondary'):
                item.class_name += ' hide'
                item.class_name = item.class_name.replace('show', '')

            for item in self.secondary_area.select(f'.secondary.primary-{key}'):
                item.class_name += ' show'
                item.class_name = item.class_name.replace('hide', '')

            if item := self.secondary_area.select_one(f'.secondary.back-arrow'):
                item.class_name += ' show'
                item.class_name = item.class_name.replace('hide', '')

        return wrap

    # ----------------------------------------------------------------------
    def blink(self):
        """"""
        if self.frame == 'secondary':
            item = random.choice(
                self.secondary_area.select(f'.cue.secondary.show'))
        elif self.frame == 'primary':
            item = random.choice(self.primary_area.select(f'.cue.primary'))

        if item == self.item:
            self.blink()
            return

        self.item = item
        if self.stimuli:
            self.blink_element(item)
        timer.set_timeout(self.blink, w.get_value('stimuli_interval'))

    # ----------------------------------------------------------------------
    def blink_element(self, item):
        """"""
        item.class_name += ' blink'
        timer.set_timeout(lambda: self.blink_element_off(
            item), w.get_value('stimuli_duration'))

    # ----------------------------------------------------------------------
    def blink_element_off(self, item):
        """"""
        item.class_name = item.class_name.replace('blink', '')


if __name__ == '__main__':
    P300GUI()


