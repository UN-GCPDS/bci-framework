"""
=====================
Visual working memory
=====================

"""

from bci_framework.extensions.stimuli_delivery import StimuliAPI
from bci_framework.extensions.stimuli_delivery.utils import keypress
from bci_framework.extensions.stimuli_delivery.utils import Widgets as w
from bci_framework.extensions.stimuli_delivery.utils import Tone as t
from bci_framework.extensions.stimuli_delivery.utils import Units as u

from browser import document, timer, html, window
from points import get_points

import time
import random
from typing import Literal
import logging

COLORS = [
    '#ff0000',
    '#0000ff',
    '#ff00ff',
    '#00ff00',
    '#ffff00',
    '#ffffff',
    '#000000',
]

UNICODE_CUES = {
    'Right': 'arrow-right-short',
    'Left': 'arrow-left-short',
}


########################################################################
class VisualWorkingMemory(StimuliAPI):
    """Visual working memory: change detection task."""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        self.add_stylesheet('styles.css')
        self.build_areas()
        self.show_cross()

        self.dashboard <= w.label(
            'Visual working memory - Change detection task', 'headline4')
        self.dashboard <= html.BR()

        # Markers
        self.dashboard <= w.label('Squares', 'headline4')
        self.dashboard <= w.slider(
            label='Squares size:',
            min=0.1,
            max=5,
            step=0.01,
            value=1.17,
            unit='dva',
            id='size'
        )
        self.dashboard <= w.slider(
            label='Minimum distance between Squares:',
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
            label='Inter trial break:',
            min=0,
            max=3000,
            value=2000,
            unit='ms',
            id='break',
        )
        self.dashboard <= w.slider(
            label='Arrow cue:',
            min=100,
            max=1000,
            value=200,
            unit='ms',
            id='cue',
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
        self.dashboard <= w.checkbox(
            label='Task level:',
            options=[[f'{i} squares', i in [1, 2, 4]] for i in range(1, 7)],
            on_change=None,
            id='task_level',
        )
        self.dashboard <= w.slider(
            label='Numbers of trials per level:',
            min=1,
            max=500,
            value=100,
            discrete=True,
            markers=True,
            id='trials'
        )

        # Presentation
        self.dashboard <= w.label('Presentation', 'headline4')
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
            # id='record',
        )
        self.dashboard <= w.switch(
            label='Dummy mode',
            checked=False,
            id='dummy',
        )

        self.dashboard <= w.button('Test shapes', on_click=self.test_shapes)
        self.dashboard <= w.toggle_button([('Start run', self.start), ('Stop run', self.stop)], id='run')
        self.dashboard <= w.toggle_button([('Start marker synchronization', self.start_marker_synchronization), ('Stop marker synchronization', self.start_marker_synchronization)], id='sync')



    # ----------------------------------------------------------------------
    def test_shapes(self) -> None:
        """Preview the size and distribution of the squares."""
        self.clear()
        keypress(self.handle_response)
        u(d=w.get_value('d'), dpi=w.get_value('dpi'))
        self.build_squares_area()
        self.soa(cue='Right', shapes=4, change=True)
        self.memory_array(cue='Right', shapes=4, change=True)

    # ----------------------------------------------------------------------
    def start(self):
        """Start the run.

        A run consist in a consecutive trials execution.
        """
        if w.get_value('record'):
            self.start_record()

        self.build_trials()
        timer.set_timeout(lambda: self.run_pipeline(
            self.pipeline_trial, self.trials, callback='stop_run'), 2000)

    # ----------------------------------------------------------------------
    def stop(self):
        """Stop pipeline execution."""
        self.stop_pipeline()

    # ----------------------------------------------------------------------
    def stop_run(self):
        """"""
        self.clear()
        w.get_value('run').off()
        if w.get_value('record'):
            timer.set_timeout(self.stop_record, 2000)

    # ----------------------------------------------------------------------
    def build_trials(self) -> None:
        """Define the `trials` and `pipeline trials`.

        The `trials` consist (in this case) in a list of cues.
        The `pipeline trials` is a set of couples `(callable, duration)` that
        define a single trial, this list of functions are executed asynchronously
        and repeated for each trial.
        """
        levels = [int(v[:1]) for v in w.get_value('task_level')]
        trials = levels * w.get_value('trials')
        cues = [random.choice(['Right', 'Left']) for _ in trials]
        changes = [random.choice([0, 1]) for _ in trials]

        trials = list(zip(trials, cues, changes))

        self.trials = [{'cue': cue,
                        'shapes': shapes,
                        'change': bool(change),
                        } for shapes, cue, change in trials]
        random.shuffle(self.trials)

        self.pipeline_trial = [

            ['soa', w.get_value('break')],
            ['cue', w.get_value('cue')],
            ['memory_array', w.get_value('memory_array')],
            ['retention', w.get_value('retention')],
            ['test_array', w.get_value('test_array')],
        ]

    # ----------------------------------------------------------------------
    def soa(self, cue: Literal['Right', 'Left'], shapes: int, change: bool) -> None:
        """Stimulus onset asynchronously."""
        self.clear()
        u(d=w.get_value('d'), dpi=w.get_value('dpi'))
        self.build_squares_area()
        self.build_markers(shapes)
        if change:
            self.prepare_shuffle(cue)

    # ----------------------------------------------------------------------
    def cue(self, cue: Literal['Right', 'Left'], shapes: int, change: bool) -> None:
        """Show the cue to indicate the hemifield target."""
        if not hasattr(self, 'cue_placeholder'):
            self.cue_placeholder = html.I('', id='cue', style={
                'font-size': u.dva(8),
                'padding-top': f'calc(50vh - {u.dva(8, scale=1/2)})',
            })
            self.stimuli_area <= self.cue_placeholder

        self.cue_placeholder.class_name = f'bi bi-{UNICODE_CUES[cue]}'
        self.send_marker(cue)

    # ----------------------------------------------------------------------
    def memory_array(self, cue: Literal['Right', 'Left'], shapes: int, change: bool) -> None:
        """Show the initial array."""
        if hasattr(self, 'cue_placeholder'):
            self.cue_placeholder.class_name = ''
        self._set_visible_markers(True)
        self.send_marker(f'{shapes}')

    # ----------------------------------------------------------------------
    def retention(self, cue: Literal['Right', 'Left'], shapes: int, change: bool) -> None:
        """Remove the array."""
        self.send_marker('Retention')
        self._set_visible_markers(False)

    # ----------------------------------------------------------------------
    def test_array(self, cue: Literal['Right', 'Left'], shapes: int, change: bool) -> None:
        """Show the array again."""

        if change:  # Show an array with differences
            f = self.shuffled_colors
            for i, color in enumerate(f):
                if cue == 'Right':
                    self.markers_r[i][0].style = {'background-color': color}
                    if w.get_value('record'):
                        self.markers_r[i][0].style = {
                            'border-radius': '100%'}

                elif cue == 'Left':
                    self.markers_l[i][0].style = {'background-color': color}
                    if w.get_value('record'):
                        self.markers_r[i][0].style = {
                            'border-radius': '100%'}

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
        keypress(self.handle_response, timeout=w.get_value('test_array'))
        if change:
            self.send_marker('Changed')
        else:
            self.send_marker('No-changed')

    # ----------------------------------------------------------------------
    def handle_response(self, response: str) -> None:
        """Capture the subject keyboard response."""
        if self.mode == 'stimuli':
            if response == 'q':
                # print("DIFFFERENT")
                self.send_marker(f'Different')
            elif response == 'p':
                # print("IDENTICAL")
                self.send_marker(f'Identical')
            else:
                self.send_marker(f'No-response')

    # ----------------------------------------------------------------------
    def _set_visible_markers(self, visible: bool) -> None:
        """Toggle the squares visibility."""
        if hasattr(self, 'markers_r'):
            right = [marker for marker, color in self.markers_r]
            left = [marker for marker, color in self.markers_l]
            for marker in right + left:
                if visible:
                    marker.style = {'display': 'block'}
                else:
                    marker.style = {'display': 'none'}

    # ----------------------------------------------------------------------
    def clear(self) -> None:
        """Remove all elements from view."""
        self._set_visible_markers(False)
        if hasattr(self, 'cue_placeholder'):
            self.cue_placeholder.class_name = ''
        if hasattr(self, 'button_different'):
            self.button_identical.style = {'display': 'none'}
            self.button_different.style = {'display': 'none'}

    # ----------------------------------------------------------------------
    def build_markers(self, shapes: int) -> None:
        """Display the squares.
        """
        size = w.get_value('size')
        distance = w.get_value('distance')

        points_r = get_points(shapes, distance, size)
        points_l = get_points(shapes, distance, size)

        colors = COLORS + COLORS
        random.shuffle(colors)

        for element in document.select('.bci-marker'):
            element.remove()

        self.markers_r = []
        for i, point in enumerate(points_r):
            self.markers_r.append([html.DIV('', Class='bci-marker', id=f'right_{i}', style={
                'background-color': colors[i],
                'width': u.dva(size),
                'height': u.dva(size),
                'left': f'calc({u.dva(point[0])} - {u.dva(size, scale=0.5)})',
                'top': f'calc({u.dva(point[1])} - {u.dva(size, scale=0.5)})',
                'position': 'absolute',
                'display': 'none',
            }), colors[i]])
            document.select_one(
                '.markers_r-placeholder') <= self.markers_r[-1][0]

        self.markers_l = []
        for j, point in enumerate(points_l):
            self.markers_l.append([html.DIV('', Class='bci-marker', id=f'left_{i}', style={
                'background-color': colors[i + j + 1],
                'width': u.dva(size),
                'height': u.dva(size),
                'left': f'calc({u.dva(point[0])} - {u.dva(size, scale=0.5)})',
                'top': f'calc({u.dva(point[1])} - {u.dva(size, scale=0.5)})',
                'position': 'absolute',
                'display': 'none',
            }), colors[i + j + 1]])
            document.select_one(
                '.markers_l-placeholder') <= self.markers_l[-1][0]

    # ----------------------------------------------------------------------
    def prepare_shuffle(self, cue: Literal['Right', 'Left'], differences: int = 1) -> None:
        """Makes sure of changing the color of the squares."""
        right = [color for marker, color in self.markers_r]
        left = [color for marker, color in self.markers_l]

        single = [s for s in (right + left) if (right + left).count(s) == 1]
        usable = list(set(COLORS) - set(right + left)) + single

        if cue == 'Right':
            original = right[:differences]
        elif cue == 'Left':
            original = left[:differences]

        mix = original + usable
        while [a == b for a, b in zip(original, mix[:differences])].count(True):
            random.shuffle(mix)

        self.shuffled_colors = mix[:differences]

    # ----------------------------------------------------------------------
    def synchronizer(self, value: bool) -> None:
        """Show or hide synchronizer."""
        if value:
            self.show_synchronizer()
        else:
            self.hide_synchronizer()

    # ----------------------------------------------------------------------
    def build_squares_area(self) -> None:
        """Create a space to positioning the squares."""
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
                                          'background-color': '#818181',
                                          'position': 'absolute',
                                          'z-index': 10,
                                      })

        self.stimuli_area <= html.DIV(Class='markers_r-placeholder',
                                      style={
                                          'width': u.dva(7.2),
                                          'height': u.dva(13.15),
                                          'margin-top': f'calc(50vh - {u.dva(13.15, scale=0.5)})',
                                          'margin-left': f'calc(50% - {u.dva(7.2, scale=0.5)} + {u.dva(5.4)})',
                                          'background-color': '#818181',
                                          'position': 'absolute',
                                          'z-index': 10,
                                      })


if __name__ == '__main__':
    VisualWorkingMemory()


