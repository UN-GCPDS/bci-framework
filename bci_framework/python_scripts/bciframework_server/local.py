from radiant import PythonHandler
import os


########################################################################
class LocalInterpreter(PythonHandler):
    """"""

    # ----------------------------------------------------------------------
    def get_url(self):
        """"""
        file = os.path.expanduser(os.path.join(
            '~/', '.bciframework', 'stimuli.ip'))
        with open(file, 'r') as file:
            return file.read()
