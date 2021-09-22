import os
import sys
import json
from ...extensions import properties as prop
from typing import Callable

from gcpds.filters import frequency as flt

import numpy as np

notch_filters = ('none', '50 Hz', '60 Hz')
bandpass_filters = ('none', 'delta', 'theta', 'alpha', 'beta',
                    '5-45 Hz', '3-30 Hz', '4-40 Hz', '2-45 Hz', '1-50 Hz',
                    '7-13 Hz', '15-50 Hz', '1-100 Hz', '5-50 Hz',)
scale = ('50 µV', '100 µV', '200 µV', '400 µV', '800 µV', '1000 µV')
channels = ['All'] + list(prop.CHANNELS.values())
substract = ('none', 'channel mean', 'global mean', 'Cz')
window_time = ('30 s', '15 s', '10 s', '1 s')


#  Create interact file with custom widgets
if os.path.exists(os.path.join(sys.path[0], 'interact')):
    os.remove(os.path.join(sys.path[0], 'interact'))


# ----------------------------------------------------------------------
def interact(*topics, exclusive=True) -> Callable:
    """"""

    with open(os.path.join(sys.path[0], 'interact'), 'a+') as file:

        if len(topics) == 3:
            extra = [topics[-1]]
        else:
            extra = []
        file.write(json.dumps(list(topics) + extra + [exclusive]) + '\n')

    def wrap_wrap(fn: Callable) -> Callable:

        def wrap(cls, *args, **kwargs):
            cls.interact[topics[0].lower().replace(' ', '_')] = topics[2]
            fn(*([cls] + list(args)), **kwargs)
        return wrap
    return wrap_wrap


########################################################################
class Filters:
    """"""
    # ----------------------------------------------------------------------
    @interact('BandPass', bandpass_filters, 'none')
    def interact_bandpass(self, bandpass):
        """"""
        if bandpass == 'none':
            self.remove_transformers(['bandpass'])
        elif bandpass in ['delta', 'theta', 'alpha', 'beta']:
            bandpass = getattr(flt, bandpass)
            self.add_transformers(
                {'bandpass': (bandpass, {'fs': prop.SAMPLE_RATE})})
        else:
            bandpass = bandpass.replace(' Hz', '').replace('-', '')
            bandpass = getattr(flt, f'band{bandpass}')
            self.add_transformers(
                {'bandpass': (bandpass, {'fs': prop.SAMPLE_RATE})})

    # ----------------------------------------------------------------------
    @interact('Notch', notch_filters, 'none')
    def interact_notch(self, notch):
        """"""
        if notch == 'none':
            self.remove_transformers(['notch'])
        else:
            notch = notch.replace(' Hz', '')
            notch = getattr(flt, f'notch{notch}')
            self.add_transformers(
                {'notch': (notch, {'fs': prop.SAMPLE_RATE})})

    # ----------------------------------------------------------------------
    @interact('Scale', scale, '100 µV', 100)
    def interact_scale(self, scale):
        """"""
        scale = int(scale.replace(' µV', ''))
        self.axis.set_ylim(-scale, scale * len(prop.CHANNELS))
        self.axis.set_yticks(np.linspace(
            0, (len(prop.CHANNELS) - 1) * scale, len(prop.CHANNELS)))
        self.interact['scale'] = scale


########################################################################
class Channels:
    """"""

    # ----------------------------------------------------------------------
    @interact('Channels', channels, 'All', exclusive=False)
    def interact_channels(self, channels):
        """"""
        channels = channels.split(',')
        self.interact['channels'] = [
            k - 1 for k in prop.CHANNELS if prop.CHANNELS[k] in channels]

        if not self.interact['channels']:
            self.interact['channels'] = 'All'


########################################################################
class Substract:
    """"""

    # ----------------------------------------------------------------------
    @interact('Substract', substract, 'none')
    def interact_substract(self, substract):
        """"""
        self.interact['substract'] = substract


########################################################################
class WindowTime:
    """"""

    # ----------------------------------------------------------------------
    @interact('Window time', window_time, '30 s', 30)
    def interact_window_time(self, window_time):
        """"""
        self.interact['window_time'] = int(window_time.replace(' s', ''))
