import os
import sys
import json
import logging
from ...extensions import properties as prop
from typing import Callable

from functools import wraps
from gcpds.filters import frequency as flt

import numpy as np

notch_filters = ('none', '50 Hz', '60 Hz')
bandpass_filters = ('none', 'delta', 'theta', 'alpha', 'beta',
                    '5-45 Hz', '3-30 Hz', '4-40 Hz', '2-45 Hz', '1-50 Hz',
                    '7-13 Hz', '15-50 Hz', '1-100 Hz', '5-50 Hz',)
scale = ('50 µV', '100 µV', '200 µV', '400 µV', '800 µV', '1000 µV')
channels = ['All'] + list(prop.CHANNELS.values())
substract = ('none', 'channel mean', 'global mean', 'Cz')

if prop.RASPAD:
    window_time = ('15 s', '10 s', '1 s')
    default_time = 15
else:
    window_time = ('30 s', '15 s', '10 s', '1 s')
    default_time = 30

#  Create interact file with custom widgets
if os.path.exists(os.path.join(sys.path[0], 'interact')):
    os.remove(os.path.join(sys.path[0], 'interact'))


# ----------------------------------------------------------------------
def interact(*topics, exclusive=True) -> Callable:
    """"""

    def wrap_wrap(fn: Callable) -> Callable:

        with open(os.path.join(sys.path[0], 'interact'), 'a+') as file:
            if len(topics) == 3:
                extra = [topics[-1]]
            else:
                extra = []
            file.write(json.dumps(['#'] + list(topics)
                                  + extra + [exclusive]) + '\n')

        def wrap(cls, *args, **kwargs):
            cls.widget_value[topics[0]] = topics[2]
            fn(*([cls] + list(args)), **kwargs)
        return wrap
    return wrap_wrap


########################################################################
class Filters:
    """"""

    # ----------------------------------------------------------------------
    @interact('BandPass', bandpass_filters, '1-100 Hz')
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
    @interact('Notch', notch_filters, '60 Hz')
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
        self.widget_value['Scale'] = scale


########################################################################
class Channels:
    """"""

    # ----------------------------------------------------------------------
    @interact('Channels', channels, 'All', exclusive=False)
    def interact_channels(self, channels):
        """"""
        channels = channels.split(',')
        self.widget_value['Channels'] = [
            k - 1 for k in prop.CHANNELS if prop.CHANNELS[k] in channels]

        if not self.widget_value['Channels']:
            self.widget_value['Channels'] = 'All'


########################################################################
class Substract:
    """"""

    # ----------------------------------------------------------------------
    @interact('Substract', substract, 'channel mean')
    def interact_substract(self, substract):
        """"""
        self.widget_value['Substract'] = substract


########################################################################
class WindowTime:
    """"""

    # ----------------------------------------------------------------------
    @interact('Window time', window_time, f'{default_time} s', default_time)
    def interact_window_time(self, window_time):
        """"""
        self.widget_value['Window time'] = int(window_time.replace(' s', ''))


########################################################################
class Widgets(Filters, Channels, Substract, WindowTime):
    """"""

    # ----------------------------------------------------------------------
    def enable_widgets(self, *widgets):
        """"""
        lines = []
        with open(os.path.join(sys.path[0], 'interact'), 'r') as file:

            for l in file.readlines():
                line = json.loads(l)
                if (line[0] == '#') and (line[1] in widgets):
                    lines.append(json.dumps(line[1:]) + '\n')
                else:
                    lines.append(json.dumps(line) + '\n')

        with open(os.path.join(sys.path[0], 'interact'), 'w') as file:
            file.writelines(lines)



