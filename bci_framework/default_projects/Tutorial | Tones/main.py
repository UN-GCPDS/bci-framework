from bci_framework.projects.server import StimuliAPI, StimuliServer
from bci_framework.projects import Tone, Widgets
# from bci_framework.projects import properties as prop
# from bci_framework.projects.utils import timeit

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
class Tones(StimuliAPI):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """"""
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
        self.dashboard <= self.widgets.title('Tones', 'headline4', style={'margin-bottom': '15px', 'display': 'flex', })
        self.dashboard <= html.BR()

        self.dashboard <= self.widgets.slider('Frequency', min=10, max=22e3, step=1, valuenow=447, id='f', on_change=self.tone.set_note)
        self.dashboard <= self.widgets.slider('Gain', min=0, max=1, step=0.1, valuenow=0.5, id='gain', on_change=self.tone.set_gain)
        
        self.dashboard <= self.widgets.button('Start', connect=lambda: self.tone.start(self.widgets.get_value('f'), self.widgets.get_value('gain')), style={'margin': '0 15px'})
        self.dashboard <= self.widgets.button('Stop', connect=self.tone.stop, style={'margin': '0 15px'})

    
        self.dashboard <= self.widgets.title('Notes', 'headline4', style={'margin-top': '15px', 'display': 'flex', })

        self.dashboard <= self.widgets.combobox('Note', options=[[n,n] for n in self.tone.note_values], valuenow='D5', id='note')


        self.dashboard <= self.widgets.button('Beep(1)', connect=lambda: self.beep(1), style={'margin': '0 15px'})
        self.dashboard <= self.widgets.button('Beep(2)', connect=lambda: self.beep(2), style={'margin': '0 15px'})
        self.dashboard <= self.widgets.button('Beep(3)', connect=lambda: self.beep(3), style={'margin': '0 15px'})
        self.dashboard <= self.widgets.button('Beep(4)', connect=lambda: self.beep(4), style={'margin': '0 15px'})


    # ----------------------------------------------------------------------
    def beep(self, n):
        """"""
        note = self.widgets.get_value('note')
        gain = self.widgets.get_value('gain')
        duration = 100
        
        self.tone(note, duration)
        
        if n>1:
            for i in range(1, n):
                timer.set_timeout(lambda :self.tone(note, duration, gain), (duration+50)*i)
            
        


    if __name__ == '__main__':
        StimuliServer('Tones')


