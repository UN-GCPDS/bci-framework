import os
from ...subprocess_script import LoadSubprocess
import socket
# import logging


########################################################################
class StimuliDelivery:
    """"""
    # ----------------------------------------------------------------------

    def __init__(self, core):
        """Constructor"""

        self.parent_frame = core.main
        self.core = core

        self.update_experiments_list()

    # ----------------------------------------------------------------------
    def update_experiments_list(self):
        """"""
        for i in range(self.parent_frame.listWidget_projects.count()):
            item = self.parent_frame.listWidget_projects.item(i)
            if item.icon_name == 'icon_sti':
                self.parent_frame.comboBox_load_experiment.addItem(item.text())

        self.parent_frame.comboBox_load_experiment.activated.connect(lambda evt: self.load_experiment(
            self.parent_frame.comboBox_load_experiment.currentText()))

    # ----------------------------------------------------------------------
    def load_experiment(self, experiment):
        """"""
        module = os.path.join('default_projects', experiment, 'main.py')
        self.preview_stream = LoadSubprocess(
            self.parent_frame, module, debug=False, web_view='gridLayout_stimuli_webview', endpoint='delivery')

        self.parent_frame.lineEdit_stimuli_ip.setText(
            f'{self.get_local_ip_address()}:{self.preview_stream.port}')

    # ----------------------------------------------------------------------
    def get_local_ip_address(self):
        """Connect to internet for get the local IP."""
        try:
            local_ip_address = socket.gethostbyname(socket.gethostname())
            return local_ip_address
        except:
            return 'localhost'

