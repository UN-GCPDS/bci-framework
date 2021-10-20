"""
==========
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
    # print('WARNING - USING CUSTOM PROPERTIES')
    # HOST = '192.168.1.1'
    # CHANNELS = {i + 1: f'ch-{i+1}' for i in range(32)}
    # SAMPLE_RATE = 1000
    # STREAMING_PACKAGE_SIZE = 100
    # BOARDMODE = 'default'
    # CONNECTION = 'wifi'
    # SYNCLATENCY = 0
    # OFFSET = 0
    # DAISY = [True]

    # ----------------------------------------------------------------------
    def __getattr__(self, attr: str):
        """Add the prefix to environ variable and try to get it."""
        if prop := os.environ.get(f"BCISTREAM_{attr}", None):
            p = json.loads(prop)
            if attr == 'CHANNELS':
                p = {int(k): p[k] for k in p}
            return p
        else:
            logging.warning(
                f'{attr} not found, it must be defined in the environ as BCISTREAM_{attr}')
            return None


properties = Properties()
