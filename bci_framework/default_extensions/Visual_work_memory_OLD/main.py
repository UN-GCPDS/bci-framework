from bci_framework.extensions.stimuli_delivery import StimuliServer, StimuliAPI, DeliveryInstance
from bci_framework.extensions.stimuli_delivery.utils import Widgets, Tone

from browser import document, timer, html, window
from points import get_points

import time
import random

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


UNICODE_RIGHT = '&#x1f852;'
UNICODE_LEFT = '&#x1f850;'


########################################################################
class Memory(StimuliAPI):

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        self.add_stylesheet('styles.css')

        self.build_areas()
        self.add_run_progressbar()
        self.add_cross()

        self.on_trial = False

        self.widgets = Widgets()
        self.tone = Tone()
        
        self.dashboard <= self.widgets.label('Visual working memory', 'headline3', style={'margin-bottom': '15px', 'display': 'flex', })
        self.dashboard <= html.BR()

        self.dashboard <= self.widgets.label('Markers', 'headline4')
        self.dashboard <= self.widgets.radios('Shapes', [('square', '0%'), ('circles', '100%')], id='shapes')
        self.dashboard <= self.widgets.slider(label='Number of markers by hemifield:', min=2, max=8, value=4, discrete=True, markers=True, id='squares')
        self.dashboard <= self.widgets.slider(label='Marker size:', min=2, max=10, step=0.1, value=7, unit='% of screen height', id='size',)
        self.dashboard <= self.widgets.slider(label='Minimum distance between markers:', min=100, max=1000, value=200, unit='% of squares size', id='distance')

        self.dashboard <= self.widgets.label('Intervals', 'headline4')
        self.dashboard <= self.widgets.slider(label='Stimulus onset asynchrony:', min=100, max=1000, value=200, unit='ms', id='soa')
        self.dashboard <= self.widgets.slider(label='Memory array:', min=50, max=500, value=100, unit='ms', id='memory_array')
        self.dashboard <= self.widgets.slider(label='Retention interval:', min=500, max=1500, value=900, unit='ms', id='retention')
        self.dashboard <= self.widgets.slider(label='Test array:', min=500, max=5000, value=2000, unit='ms', id='test_array')

        self.dashboard <= self.widgets.label('Trial', 'headline4')

        self.dashboard <= self.widgets.slider(label='Max differences:', min=1, max=8, value=2, discrete=True, markers=True, id='differences')
        self.dashboard <= self.widgets.slider(label='Numbers of trials for each difference:', min=1, max=8, value=4, discrete=True, markers=True, id='trials')
        
        self.dashboard <= self.widgets.switch('Wait for user response', checked=True, id='wait')
        self.dashboard <= self.widgets.switch('Record EEG', checked=False, on_change=None, id='record')

        self.dashboard <= self.widgets.button('Test single trial', on_click=self.single_trial, style={'margin': '0 30px'})
        self.dashboard <= self.widgets.button('Start run', on_click=self.start, style={'margin': '0 15px'})
        self.dashboard <= self.widgets.button('Stop run', on_click=self.stop, style={'margin': '0 15px'})


    # ----------------------------------------------------------------------
    def test_array(self):
        """"""
        if not hasattr(self, 'button_different'):
            self.button_different = self.widgets.button('Different (q)', unelevated=False, outlined=True, on_click=lambda :self.manual_trial('DIFFERENT'), Class='test-button', id='different')
            self.button_identical = self.widgets.button('Identical (p)', unelevated=False, outlined=True, on_click=lambda :self.manual_trial('IDENTICAL'), Class='test-button', id='identical')

            self.stimuli_area <= self.button_different
            self.stimuli_area <= self.button_identical

        self.button_identical.style = {'display': 'block'}
        self.button_different.style = {'display': 'block'}

    # ----------------------------------------------------------------------
    def start(self):
        """"""
        self.configure()
        if self.widgets.get_value('record'):
            self.start_record()
        timer.set_timeout(lambda :self.start_trial(single=False), 2000)        
        
        
    # ----------------------------------------------------------------------
    def stop(self):
        """"""
        self.clear()
        self.set_progress(0)
        if hasattr(self, 'auto_trials'):
            timer.clear_timeout(self.auto_trials)
            
        if self.widgets.get_value('record'):
            timer.set_timeout(self.stop_record, 2000)


    # ----------------------------------------------------------------------
    def single_trial(self):
        """"""
        self.configure()
        self.start_trial()

    # ----------------------------------------------------------------------
    @DeliveryInstance.both
    def configure(self):
        """"""
        self.propagate_seed()
        differences = int(self.widgets.get_value('differences'))
        trials = int(self.widgets.get_value('trials'))

        self.trials = []
        for d in range(differences + 1):
            self.trials.extend([[random.choice([1, 0]), d]] * trials)

        self.total_trials = len(self.trials)
        random.shuffle(self.trials)

    # ----------------------------------------------------------------------
    @DeliveryInstance.both
    def start_trial(self, single=True):
        """"""
        self.clear()

        self.build_trial()
        self.shuffled_colors = self.shuffle()

        self.set_progress(1 - (len(self.trials) - 1) / self.total_trials)

        soa_time = self.widgets.get_value('soa')
        ma_time = soa_time + self.widgets.get_value('memory_array')
        rt_time = ma_time + self.widgets.get_value('retention')
        test_time = rt_time + self.widgets.get_value('test_array')

        if not single:
            self.tone("C#6", 200)

        self.send_marker('START')
        self.start_arrow()
        timer.set_timeout(lambda: self.set_visible_markers(True), soa_time)
        timer.set_timeout(lambda: self.set_visible_markers(False), ma_time)
        timer.set_timeout(self.change_markers, rt_time)
        timer.set_timeout(lambda: self.set_visible_markers(False), test_time)

        if not single and self.trials:
            random_trial_interval = random.randint(1000, 1800)
            print(f'Random trial interval: {random_trial_interval}')
            if not self.widgets.get_value('wait'):
                self.auto_trials = timer.set_timeout(lambda: self.start_trial(False), test_time + random_trial_interval)
                

    # ----------------------------------------------------------------------
    @DeliveryInstance.event
    def manual_trial(self, marker):
        """"""
        self.send_marker(marker)
        self.clear()
        timer.set_timeout(lambda: self.start_trial(False), 2000)

    # ----------------------------------------------------------------------
    def start_arrow(self):
        """"""
        self.clear()

        if not hasattr(self, 'hint'):
            self.hint = html.SPAN('', id='hint')
            self.stimuli_area <= self.hint

        if self.trials[0][0]:
            self.hint.html = UNICODE_RIGHT
        else:
            self.hint.html = UNICODE_LEFT

        self.hint.style = {'display': 'flex'}

    # ----------------------------------------------------------------------
    def clear(self):
        """"""
        self.set_visible_markers(False)
        if hasattr(self, 'hint'):
            self.hint.style = {'display': 'none'}
        if hasattr(self, 'button_different'):
            self.button_identical.style = {'display': 'none'}
            self.button_different.style = {'display': 'none'}
        self.add_cross()

    # ----------------------------------------------------------------------
    def set_visible_markers(self, visible=False):
        """"""
        if visible:
            self.send_marker('SHOW')
        else:
            self.send_marker('HIDE')
        
        if not hasattr(self, 'markers_r'):
            return

        if hasattr(self, 'hint'):
            self.hint.style = {'display': 'none'}

        right = [marker for marker, color in self.markers_r]
        left = [marker for marker, color in self.markers_l]

        for marker in right + left:
            if visible:
                marker.style = {'display': 'block'}
            else:
                marker.style = {'display': 'none'}

    # ----------------------------------------------------------------------
    def build_trial(self):
        """"""
        boxes = self.widgets.get_value('squares')
        size = self.widgets.get_value('size')
        distance = self.widgets.get_value('distance')
        shapes = self.widgets.get_value('shapes')

        points_r = get_points(boxes, distance * size / 150, size)
        points_l = get_points(boxes, distance * size / 150, size)

        colors = COLORS + COLORS
        random.shuffle(colors)

        self.markers_r = []
        for i, point in enumerate(points_r):
            self.markers_r.append([html.DIV('', id=f'right_{i}', style={
                'background-color': colors[i],
                'border-radius': shapes,
                'width': f'{size}vh',
                'height': f'{size}vh',
                'left': f'calc(100% - {point[0]}% - {size/2}vh)',
                'top': f'calc({point[1]}% - {size/2}vh)',
                'position': 'absolute',
                'display': 'none',
            }), colors[i]])
            self.stimuli_area <= self.markers_r[-1][0]

        self.markers_l = []
        for j, point in enumerate(points_l):
            self.markers_l.append([html.DIV('', id=f'left_{i}', style={
                'background-color': colors[i + j + 1],
                'border-radius': shapes,
                'width': f'{size}vh',
                'height': f'{size}vh',
                'left': f'calc({point[0]}% - {size/2}vh)',
                'top': f'calc({point[1]}% - {size/2}vh)',
                'position': 'absolute',
                'display': 'none',
            }), colors[i + j + 1]])
            self.stimuli_area <= self.markers_l[-1][0]

    # ----------------------------------------------------------------------
    def change_markers(self):
        """"""
        f = self.shuffled_colors
        self.send_marker(f'{len(f)}')

        for i, color in enumerate(f):
            if self.trials[0][0]:
                self.markers_r[i][0].style = {'background-color': color}
            else:
                self.markers_l[i][0].style = {'background-color': color}

        self.set_visible_markers(True)
        self.trials.pop(0)
        self.test_array()

    # ----------------------------------------------------------------------
    def shuffle(self):
        """"""
        X = self.trials[0][1]
        right = [color for marker, color in self.markers_r]
        left = [color for marker, color in self.markers_l]

        single = [s for s in (right + left) if (right + left).count(s) == 1]
        usable = list(set(COLORS) - set(right + left)) + single

        if self.trials[0][0]:
            original = right[:X]
        else:
            original = left[:X]

        mix = original + usable
        while [a == b for a, b in zip(original, mix[:X])].count(True):
            random.shuffle(mix)

        return mix[:X]


if __name__ == '__main__':
    StimuliServer('Memory')


