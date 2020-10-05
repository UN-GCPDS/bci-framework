from bci_framework.projects.server import StimuliServer, StimuliAPI, DeliveryInstance
from bci_framework.projects import properties as prop
from bci_framework.projects import Tone, Widgets
from bci_framework.projects.utils import timeit

from browser import document, timer, html, window
from points import get_points

import time
import random
random.seed(8511)


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
    def __init__(self):
        """"""
        document.select('head')[0] <= html.LINK(
            href='/root/styles.css', type='text/css', rel='stylesheet')

        self.stimuli_area
        self.dashboard

        self.on_trial = False

        self.widgets = Widgets()
        self.run_progressbar = self.add_run_progressbar()

        self.tone = Tone()

        self.build_dashboard()
        self.add_cross()

    # ----------------------------------------------------------------------
    def add_cross(self):
        """"""
        self.stimuli_area <= html.DIV(Class='cross_contrast')
        self.stimuli_area <= html.DIV(Class='cross')

    # ----------------------------------------------------------------------

    def build_dashboard(self):
        """"""
        self.dashboard <= self.widgets.title('Visual working memory', 'headline3', style={'margin-bottom': '15px', 'display': 'flex', })
        self.dashboard <= html.BR()

        self.dashboard <= self.widgets.title('Markers', 'headline4')
        self.dashboard <= self.widgets.radios('Shapes', [('square', '0%'), ('circles', '100%')], id='shapes')
        self.dashboard <= self.widgets.slider(label='Number of markers by hemifield:', min=2, max=8, valuenow=4, discrete=True, markers=True, id='squares')
        self.dashboard <= self.widgets.slider(label='Marker size:', min=2, max=10, step=0.1, valuenow=7, unit='% of screen height', id='size',)
        self.dashboard <= self.widgets.slider(label='Minimum distance between markers:', min=100, max=1000, valuenow=200, unit='% of squares size', id='distance')

        self.dashboard <= self.widgets.title('Intervals', 'headline4')
        self.dashboard <= self.widgets.slider(label='Stimulus onset asynchrony:', min=100, max=1000, valuenow=200, unit='ms', id='soa')
        self.dashboard <= self.widgets.slider(label='Memory array:', min=50, max=500, valuenow=100, unit='ms', id='memory_array')
        self.dashboard <= self.widgets.slider(label='Retention interval:', min=500, max=1500, valuenow=900, unit='ms', id='retention')
        self.dashboard <= self.widgets.slider(label='Test array:', min=500, max=5000, valuenow=2000, unit='ms', id='test_array')

        self.dashboard <= self.widgets.title('Trial', 'headline4')

        self.dashboard <= self.widgets.slider(label='Max differences:', min=1, max=8, valuenow=2, discrete=True, markers=True, on_change=self.update_observations, id='differences')
        self.dashboard <= self.widgets.slider(label='Numbers of trials for each difference:', min=1, max=8, valuenow=4, discrete=True, markers=True, on_change=self.update_observations, id='trials')

        self.dashboard <= self.widgets.title('Observations', 'headline4')
        self.dashboard <= html.BR()
        self.observations = self.widgets.title('', 'body1')
        self.dashboard <= self.observations
        self.dashboard <= html.BR()

        # self.dashboard <= html.DIV(sty)

        button_box = html.DIV(style={'margin-top': '50px', 'margin-bottom': '50px', })
        self.dashboard <= button_box

        button_box <= self.widgets.button('Test single trial', connect=self.single_trial, style={'margin': '0 15px'})
        button_box <= self.widgets.button('Start run', connect=self.start_run, style={'margin': '0 15px'})
        # button_box <= self.widgets.button('Beep', connect=lambda: self.tone("C#6", 200), style={'margin': '0 15px'})

        self.update_observations()

    # ----------------------------------------------------------------------
    def update_observations(self, *args, **kwargs):
        """"""
        differences = self.widgets.get_value('differences')
        trial = self.widgets.get_value('trials')
        trials = int(trial * (differences + 1))

        duration = self.widgets.get_value('soa') + self.widgets.get_value('memory_array') + self.widgets.get_value('retention') + self.widgets.get_value('test_array') + 1400
        duration *= trials
        duration = (duration / 1000) / 60

        self.observations.html = f"There will performed <b>{trials}</b> trials per run and will lasts <b>{duration:.1f}</b> minutes."

    # ----------------------------------------------------------------------
    def test_array(self):
        """"""
        if not hasattr(self, 'button_different'):
            self.button_different = self.widgets.button('Different (q)', unelevated=False, outlined=True, style={
                'bottom': '15px',
                'width': '35%',
                'right': '10%',
                'position': 'absolute',
                'color': '#d62728',
                'border-color': '#d62728',
            })
            self.button_identical = self.widgets.button('Identical (p)', unelevated=False, outlined=True, style={
                'bottom': '15px',
                'width': '35%',
                'left': '10%',
                'position': 'absolute',
                'color': '#2ca02c',
                'border-color': '#2ca02c',
            })

            self.stimuli_area <= self.button_different
            self.stimuli_area <= self.button_identical

        self.button_identical.style = {'display': 'block'}
        self.button_different.style = {'display': 'block'}

    # ----------------------------------------------------------------------
    def start_run(self):
        """"""
        self.configure()
        self.start_trial(single=False)

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

        self.run_progressbar.mdc.set_progress(1 - (len(self.trials) - 1) / self.total_trials)

        soa_time = self.widgets.get_value('soa')
        ma_time = soa_time + self.widgets.get_value('memory_array')
        rt_time = ma_time + self.widgets.get_value('retention')
        test_time = rt_time + self.widgets.get_value('test_array')

        if not single:
            self.tone("C#6", 200)

        self.start_arrow()
        timer.set_timeout(lambda: self.set_visible_markers(True), soa_time)
        timer.set_timeout(lambda: self.set_visible_markers(False), ma_time)
        timer.set_timeout(self.change_markers, rt_time)
        timer.set_timeout(lambda: self.set_visible_markers(False), test_time)

        if not single and self.trials:
            random_trial_interval = random.randint(1000, 1800)
            print(f'Random trial interval: {random_trial_interval}')
            timer.set_timeout(lambda: self.start_trial(False), test_time + random_trial_interval)

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

        for i, color in enumerate(f):
            if self.trials[0][0]:
                self.markers_r[i][0].style = {'background-color': color}
                # self.markers_r[i][0].style = {'border': f'5px solid {color}'}
            else:
                self.markers_l[i][0].style = {'background-color': color}
                # self.markers_l[i][0].style = {'border': f'5px solid {color}'}

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


