"""
Properties
==========
"""
import json
import os

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
    #----------------------------------------------------------------------
    def __getattr__(self, attr):
        """Add the prefix to environ variable and try to get it."""
        if prop := os.environ.get(f"BCISTREAM_{attr}", None):
            return json.loads(prop)
        else:
            return None


properties = Properties()