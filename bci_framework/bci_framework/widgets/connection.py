import os
from ..dialogs import Dialogs
from openbci_stream.acquisition import Cyton, CytonBase
import json
import time
import logging
import sys


import pickle

from ...extensions import properties as prop

# from ..config_manager import C
# from PySide2.QtUiTools import QUiLoader
# from PySide2.QtCore import QTimer
# from PySide2.QtGui import QMovie

# from contextlib import contextmanager
# from PyQt4 import QtCore
# from PyQt4.QtGui import QApplication, QCursor

from PySide2 import QtCore

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication
from PySide2.QtGui import QCursor


from kafka import KafkaConsumer, KafkaProducer
from datetime import datetime


########################################################################
class OpenBCIThread(QtCore.QThread):
    """"""
    over = QtCore.Signal(object)

    # ----------------------------------------------------------------------
    def stop(self):
        """"""
        self.terminate()

    # ----------------------------------------------------------------------
    def run(self):
        """"""


########################################################################
class Connection:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, core):
        """Constructor"""
        self.parent_frame = core.main
        self.core = core

        # self.parent.pushButton_disconnect.hide()

        self.config = {
            'mode': self.parent_frame.comboBox_connection_mode,
            'port': self.parent_frame.comboBox_port,
            'ip': self.parent_frame.comboBox_ip,
            'host': self.parent_frame.comboBox_host,
            'acquisition_sample_rate': self.parent_frame.comboBox_sample_rate,
            'streaming_sample_rate': self.parent_frame.comboBox_streaming_sample_rate,
            'boardmode': self.parent_frame.comboBox_boardmode,
            'gain': self.parent_frame.comboBox_gain,
            'input_type': self.parent_frame.comboBox_input_type,
            'bias': self.parent_frame.comboBox_bias,
            'srb1': self.parent_frame.comboBox_srb1,
            'srb2': self.parent_frame.comboBox_srb2,
            'pchan': self.parent_frame.comboBox_pchan,
            'nchan': self.parent_frame.comboBox_nchan,
            'test_signal_type': self.parent_frame.comboBox_test_signal,
            'test_signal': self.parent_frame.checkBox_test_signal,

        }

        self.load_config()
        self.update_connections()
        self.update_environ()
        self.connect()
        self.core.config.connect_widgets(self.update_config, self.config)

    # ----------------------------------------------------------------------
    def load_config(self):
        """"""
        self.core.config.load_widgets('connection', self.config)
        self.core.update_kafka(self.parent_frame.comboBox_host.currentText())

    # ----------------------------------------------------------------------
    def update_config(self, *args, **kwargs):
        """"""
        self.core.config.save_widgets('connection', self.config)

    # ----------------------------------------------------------------------
    def connect(self):
        """"""
        self.parent_frame.pushButton_connect.clicked.connect(self.on_connect)
        self.parent_frame.comboBox_connection_mode.activated.connect(
            self.update_connections)

    # ----------------------------------------------------------------------
    def update_connections(self):
        """"""
        if 'serial' in self.parent_frame.comboBox_connection_mode.currentText().lower():

            for index in range(1, self.parent_frame.comboBox_sample_rate.count()):
                self.parent_frame.comboBox_sample_rate.model().item(index).setEnabled(False)
            if self.parent_frame.comboBox_sample_rate.currentIndex() >= 1:
                self.parent_frame.comboBox_sample_rate.setCurrentIndex(0)

            for index in range(3, self.parent_frame.comboBox_streaming_sample_rate.count()):
                self.parent_frame.comboBox_streaming_sample_rate.model().item(
                    index).setEnabled(False)
            if self.parent_frame.comboBox_streaming_sample_rate.currentIndex() >= 3:
                self.parent_frame.comboBox_streaming_sample_rate.setCurrentIndex(
                    2)

            self.parent_frame.label_port_ip.setText('Port')
            self.parent_frame.comboBox_ip.hide()
            self.parent_frame.comboBox_port.show()

        else:

            for index in range(1, self.parent_frame.comboBox_sample_rate.count()):
                self.parent_frame.comboBox_sample_rate.model().item(index).setEnabled(True)

            for index in range(3, self.parent_frame.comboBox_streaming_sample_rate.count()):
                self.parent_frame.comboBox_streaming_sample_rate.model().item(index).setEnabled(True)

            self.parent_frame.label_port_ip.setText('IP')
            self.parent_frame.comboBox_ip.show()
            self.parent_frame.comboBox_port.hide()

    # # ----------------------------------------------------------------------

    # def show_dialog_connection(self):
        # """"""
        # self.dialog_conection = QUiLoader().load('bci_framework/qtgui/connecting.ui', self.parent)

        # movie = QMovie(':/bci/icons/bci/connecting.gif')
        # movie.start()
        # self.dialog_conection.label_gif.setMovie(movie)

        # self.dialog_conection.show()

    # ----------------------------------------------------------------------
    def handle_exception(self):
        """"""
        checks = []

        if 'serial' in self.parent_frame.comboBox_connection_mode.currentText().lower():
            checks.extend(['* Check that USB dongle were connected',
                           '* Verify serial permissions',
                           ])

        if self.parent_frame.comboBox_host.currentText() != 'localhost':
            checks.extend([f'* The server could not be running, or running on a different IP that {self.parent_frame.comboBox_host.currentText()}',
                           '* This machine must have access to the server or running on the same network.',
                           ])
        # else:
            # checks.extend([f'* Verify that Kafka is running on this machine',
                           # ])

        if hasattr(self.core, 'conection_message'):
            checks.extend([self.core.conection_message])
            self.core.conection_message = ""
        checks = '\n'.join(checks)
        Dialogs.critical_message(self.parent_frame, 'Connection error', f"{checks}")

    # ----------------------------------------------------------------------
    def on_connect(self, toggled):
        """"""
        if toggled:  # Connect
            QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
            self.core.update_kafka(self.parent_frame.comboBox_host.currentText())
            if '--debug' in sys.argv:
                self.openbci_connect()
            else:
                try:
                    self.openbci_connect()
                    QApplication.restoreOverrideCursor()
                except:
                    QApplication.restoreOverrideCursor()
                    self.core.status_bar(message='')
                    self.handle_exception()
                    self.on_connect(False)

        else:   # Disconnect

            try:
                self.openbci.stop_stream()
            except:
                pass
            try:
                del self.openbci
            except:
                pass
            self.core.stop_kafka()

            if self.parent_frame.checkBox_test_signal.isChecked():
                self.parent_frame.groupBox_settings.setEnabled(False)
                self.parent_frame.groupBox_leadoff_impedance.setEnabled(False)

            self.parent_frame.pushButton_connect.setText('Connect')
            self.parent_frame.pushButton_connect.setChecked(False)
            self.core.status_bar(right_message=('Disconnected', None))
            self.parent_frame.checkBox_view_impedances.setChecked(False)
            self.parent_frame.stackedWidget_montage.setCurrentIndex(0)

    # ----------------------------------------------------------------------

    def openbci_connect(self):
        """"""
        if 'serial' in self.parent_frame.comboBox_connection_mode.currentText().lower():
            mode = 'serial'
            endpoint = self.parent_frame.comboBox_port.currentText()
            os.environ['BCISTREAM_CONNECTION'] = json.dumps('serial')
        else:
            mode = 'wifi'
            endpoint = self.parent_frame.comboBox_ip.currentText()
            os.environ['BCISTREAM_CONNECTION'] = json.dumps('wifi')

        host = self.parent_frame.comboBox_host.currentText()

        sample_rate = self.parent_frame.comboBox_sample_rate.currentText()
        sample_rate = getattr(CytonBase, f"SAMPLE_RATE_{sample_rate}SPS")

        streaming_sample_rate = self.parent_frame.comboBox_streaming_sample_rate.currentText()

        boardmode = self.parent_frame.comboBox_boardmode.currentText()
        boardmode = getattr(CytonBase, f"BOARD_MODE_{boardmode}")

        gain = self.parent_frame.comboBox_gain.currentText()
        gain = getattr(CytonBase, f'GAIN_{gain}')

        adsinput = self.parent_frame.comboBox_input_type.currentText()
        adsinput = getattr(CytonBase, f'ADSINPUT_{adsinput}')

        bias = self.parent_frame.comboBox_bias.currentText()
        bias = getattr(CytonBase, f"BIAS_{bias}")

        srb1 = self.parent_frame.comboBox_srb1.currentText()
        srb1 = getattr(CytonBase, f'SRB1_{srb1}')

        srb2 = self.parent_frame.comboBox_srb2.currentText()
        srb2 = getattr(CytonBase, f'SRB2_{srb2}')

        pchan = self.parent_frame.comboBox_pchan.currentText()
        pchan = getattr(CytonBase, pchan.replace(' ', '_'))

        nchan = self.parent_frame.comboBox_nchan.currentText()
        nchan = getattr(CytonBase, nchan.replace(' ', '_'))

        channels = self.core.montage.get_montage()

        # Connect
        self.openbci = Cyton(mode, endpoint, host=host, capture_stream=False,
                             daisy=prop.DAISY, montage=channels, streaming_package_size=int(streaming_sample_rate))
        self.openbci.command(sample_rate)

        # Some time this command not take effect
        boardmode_setted = False
        for _ in range(10):
            response = self.openbci.command(boardmode)
            if response and b'Success' in response:
                logging.info(f'Bardmode setted in {boardmode} mode')
                boardmode_setted = True
                break
            time.sleep(0.1)

        self.boardmode = self.openbci.boardmode
        if not boardmode_setted:
            logging.warning('Boardmode not setted!')
            # Dialogs.warning_message(
                # self.parent_frame, 'Boardmode', f'Boardmode could no be setted correctly.\n{self.boardmode}')
            self.parent_frame.comboBox_boardmode.setCurrentText(
                self.boardmode.capitalize())

        self.session_settings(channels, bias, gain, srb1, adsinput, srb2)

        if not self.parent_frame.checkBox_send_leadoff.isChecked():
            self.openbci.leadoff_impedance(
                channels, pchan=pchan, nchan=nchan)

        if self.parent_frame.checkBox_test_signal.isChecked():
            test_signal = self.parent_frame.comboBox_test_signal.currentText()
            test_signal = getattr(
                CytonBase, f"TEST_{test_signal.replace(' ', '_')}")
            self.openbci.command(test_signal)

            self.core.status_bar(message=f'OpenBCI connected on test mode ({test_signal}) to {endpoint} running in {host}')

        else:
            all_channels = set(range(16 if prop.DAISY else 8))
            used_channels = set(channels.keys())
            deactivated = all_channels.difference(used_channels)
            self.openbci.deactivate_channel(deactivated)
            self.openbci.activate_channel(used_channels)

            self.core.status_bar(message=f'OpenBCI connected and streaming in {self.boardmode} mode to {endpoint} running in {host}')

        self.openbci.start_stream()

        self.parent_frame.pushButton_connect.setText('Disconnect')
        self.update_environ()

    # ----------------------------------------------------------------------
    def session_settings(self, *args):
        """"""
        if hasattr(self, 'last_settings'):
            channels, bias, gain, srb1, adsinput, srb2 = self.last_settings
        elif args:
            self.last_settings = args
            channels, bias, gain, srb1, adsinput, srb2 = args
        else:
            return

        if self.parent_frame.checkBox_default_settings.isChecked():
            self.openbci.command(self.openbci.DEFAULT_CHANNELS_SETTINGS)
        else:
            self.openbci.channel_settings(channels, power_down=CytonBase.POWER_DOWN_ON,
                                          gain=gain,
                                          input_type=adsinput,
                                          bias=bias,
                                          srb2=srb2,
                                          srb1=srb1)

    # # ----------------------------------------------------------------------
    # def openbci_disconnect(self):
        # """"""
        # # self.openbci.
        # if self.parent_frame.checkBox_test_signal.isChecked():
            # self.parent_frame.groupBox_settings.setEnabled(False)
            # self.parent_frame.groupBox_leadoff_impedance.setEnabled(False)
        # try:
            # self.openbci.stop_stream()
        # except:
            # pass
        # self.parent_frame.pushButton_connect.setText('Connect')
        # self.parent_frame.pushButton_connect.setChecked(False)
        # self.core.status_bar(right_message=('Disconnect', None))

    # ----------------------------------------------------------------------
    def update_environ(self):
        """"""
        os.environ['BCISTREAM_HOST'] = json.dumps(
            self.parent_frame.comboBox_host.currentText())

        sps = self.parent_frame.comboBox_sample_rate.currentText()
        if 'k' in sps.lower():
            sps = int(sps.lower().replace('k', '')) * 1000
        else:
            sps = int(sps)
        os.environ['BCISTREAM_SAMPLE_RATE'] = json.dumps(sps)
        os.environ['BCISTREAM_STREAMING_PACKAGE_SIZE'] = json.dumps(
            int(self.parent_frame.comboBox_streaming_sample_rate.currentText()))

        os.environ['BCISTREAM_BOARDMODE'] = json.dumps(
            self.parent_frame.comboBox_boardmode.currentText().lower())
