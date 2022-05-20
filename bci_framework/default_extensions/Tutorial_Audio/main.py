from bci_framework.extensions.stimuli_delivery import StimuliAPI
from bci_framework.extensions.stimuli_delivery.utils import Widgets as w
from bci_framework.extensions.stimuli_delivery.utils import Audio as a
from browser import html, timer


########################################################################
class AudioExample(StimuliAPI):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)

        self.show_cross()
        
        a.load('rain.wav')

        self.dashboard <= w.label('Audio', 'headline4', style={'margin-bottom': '15px', 'display': 'flex', })
        self.dashboard <= html.BR()

        self.dashboard <= w.slider('Gain', min=0, max=1, step=0.1, value=0.5, id='gain', on_change=a.set_gain)

        self.dashboard <= w.button('Start', on_click=a.play, style={'margin': '0 15px'})
        self.dashboard <= w.button('Stop', on_click=a.stop, style={'margin': '0 15px'})

if __name__ == '__main__':
    AudioExample()


