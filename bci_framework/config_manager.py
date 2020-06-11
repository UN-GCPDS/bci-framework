from configparser import ConfigParser
import os
import shutil

########################################################################
class ConfigManager(ConfigParser):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, filename='.bciframework'):
        """Constructor"""
        super().__init__()

        self.filename = os.path.abspath(filename)
        self.load()

    #----------------------------------------------------------------------
    def load(self):
        """"""
        # if os.path.exists(self.filename):
            # self.read(self.filename)
        # else:
        shutil.copyfile('bciframework.default', '.bciframework')
        self.read(self.filename)


    #----------------------------------------------------------------------
    def save(self):
        """"""
        with open(self.filename, 'w') as configfile:
            self.write(configfile)

