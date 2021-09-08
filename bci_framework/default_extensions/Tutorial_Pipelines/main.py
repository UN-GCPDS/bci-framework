"""

=========
Pipelines
=========

Pipelines consist in asynchronous controlled method execution


"""

from bci_framework.extensions.stimuli_delivery import StimuliAPI
from bci_framework.extensions.stimuli_delivery.utils import Widgets as w
import logging


########################################################################
class Pipelines(StimuliAPI):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_stylesheet('styles.css')

        self.build_areas()
        self.show_cross()

        self.dashboard <= w.slider(
            label='slider',
            min=10,
            max=1000,
            value=500,
            step=1,
            unit='ms',
            id='slider',
        )
        self.dashboard <= w.range_slider(
            label='range',
            min=100,
            max=1000,
            value_lower=500,
            value_upper=700,
            step=1,
            unit='ms',
            id='range',
        )
        
        self.continue_= False
        self.dashboard <= w.button('Start pipeline', on_click=self.start)

    # ----------------------------------------------------------------------
    def start(self):
        """"""
        trials = [
            {'s1': 'Hola',  # Trial 1
             'r1': 91,
             },

            {'s1': 'Mundo',  # Trial 2
             'r1': 85,
             },

            {'s1': 'Python',  # Trial 3
             'r1': 30,
             },
        ]

        # Each method in pipeline will receibe as argument the on turn trial argument
        pipeline_trial = [
            ['view1', 50],  # Execute `self.view1` and wait 500 ms
            
            # Execute `self.view2` and wait a random (uniform) time selected between 500 and 1500
            ['view2', [500, 1500]],
            
            # Execute `self.view3` and wait the time defined in the slider
            ['view3', w.get_value('slider')],
            
            # Execute `self.view4` and wait a random (uniform) time selected between the range of the slider
            ['view4', w.get_value('range')],

        ]

        self.run_pipeline(pipeline_trial, trials)

    # ----------------------------------------------------------------------
    def view1(self, s1, r1):
        """"""
        print(f'On view1: {s1=}, {r1=}')

    # ----------------------------------------------------------------------
    def view2(self, s1, r1):
        """"""
        print(f'On view2: {s1=}, {r1=}')

    # ----------------------------------------------------------------------
    def view3(self, s1, r1):
        """"""
        print(f'On view3: {s1=}, {r1=}')

    # ----------------------------------------------------------------------
    def view4(self, s1, r1):
        """"""
        print(f'On view4: {s1=}, {r1=}\n')




if __name__ == '__main__':
    Pipelines()


