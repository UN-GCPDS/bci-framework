from bci_framework.extensions.stimuli_delivery import StimuliServer, StimuliAPI
from bci_framework.extensions.stimuli_delivery.utils import Widgets, Tone

from browser import html, timer


NOTES = ['C',
         'C#',
         'Db',
         'D',
         'D#',
         'Eb',
         'E',
         'F',
         'F#',
         'Gb',
         'G',
         'G#',
         'Ab',
         'A',
         'A#',
         'Bb',
         'B'
         ]


########################################################################
class TonesExample(StimuliAPI):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)

        self.add_stylesheet('styles.css')

        self.stimuli_area
        self.dashboard

        self.widgets = Widgets()
        self.tone = Tone()

        self.add_cross()
        # self.add_run_progressbar()
        # self.add_blink_area()

        self.build_dashboard()

    # ----------------------------------------------------------------------
    def build_dashboard(self):
        """"""
        self.dashboard <= self.widgets.label('Tones', 'headline4', style={'margin-bottom': '15px', 'display': 'flex', })
        self.dashboard <= html.BR()

        self.dashboard <= self.widgets.slider('Frequency', min=10, max=22e3, step=1, value=447, id='f', on_change=self.tone.set_note)
        self.dashboard <= self.widgets.slider('Gain', min=0, max=1, step=0.1, value=0.5, id='gain', on_change=self.tone.set_gain)

        self.dashboard <= self.widgets.button('Start', on_click=lambda: self.tone.start(self.widgets.get_value('f'), self.widgets.get_value('gain')), style={'margin': '0 15px'})
        self.dashboard <= self.widgets.button('Stop', on_click=self.tone.stop, style={'margin': '0 15px'})

        self.dashboard <= self.widgets.label('Notes', 'headline4', style={'margin-top': '15px', 'display': 'flex', })

        self.dashboard <= self.widgets.select('Note', options=[[n, n] for n in self.tone.note_values], value='D5', id='note')

        self.dashboard <= self.widgets.button('Beep(1)', on_click=lambda: self.beep(1), style={'margin': '0 15px'})
        self.dashboard <= self.widgets.button('Beep(2)', on_click=lambda: self.beep(2), style={'margin': '0 15px'})
        self.dashboard <= self.widgets.button('Beep(3)', on_click=lambda: self.beep(3), style={'margin': '0 15px'})
        self.dashboard <= self.widgets.button('Beep(4)', on_click=lambda: self.beep(4), style={'margin': '0 15px'})

    # ----------------------------------------------------------------------
    def beep(self, n):
        """"""
        note = self.widgets.get_value('note')
        gain = self.widgets.get_value('gain')
        duration = 100

        self.tone(note, duration, gain)

        if n > 1:
            for i in range(1, n):
                timer.set_timeout(lambda: self.tone(note, duration, gain), (duration + 50) * i)

    if __name__ == '__main__':
        StimuliServer('TonesExample')


