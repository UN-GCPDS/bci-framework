"""
Properties
==========
"""
import json
import os
import logging


########################################################################
class Properties:
    """Simple access to environ values.

    Properties are saved as environ values, this script able to access them
    with a simple syntax, for example, if the environ `BCISTREAM_HOST` contains
    the ip, instead of call `os.environ['BCISTREAM_HOST']` is possible to get
    value simply with `properties.HOST`.

    Example:
    ```
    from bci_framework.projects import properties as prop

    with OpenBCIConsumer(host=prop.HOST) as stream:
        for message in stream:
            ...
    ```
    """

    # HOST = '192.168.1.1'
    # CHANNELS = {f'ch{n}': f'{n}' for n in range(1, 9)}
    # SAMPLE_RATE = 250
    # STREAMING_PACKAGE_SIZE = 250
    # BOARDMODE = 'analog'

    # ----------------------------------------------------------------------
    def __getattr__(self, attr):
        """Add the prefix to environ variable and try to get it."""
        if prop := os.environ.get(f"BCISTREAM_{attr}", None):
            p = json.loads(prop)
            if attr == 'CHANNELS':
                p = {int(k): p[k] for k in p}
            return p
        else:
            logging.warning(f'{attr} not found, it must be defined in the environ as BCISTREAM_{attr}')
            return None


properties = Properties()
