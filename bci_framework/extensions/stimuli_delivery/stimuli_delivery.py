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
import logging
import json
import socket

from radiant.server import RadiantAPI, RadiantServer, RadiantHandler


try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip_address = s.getsockname()[0]
    s.close()
    ip = local_ip_address

except:
    ip = 'localhost'

if len(sys.argv) > 1 and sys.argv[1].isdecimal():
    port = sys.argv[1]
else:
    port = '5000'

debug = '--debug' in sys.argv

logging.root.name = "StimuliDelivery:Python"
logging.getLogger().setLevel(logging.WARNING)


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
    def __new__(self):
        """"""
        StimuliServer(self.__name__)


# ----------------------------------------------------------------------
def StimuliServer(class_, *args, **kwargs):
    """Rename `RadiantServer` with a preconfigured `StimuliServer`."""

    # brython_environ = {k: os.environ[k] for k in os.environ if k.startswith('BCISTREAM_')}
    brython_environ = {k: os.environ.get(k) for k in dict(
        os.environ) if k.startswith('BCISTREAM_')}
    environ = {'port': port,
               'ip': ip,
               'mode': 'stimuli',
               'debug': debug,
               'brython_environ': str(brython_environ),
               }

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
                         environ=environ,
                         port=port,
                         host='0.0.0.0',
                         theme=os.path.realpath(os.path.join(
                             os.path.dirname(__file__), 'colors.xml')),
                         # callbacks=[(os.path.realpath(os.path.join(
                         # os.path.dirname(__file__), 'tornado_handlers.py')), 'consumer')]
                         debug_level=0,
                         brython_version='3.9.1',
                         )

