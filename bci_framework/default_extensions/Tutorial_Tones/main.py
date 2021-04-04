from bci_framework.extensions.stimuli_delivery import StimuliAPI
from bci_framework.extensions.stimuli_delivery.utils import Widgets as w
from bci_framework.extensions.stimuli_delivery.utils import Tone as t

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

        self.show_cross()

        self.dashboard <= w.label('Tones', 'headline4', style={'margin-bottom': '15px', 'display': 'flex', })
        self.dashboard <= html.BR()

        self.dashboard <= w.slider('Frequency', min=10, max=22e3, step=1, value=447, id='f', on_change=t.set_note)
        self.dashboard <= w.slider('Gain', min=0, max=1, step=0.1, value=0.5, id='gain', on_change=t.set_gain)

        self.dashboard <= w.button('Start', on_click=lambda: t.start(w.get_value('f'), w.get_value('gain')), style={'margin': '0 15px'})
        self.dashboard <= w.button('Stop', on_click=t.stop, style={'margin': '0 15px'})

        self.dashboard <= w.label('Notes', 'headline4', style={'margin-top': '15px', 'display': 'flex', })

        self.dashboard <= w.select('Note', options=[[n, n] for n in t.note_values], value='D5', id='note')

        self.dashboard <= w.button('Beep(1)', on_click=lambda: self.beep(1), style={'margin': '0 15px'})
        self.dashboard <= w.button('Beep(2)', on_click=lambda: self.beep(2), style={'margin': '0 15px'})
        self.dashboard <= w.button('Beep(3)', on_click=lambda: self.beep(3), style={'margin': '0 15px'})
        self.dashboard <= w.button('Beep(4)', on_click=lambda: self.beep(4), style={'margin': '0 15px'})

    # ----------------------------------------------------------------------
    def beep(self, n):
        """"""
        note = w.get_value('note')
        gain = w.get_value('gain')
        duration = 100

        t(note, duration, gain)

        if n > 1:
            for i in range(1, n):
                timer.set_timeout(lambda: t(note, duration, gain), (duration + 50) * i)

if __name__ == '__main__':
    TonesExample()


