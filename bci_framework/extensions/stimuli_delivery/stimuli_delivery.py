import os
import sys

from radiant.server import RadiantAPI, RadiantServer, RadiantHandler

if len(sys.argv) > 1:
    port = sys.argv[1]
else:
    port = '5000'


########################################################################
class DeliveryInstance_:
    """"""
    # ---------------------------------------------------------------------
    @staticmethod
    def no_sense_decorator(method):
        return method

    both = no_sense_decorator
    rboth = no_sense_decorator
    remote = no_sense_decorator
    local = no_sense_decorator
    event = no_sense_decorator


DeliveryInstance = DeliveryInstance_()


########################################################################
class StimuliAPI(RadiantAPI):
    """"""

    # ---------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)


# ----------------------------------------------------------------------
def StimuliServer(class_, *args, **kwargs):
    """"""
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

