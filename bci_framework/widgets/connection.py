import json

from openbci_stream.acquisition import Cyton, CytonBase
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QTimer
from PySide2.QtGui import QMovie

import os

########################################################################


class Connection:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, parent, core):
        """Constructor"""
        self.parent = parent
        self.core = core

        # self.parent.pushButton_disconnect.hide()

        self.update_connections()
        self.update_environ()
        self.connect()

    # ----------------------------------------------------------------------

    def connect(self):
        """"""
        # self.parent.pushButton_connect.clicked.connect(self.show_dialog_connection)
        self.parent.pushButton_connect.clicked.connect(self.openbci_connect)
        # self.parent.pushButton_disconnect.clicked.connect(self.openbci_disconnect)
        self.parent.comboBox_connection_mode.activated.connect(self.update_connections)

    # ----------------------------------------------------------------------

    def update_connections(self):
        """"""
        if 'serial' in self.parent.comboBox_connection_mode.currentText().lower():

            for index in range(1, self.parent.comboBox_sample_rate.count()):
                self.parent.comboBox_sample_rate.model().item(index).setEnabled(False)
            if self.parent.comboBox_sample_rate.currentIndex() >= 1:
                self.parent.comboBox_sample_rate.setCurrentIndex(0)

            for index in range(3, self.parent.comboBox_streaming_sample_rate.count()):
                self.parent.comboBox_streaming_sample_rate.model().item(index).setEnabled(False)
            if self.parent.comboBox_streaming_sample_rate.currentIndex() >= 3:
                self.parent.comboBox_streaming_sample_rate.setCurrentIndex(2)

            self.parent.label_port_ip.setText('Port')
            self.parent.comboBox_ip.hide()
            self.parent.comboBox_port.show()

        else:

            for index in range(1, self.parent.comboBox_sample_rate.count()):
                self.parent.comboBox_sample_rate.model().item(index).setEnabled(True)

            for index in range(3, self.parent.comboBox_streaming_sample_rate.count()):
                self.parent.comboBox_streaming_sample_rate.model().item(index).setEnabled(True)

            self.parent.label_port_ip.setText('IP')
            self.parent.comboBox_ip.show()
            self.parent.comboBox_port.hide()

    # # ----------------------------------------------------------------------

    # def show_dialog_connection(self):
        # """"""
        # self.dialog_conection = QUiLoader().load('bci_framework/qtgui/connecting.ui', self.parent)

        # movie = QMovie(':/bci/icons/bci/connecting.gif')
        # movie.start()
        # self.dialog_conection.label_gif.setMovie(movie)

        # self.dialog_conection.show()

    # ----------------------------------------------------------------------
    def on_connect(self, toggled):
        """"""
        if toggled:
            self.openbci_connect(toggled)
        else:
            self.openbci_disconnect()

    # ----------------------------------------------------------------------
    def openbci_connect(self):
        """"""
        # dialog_conection.update()

        if 'serial' in self.parent.comboBox_connection_mode.currentText().lower():
            mode = 'serial'
            endpoint = self.parent.comboBox_port.currentText()
        else:
            mode = 'wifi'
            endpoint = self.parent.comboBox_ip.currentText()

        host = self.parent.comboBox_host.currentText()

        sample_rate = self.parent.comboBox_sample_rate.currentText()
        sample_rate = getattr(CytonBase, f"SAMPLE_RATE_{sample_rate}SPS")

        streaming_sample_rate = self.parent.comboBox_streaming_sample_rate.currentText()

        boardmode = self.parent.comboBox_boardmode.currentText()
        boardmode = getattr(CytonBase, f"BOARD_MODE_{boardmode}")

        gain = self.parent.comboBox_gain.currentText()
        gain = getattr(CytonBase, f'GAIN_{gain}')

        adsinput = self.parent.comboBox_input_type.currentText()
        adsinput = getattr(CytonBase, f'ADSINPUT_{adsinput}')

        bias = self.parent.comboBox_bias.currentText()
        bias = getattr(CytonBase, f"BIAS_{bias}")

        srb1 = self.parent.comboBox_srb1.currentText()
        srb1 = getattr(CytonBase, f'SRB1_{srb1}')

        srb2 = self.parent.comboBox_srb2.currentText()
        srb2 = getattr(CytonBase, f'SRB2_{srb2}')

        pchan = self.parent.comboBox_pchan.currentText()
        pchan = getattr(CytonBase, pchan.replace(' ', '_'))

        nchan = self.parent.comboBox_nchan.currentText()
        nchan = getattr(CytonBase, nchan.replace(' ', '_'))

        channels = self.core.montage.get_montage()
        daisy = max(channels.keys()) > 8

        # import time
        # self.dialog_conection.label_laptop.setEnabled(True)

        self.openbci = Cyton(mode, endpoint, host=host, capture_stream=False, daisy=daisy, montage=channels, stream_samples=int(streaming_sample_rate))
        # self.dialog_conection.plainTextEdit.insertPlainText("\nCalling Cyton")

        self.openbci.command(sample_rate)
        # self.dialog_conection.plainTextEdit.insertPlainText("\nSample rate")

        self.openbci.leadoff_impedance(channels, pchan=pchan, nchan=nchan)
        # self.dialog_conection.plainTextEdit.insertPlainText("\LeadOff impedance")
        self.openbci.channel_settings(channels, power_down=CytonBase.POWER_DOWN_ON,
                                      gain=gain,
                                      input_type=adsinput,
                                      bias=bias,
                                      srb2=srb2,
                                      srb1=srb1)
        # self.dialog_conection.plainTextEdit.insertPlainText("\nSettings")

        # self.dialog_conection.label_openbci.setEnabled(True)

        # self.parent.pushButton_disconnect.show()
        self.parent.pushButton_connect.setText('Disconnect')

        self.update_environ()

    # ----------------------------------------------------------------------
    def openbci_disconnect(self):
        """"""
        # self.openbci.
        self.parent.pushButton_connect.setText('Connect')

    # ----------------------------------------------------------------------
    def update_environ(self):
        """"""
        os.environ['BCISTREAM_HOST'] = json.dumps(self.parent.comboBox_host.currentText())

        sps = self.parent.comboBox_sample_rate.currentText()
        if 'k' in sps.lower():
            sps = int(sps.lower().replace('k', '')) * 1000
        else:
            sps = int(sps)
        os.environ['BCISTREAM_SAMPLE_RATE'] = json.dumps(sps)

