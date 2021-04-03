from bci_framework.extensions.stimuli_delivery import StimuliAPI
from bci_framework.extensions.stimuli_delivery.utils import keypress
from bci_framework.extensions.stimuli_delivery.utils import Widgets as w
from bci_framework.extensions.stimuli_delivery.utils import Tone as t
from bci_framework.extensions.stimuli_delivery.utils import Units as u

from browser import document, timer, html, window
from points import get_points

import time
import random

import logging

COLORS = [

    '#1f77b4',
    '#ff7f0e',
    '#2ca02c',
    '#d62728',
    '#9467bd',
    '#8c564b',
    '#e377c2',
    '#7f7f7f',
    '#bcbd22',
    '#17becf',

]

UNICODE_CUES = {
    'Right': '&#x1f86a;',
    'Left': '&#x1f868;',
    'Up': '&#x1f869;',
    'Bottom': '&#x1f86b;',
}


########################################################################
class Memory(StimuliAPI):

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        self.add_stylesheet('styles.css')
        self.build_areas()
        self.show_cross()
        
        self.dashboard <= w.label('Visual working memory - Change detection task', 'headline4')
        self.dashboard <=  html.BR()

        # Markers
        self.dashboard <= w.label('Markers', 'headline4')
        self.dashboard <= w.radios(
            label='Shapes',
            options=[('square', '0%'),
                     ('circles', '100%')],
            id='shapes'
        )
        self.dashboard <= w.slider(
            label='Number of markers by hemifield:',
            min=2,
            max=8,
            value=4,
            discrete=True,
            markers=True,
            id='squares'
        )
        self.dashboard <= w.slider(
            label='Marker size:',
            min=0.1,
            max=5,
            step=0.01,
            value=1.17,
            unit='dva',
            id='size'
        )
        self.dashboard <= w.slider(
            label='Minimum distance between markers:',
            min=1,
            max=10,
            step=0.01,
            value=3.5,
            unit='dva',
            id='distance'
        )

        # Intervals
        self.dashboard <= w.label('Intervals', 'headline4')
        self.dashboard <= w.slider(
            label='Stimulus onset asynchrony:',
            min=100,
            max=1000,
            value=200,
            unit='ms',
            id='soa',
        )
        self.dashboard <= w.slider(
            label='Memory array:',
            min=50,
            max=500,
            value=100,
            unit='ms',
            id='memory_array',
        )
        self.dashboard <= w.slider(
            label='Retention interval:',
            min=500,
            max=1500,
            value=900,
            unit='ms',
            id='retention'
        )
        self.dashboard <= w.slider(
            label='Test array:',
            min=500,
            max=5000,
            value=2000,
            unit='ms',
            id='test_array'

        )

        # Trial
        self.dashboard <= w.label('Trial', 'headline4')
        self.dashboard <= w.slider(
            label='Max differences:',
            min=1,
            max=8,
            value=2,
            discrete=True,
            markers=True,
            id='differences'
        )
        self.dashboard <= w.slider(
            label='Numbers of trials for each difference:',
            min=1,
            max=8,
            value=4,
            discrete=True,
            markers=True,
            id='trials'
        )
        
        # Montage
        self.dashboard <= w.label('Montage', 'headline4')
        self.dashboard <= w.slider(
            label='Distance from monitor:',
            min=0.1,
            max=3,
            step=0.01,
            value=0.3,
            unit='m',
            id='d'
        )
        self.dashboard <= w.slider(
            label='Monitor DPI:',
            min=1,
            max=450,
            step=1,
            value=141,
            unit='dpi',
            id='dpi'
        )

        self.dashboard <= w.switch(
            label='Record EEG',
            checked=False,
            id='record',
        )
        self.dashboard <= w.switch(
            label='External marker synchronizer',
            checked=False,
            on_change=self.synchronizer,
            id='record',
        )
        
        self.dashboard <= w.button('Test shapes', raised=False, outlined=True, on_click=self.test_shapes)
        self.dashboard <= w.button('Start run', on_click=self.start)
        self.dashboard <= w.button('Stop run', on_click=self.stop)
        
    # ----------------------------------------------------------------------
    def test_shapes(self):
        """"""
        self.clear()
        keypress(self.handle_response)
        u(d=w.get_value('d'), dpi=w.get_value('dpi'))
        self.build_markers_area()
        self.soa('Right', d=2)
        self.memory_array()
        
    # ----------------------------------------------------------------------
    def handle_response(self, response):
        """"""
        if response == 'q':
            print("DIFFFERENT")
        elif response == 'p':
            print("IDENTICAL")

    # ----------------------------------------------------------------------
    def soa(self, cue, d, **kwargs):
        """"""
        self.clear()
        u(d=w.get_value('d'), dpi=w.get_value('dpi'))
        self.build_markers_area()
        self.build_markers()
        self.prepare_shuffle(cue, d)

    # ----------------------------------------------------------------------
    def cue(self, cue, **kwargs):
        """"""
        if not hasattr(self, 'cue_placeholder'):
            self.cue_placeholder = html.SPAN('', id='cue', style={
                'font-size': u.dva(8),
                'padding-top': f'calc(50vh - {u.dva(8, scale=1/50)})',
                })
            self.stimuli_area <= self.cue_placeholder

        # self.send_marker(cue)
        self.cue_placeholder.html = UNICODE_CUES[cue]
        self.cue_placeholder.style = {'display': 'flex'}

    # ----------------------------------------------------------------------
    def memory_array(self, **kwargs):
        """"""
        if hasattr(self, 'cue_placeholder'):
            self.cue_placeholder.style = {'display': 'none'}
        self._set_visible_markers(True)

    # ----------------------------------------------------------------------
    def _set_visible_markers(self, visible):
        """"""
        if hasattr(self, 'markers_r'):
            right = [marker for marker, color in self.markers_r]
            left = [marker for marker, color in self.markers_l]
            for marker in right + left:
                if visible:
                    marker.style = {'display': 'block'}
                else:
                    marker.style = {'display': 'none'}

    # ----------------------------------------------------------------------
    def retention(self, **kwargs):
        """"""
        self._set_visible_markers(False)

    # ----------------------------------------------------------------------
    def test_array(self, cue, **kwargs):
        """"""
        f = self.shuffled_colors
        keypress(self.handle_response)
        for i, color in enumerate(f):
            if cue == 'Right':
                self.markers_r[i][0].style = {'background-color': color}
            elif cue == 'Left':
                self.markers_l[i][0].style = {'background-color': color}

        self._set_visible_markers(True)

        if not hasattr(self, 'button_different'):
            self.button_different = w.button('Different (q)', unelevated=False, outlined=True, on_click=lambda: self.manual_trial(
                'DIFFERENT'), Class='test-button', id='different')
            self.button_identical = w.button('Identical (p)', unelevated=False, outlined=True, on_click=lambda: self.manual_trial(
                'IDENTICAL'), Class='test-button', id='identical')

            self.stimuli_area <= self.button_different
            self.stimuli_area <= self.button_identical

        self.button_identical.style = {'display': 'block'}
        self.button_different.style = {'display': 'block'}

    # ----------------------------------------------------------------------
    def build_trials(self):
        """"""

        self.trials = [{'cue': 'Right',
                        'd': 2,
                        },
                       {'cue': 'Right',
                        'd': 2,
                        },
                       {'cue': 'Right',
                        'd': 2,
                        },
                       {'cue': 'Right',
                        'd': 2,
                        },

                       ]

        self.pipeline_trial = [

            (self.soa, 1000),
            (self.cue, 500),
            (self.memory_array, 500),
            (self.retention, 500),
            (self.test_array, 2000),

        ]

    # ----------------------------------------------------------------------
    def clear(self):
        """"""
        self._set_visible_markers(False)
        if hasattr(self, 'cue_placeholder'):
            self.cue_placeholder.style = {'display': 'none'}
        if hasattr(self, 'button_different'):
            self.button_identical.style = {'display': 'none'}
            self.button_different.style = {'display': 'none'}

    # ----------------------------------------------------------------------
    def start(self):
        """"""
        if w.get_value('record'):
            self.start_record()

        self.build_trials()
        timer.set_timeout(lambda: self.run_pipeline(
            self.pipeline_trial, self.trials, callback=self.clear), 2000)

    # ----------------------------------------------------------------------
    def stop(self):
        """"""
        self.stop_pipeline()
        self.clear()
        if w.get_value('record'):
            timer.set_timeout(self.stop_record, 2000)

    # ----------------------------------------------------------------------
    def build_markers(self):
        """"""
        boxes = w.get_value('squares')
        size = w.get_value('size')
        distance = w.get_value('distance')
        shapes = w.get_value('shapes')

        points_r = get_points(boxes, distance, size)
        points_l = get_points(boxes, distance, size)

        colors = COLORS + COLORS
        random.shuffle(colors)

        for element in document.select('.bci-marker'):
            element.remove()

        self.markers_r = []
        for i, point in enumerate(points_r):
            self.markers_r.append([html.DIV('', Class='bci-marker', id=f'right_{i}', style={
                'background-color': colors[i],
                'border-radius': shapes,
                'width': u.dva(size),
                'height': u.dva(size),
                'left': f'calc({u.dva(point[0])} - {u.dva(size, scale=0.5)})',
                'top': f'calc({u.dva(point[1])} - {u.dva(size, scale=0.5)})',
                'position': 'absolute',
                'display': 'none',
            }), colors[i]])
            document.select_one('.markers_r-placeholder') <= self.markers_r[-1][0]

        self.markers_l = []
        for j, point in enumerate(points_l):
            self.markers_l.append([html.DIV('', Class='bci-marker', id=f'left_{i}', style={
                'background-color': colors[i + j + 1],
                'border-radius': shapes,
                'width': u.dva(size),
                'height': u.dva(size),                
                'left': f'calc({u.dva(point[0])} - {u.dva(size, scale=0.5)})',
                'top': f'calc({u.dva(point[1])} - {u.dva(size, scale=0.5)})',
                'position': 'absolute',
                'display': 'none',
            }), colors[i + j + 1]])
            document.select_one('.markers_l-placeholder') <= self.markers_l[-1][0]

    # ----------------------------------------------------------------------
    def prepare_shuffle(self, cue, d):
        """"""
        right = [color for marker, color in self.markers_r]
        left = [color for marker, color in self.markers_l]

        single = [s for s in (right + left) if (right + left).count(s) == 1]
        usable = list(set(COLORS) - set(right + left)) + single

        if cue == 'Right':
            original = right[:d]
        elif cue == 'Left':
            original = left[:d]

        mix = original + usable
        while [a == b for a, b in zip(original, mix[:d])].count(True):
            random.shuffle(mix)

        self.shuffled_colors = mix[:d]

    # ----------------------------------------------------------------------
    def synchronizer(self, value):
        """"""
        if value:
            self.show_synchronizer()
        else:
            self.hide_synchronizer()
            
    # ----------------------------------------------------------------------
    def build_markers_area(self):
        """"""
        
        if element := document.select_one('.markers_l-placeholder'):
            element.remove()
            
        if element := document.select_one('.markers_r-placeholder'):
            element.remove()

        self.stimuli_area <= html.DIV(Class='markers_l-placeholder',
        style={
        'width': u.dva(7.2),
        'height': u.dva(13.15),
        'margin-top': f'calc(50vh - {u.dva(13.15, scale=0.5)})',
        'margin-left': f'calc(50% - {u.dva(7.2, scale=0.5)} - {u.dva(5.4)})',
        'background-color': '#f3f3f3',
        'position': 'absolute',
        'z-index': 10,
        })

  
        self.stimuli_area <= html.DIV(Class='markers_r-placeholder',
        
        style={
        'width': u.dva(7.2),
        'height': u.dva(13.15),
        'margin-top': f'calc(50vh - {u.dva(13.15, scale=0.5)})',
        'margin-left': f'calc(50% - {u.dva(7.2, scale=0.5)} + {u.dva(5.4)})',
        'background-color': '#f3f3f3',
        'position': 'absolute',        
        'z-index': 10,
        })



if __name__ == '__main__':
    Memory()


