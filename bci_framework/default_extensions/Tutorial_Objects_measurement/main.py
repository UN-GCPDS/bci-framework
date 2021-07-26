"""
===================
Objects Measurement
===================

The stimuli delivery use a CSS backend, so the units system must be inherited
from them, however, these units are not based on a real representation, so must
be used `u.scale` to draw with the correct unit.

Degrees of visual angle (dva) are a common unit used in neuroscience
experiments designs, are based on the perspective of size, this units needs the
`real DPI` and the distance from monitor.

By default the `dpi` is calculated from the monitor running `BCI-Framework`, it
must be recalculated if a different monitor is used for stimuli delivery.

Example:
```
from bci_framework.extensions.stimuli_delivery.utils import Units as u

real_unit = f"{u.scale(3)}px"
real_unit = f"{u.scale(3, dpi=141)}px"

# Where `d` is `distance from monitor` and `dpi` is the `real monitor DPI`
u(d=1.2, dpi=141) # Define `d` and `dpi` for all calls
u.dva(3)

# Define `d` and `dpi` on each call
u.dva(3, d=1.2, dpi=141)
```

"""

from bci_framework.extensions.stimuli_delivery import StimuliServer, StimuliAPI
from bci_framework.extensions.stimuli_delivery.utils import Widgets as w
from bci_framework.extensions.stimuli_delivery.utils import Units as u
from bci_framework.extensions import properties as prop
import logging

from browser import html, window
from math import tan, radians


########################################################################
class ObjectsMeasurement(StimuliAPI):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_stylesheet('styles.css')

        self.build_areas()

        self.dashboard <= w.button(
            'CSS measures', on_click=self.css_measures)
        self.dashboard <= w.button(
            'Real measures', on_click=self.real_measures)
        self.dashboard <= w.button(
            'DVA measures', on_click=self.dva_measures)

    # ----------------------------------------------------------------------
    def css_measures(self):
        """"""
        self.stimuli_area.clear()
        self.stimuli_area <= html.DIV('3 cm?', style={'width': "3cm",
                                                      'height': "3cm",
                                                      'background-color': '#ed553b',
                                                      })
        self.stimuli_area <= html.DIV('2 in?', style={'width': "2in",
                                                      'height': "2in",
                                                      'background-color': '#f6d55c',
                                                      })

    # ----------------------------------------------------------------------
    def real_measures(self):
        """"""
        self.stimuli_area.clear()
        self.stimuli_area <= html.DIV('3 cm', style={'width': f"{u.scale(3)}cm",
                                                     'height': f"{u.scale(3)}cm",
                                                     'background-color': '#ed553b',
                                                     })
        self.stimuli_area <= html.DIV('2 in', style={'width': f"{u.scale(2)}in",
                                                     'height': f"{u.scale(2)}in",
                                                     'background-color': '#f6d55c',
                                                     })

    # ----------------------------------------------------------------------
    def dva_measures(self):
        """"""
        self.stimuli_area.clear()

        u(dpi=141, d=1.2)
        self.stimuli_area <= html.DIV('3 dva', style={'width': u.dva(3),
                                                      'height': u.dva(3),
                                                      'background-color': '#3caea3',
                                                      })
        self.stimuli_area <= html.DIV('5 dva', style={'width': u.dva(5),
                                                      'height': u.dva(5),
                                                      'background-color': '#20639b',
                                                      })


if __name__ == '__main__':
    StimuliServer('ObjectsMeasurement')


