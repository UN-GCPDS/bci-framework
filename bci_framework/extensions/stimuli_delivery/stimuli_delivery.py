"""
================
Stimuli Delivery
================

The stimuli delivery consist in a reimplementation of `Brython-Radiant
<https://radiant-framework.readthedocs.io/en/latest/>`_ with some renames and a
preconfigured server.
"""

import os
import sys

from radiant.server import RadiantAPI, RadiantServer, RadiantHandler

if len(sys.argv) > 1:
    port = sys.argv[1]
else:
    port = '5000'


########################################################################
class _delivery_instance:
    """This class make compatible the functional decorators defined with Brython."""
    # ---------------------------------------------------------------------
    @staticmethod
    def no_sense_decorator(method):
        return method

    both = no_sense_decorator
    rboth = no_sense_decorator
    remote = no_sense_decorator
    local = no_sense_decorator
    event = no_sense_decorator


DeliveryInstance = _delivery_instance()


########################################################################
class StimuliAPI(RadiantAPI):
    """Rename Randiant with a arand new class."""

    # ---------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# ----------------------------------------------------------------------
def StimuliServer(class_, *args, **kwargs):
    """Rename `RadiantServer` with a preconfigured `StimuliServer`."""
    return RadiantServer(class_,
                         path=os.path.realpath(os.path.join(
                             os.path.dirname(__file__), 'path')),
                         handlers=([r'^/ws', (os.path.realpath(os.path.join(os.path.dirname(__file__), 'tornado_handlers.py')), 'WSHandler'), {}],
                                   [r'^/dashboard', RadiantHandler,
                                       {'mode': 'dashboard', }],
                                   [r'^/mode', (os.path.realpath(os.path.join(os.path.dirname(
                                       __file__), 'tornado_handlers.py')), 'ModeHandler'), {}],
                                   ),
                         template=os.path.realpath(os.path.join(
                             os.path.dirname(__file__), 'template.html')),
                         environ={'port': port,
                                  'mode': 'stimuli',
                                  },
                         port=port,
                         host='0.0.0.0',
                         theme=os.path.realpath(os.path.join(
                             os.path.dirname(__file__), 'colors.xml')),
                         )

