import os
import json
import time
import logging

from openbci_stream.acquisition import Cyton, CytonBase
from PySide2 import QtCore
from PySide2.QtCore import Qt, Signal, QThread, Slot
from PySide2.QtGui import QCursor
from PySide2.QtWidgets import QApplication

from ..dialogs import Dialogs
from ...extensions import properties as prop


########################################################################
class OpenBCIThread(QThread):
    """"""
    connection_ok = Signal()
    connection_fail = Signal()
    disconnected_ok = Signal()
    connected = False

    # ----------------------------------------------------------------------
    def stop(self):
        """"""
        self.terminate()

    # ----------------------------------------------------------------------
    def run(self):
        """"""
        self.openbci = Cyton(self.mode,
                             self.endpoint,
                             host=self.host,
                             capture_stream=False,
                             daisy=prop.DAISY,
                             montage=self.montage,
                             streaming_package_size=self.streaming_package_size)

        self.openbci.command(self.sample_rate)
        self.openbci.command(self.boardmode)

        # Some time this command not take effect
        boardmode_setted = False
        for _ in range(10):
            response = self.openbci.command(self.boardmode)
            if response and b'Success' in response:
                logging.info(f'Bardmode setted in {self.boardmode} mode')
                boardmode_setted = True
                break
            time.sleep(0.1)

        boardmode = self.openbci.boardmode
        if not boardmode_setted:
            logging.warning('Boardmode not setted!')
        self.session_settings(self.montage, self.bias,
                              self.gain, self.srb1, self.adsinput, self.srb2)

        if not self.checkBox_send_leadoff:
            self.openbci.leadoff_impedance(
                self.montage, pchan=pchan, nchan=nchan)

        if self.checkBox_test_signal:
            test_signal = self.comboBox_test_signal
            test_signal = getattr(
                CytonBase, f"TEST_{test_signal.replace(' ', '_')}")
            self.openbci.command(test_signal)

        else:
            all_channels = set(range(16 if prop.DAISY else 8))
            used_channels = set(self.montage.keys())
            deactivated = all_channels.difference(used_channels)
            self.openbci.deactivate_channel(deactivated)
            self.openbci.activate_channel(used_channels)

        if not self.streaming():
            self.openbci.start_stream()

        self.connected = True
        self.connection_ok.emit()

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

        if self.checkBox_default_settings:
            self.openbci.command(self.openbci.DEFAULT_CHANNELS_SETTINGS)
        else:
            self.openbci.channel_settings(channels, power_down=CytonBase.POWER_DOWN_ON,
                                          gain=gain,
                                          input_type=adsinput,
                                          bias=bias,
                                          srb2=srb2,
                                          srb1=srb1)

    # ----------------------------------------------------------------------
    def disconnect(self):
        """"""
        try:
            self.openbci.stop_stream()
            self.openbci
        except:
            pass
        self.disconnected_ok.emit()
        self.connected = False


########################################################################
class Connection:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, core):
        """Constructor"""
        self.parent_frame = core.main
        self.core = core

        # self.parent.pushButton_disconnect.hide()
        self.openbci = OpenBCIThread()
        self.openbci.streaming = lambda: getattr(self.core, 'streaming', False)

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
    def on_focus(self):
        """"""
        if getattr(self.core, 'streaming', False) and not self.openbci.connected:
            self.parent_frame.pushButton_connect.setEnabled(False)
            self.openbci_connect()

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

    # ----------------------------------------------------------------------
    def on_connect(self, toggled):
        """"""
        if toggled:  # Connect
            QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
            self.core.update_kafka(
                self.parent_frame.comboBox_host.currentText())
            self.openbci_connect()

        else:   # Disconnect
            self.openbci.disconnect()

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

        # self.openbci = OpenBCIThread()
        self.openbci.connection_ok.connect(self.connection_ok)
        self.openbci.connection_fail.connect(self.connection_fail)
        self.openbci.disconnected_ok.connect(self.disconnected_ok)

        self.openbci.mode = mode
        self.openbci.endpoint = endpoint
        self.openbci.host = host
        self.openbci.montage = channels
        self.openbci.streaming_package_size = int(streaming_sample_rate)
        self.openbci.sample_rate = sample_rate
        self.openbci.boardmode = boardmode
        self.openbci.adsinput = adsinput
        self.openbci.bias = bias
        self.openbci.srb1 = srb1
        self.openbci.srb2 = srb2
        self.openbci.pchan = pchan
        self.openbci.nchan = nchan
        self.openbci.gain = gain

        self.openbci.checkBox_send_leadoff = self.parent_frame.checkBox_send_leadoff.isChecked()
        self.openbci.checkBox_test_signal = self.parent_frame.checkBox_test_signal.isChecked()
        self.openbci.comboBox_test_signal = self.parent_frame.comboBox_test_signal.currentText()
        self.openbci.checkBox_default_settings = self.parent_frame.checkBox_default_settings.isChecked()

        self.openbci.start()
        self.parent_frame.pushButton_connect.setText('Connecting...')
        self.parent_frame.pushButton_connect.setEnabled(False)
        self.update_environ()

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

    # ----------------------------------------------------------------------
    @Slot()
    def connection_ok(self):
        """"""
        QApplication.restoreOverrideCursor()
        self.parent_frame.pushButton_connect.setText('Disconnect')
        self.parent_frame.pushButton_connect.setEnabled(True)

    # ----------------------------------------------------------------------
    @Slot()
    def connection_fail(self):
        """"""
        QApplication.restoreOverrideCursor()

        checks = []

        if 'serial' in self.parent_frame.comboBox_connection_mode.currentText().lower():
            checks.extend(['* Check that USB dongle were connected',
                           '* Verify serial permissions',
                           ])

        if self.parent_frame.comboBox_host.currentText() != 'localhost':
            checks.extend([f'* The server could not be running, or running on a different IP that {self.parent_frame.comboBox_host.currentText()}',
                           '* This machine must have access to the server or running on the same network.',
                           ])

        if hasattr(self.core, 'conection_message'):
            checks.extend([self.core.conection_message])
            self.core.conection_message = ""
        checks = '\n'.join(checks)
        Dialogs.critical_message(
            self.parent_frame, 'Connection error', f"{checks}")

    # ----------------------------------------------------------------------
    @Slot()
    def disconnected_ok(self):
        """"""
        self.core.stop_kafka()
        if self.parent_frame.checkBox_test_signal.isChecked():
            self.parent_frame.groupBox_settings.setEnabled(False)
            self.parent_frame.groupBox_leadoff_impedance.setEnabled(False)

        self.parent_frame.pushButton_connect.setText('Connect')
        self.parent_frame.pushButton_connect.setChecked(False)
        self.core.status_bar(right_message=('Disconnected', None))
        self.parent_frame.checkBox_view_impedances.setChecked(False)
        self.parent_frame.stackedWidget_montage.setCurrentIndex(0)
