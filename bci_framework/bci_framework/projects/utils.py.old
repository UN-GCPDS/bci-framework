from flask import request
from bci_framework.projects import properties as _prop
from kafka import KafkaProducer
import json
import logging


########################################################################
class BCIUtils:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

        try:
            self.marker_producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                                                 compression_type='gzip',)
        except:
            logging.warning("Kafka: NoBrokersAvailable")

    # ----------------------------------------------------------------------
    def _system_python(self):
        """"""
        name = f'_bci_{request.form["name"]}'
        try:
            args = eval(request.form['args'])
        except:
            args = ()
        kwargs = json.loads(request.form['kwargs'])

        if hasattr(self, name):
            return getattr(self, name)(*args, **kwargs)

        return json.dumps({'__RDNT__': False})

    # ----------------------------------------------------------------------

    def _bci_test(self, *args, **kwargs):
        """"""
        return json.dumps({'__RDNT__': True})

    # ----------------------------------------------------------------------
    def _bci_properties(self, attr):
        """"""
        return json.dumps({'__RDNT__': _prop.__getattr__(attr)})




