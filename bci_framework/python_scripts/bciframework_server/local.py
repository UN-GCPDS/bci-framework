from radiant import PythonHandler


########################################################################
class LocalInterpreter(PythonHandler):
    """"""

    # ----------------------------------------------------------------------
    def get_url(self):
        """"""
        with open('/home/yeison/.bciframework/stimuli.ip', 'r') as file:
            return file.read()

