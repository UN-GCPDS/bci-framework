import os
from ..dialogs import Dialogs
from openbci_stream.acquisition import Cyton, CytonBase
import json
import time
import logging

from ..projects import properties as prop

# from ..config_manager import C
# from PySide2.QtUiTools import QUiLoader
# from PySide2.QtCore import QTimer
# from PySide2.QtGui import QMovie

# from contextlib import contextmanager
# from PyQt4 import QtCore
# from PyQt4.QtGui import QApplication, QCursor

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication
from PySide2.QtGui import QCursor


########################################################################
class Connection:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, core):
        """Constructor"""
        self.parent = core.main
        self.core = core

        # self.parent.pushButton_disconnect.hide()

        self.config = {
            'mode': self.parent.comboBox_connection_mode,
            'port': self.parent.comboBox_port,
            'ip': self.parent.comboBox_ip,
            'host': self.parent.comboBox_host,
            'acquisition_sample_rate': self.parent.comboBox_sample_rate,
            'streaming_sample_rate': self.parent.comboBox_streaming_sample_rate,
            'boardmode': self.parent.comboBox_boardmode,
            'gain': self.parent.comboBox_gain,
            'input_type': self.parent.comboBox_input_type,
            'bias': self.parent.comboBox_bias,
            'srb1': self.parent.comboBox_srb1,
            'srb2': self.parent.comboBox_srb2,
            'pchan': self.parent.comboBox_pchan,
            'nchan': self.parent.comboBox_nchan,
            'test_signal_type': self.parent.comboBox_test_signal,
            'test_signal': self.parent.checkBox_test_signal,

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

    # ----------------------------------------------------------------------
    def update_config(self, *args, **kwargs):
        """"""
        self.core.config.save_widgets('connection', self.config)

    # ----------------------------------------------------------------------
    def connect(self):
        """"""
        self.parent.pushButton_connect.clicked.connect(self.on_connect)
        self.parent.comboBox_connection_mode.activated.connect(
            self.update_connections)

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
            # self.openbci_connect()
            QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
            try:
                self.openbci_connect()
            except:
                QApplication.restoreOverrideCursor()
                checks = []

                if 'serial' in self.parent.comboBox_connection_mode.currentText().lower():
                    checks.extend(['* Check that USB dongle were connected',
                                   '* Verify serial permissions',
                                   ])

                if self.parent.comboBox_host.currentText() != 'localhost':
                    checks.extend([f'* The server may not running, or running on a different IP that {self.parent.comboBox_host.currentText()}',
                                   '* This machine must have access to the server or running in the same network.',
                                   ])
                else:
                    checks.extend([f'* Verify that Kafka is running on this machine',
                                   ])

                checks = '\n'.join(checks)
                Dialogs.critical_message(
                    self.parent, 'Connection error', f"{checks}")

                self.parent.pushButton_connect.setChecked(False)

                self.openbci_disconnect()

            finally:
                QApplication.restoreOverrideCursor()

        else:
            self.openbci_disconnect()

    # ----------------------------------------------------------------------
    def openbci_connect(self):
        """"""
        if 'serial' in self.parent.comboBox_connection_mode.currentText().lower():
            mode = 'serial'
            endpoint = self.parent.comboBox_port.currentText()
            os.environ['BCISTREAM_CONNECTION'] = json.dumps('serial')
        else:
            mode = 'wifi'
            endpoint = self.parent.comboBox_ip.currentText()
            os.environ['BCISTREAM_CONNECTION'] = json.dumps('wifi')

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

        self.openbci = Cyton(mode, endpoint, host=host, capture_stream=False,
                             daisy=prop.DAISY, montage=channels, stream_samples=int(streaming_sample_rate))

        self.openbci.command(sample_rate)

        # if self.parent.checkBox_test_signal.isChecked():
            # test_signal = self.parent.comboBox_test_signal.currentText()
            # test_signal = getattr(
                # CytonBase, f"TEST_{test_signal.replace(' ', '_')}")
            # self.openbci.command(test_signal)

            # self.core.status_bar(
                # f'OpenBCI connected on test mode ({test_signal}) to <b>{endpoint}</b> running in <b>{host}</b>')

        # else:
        # Some time this command not take effect
        boardmode_setted = False
        for _ in range(10):
            if b'Success' in self.openbci.command(boardmode):
                logging.info(f'Bardmode setted in {boardmode} mode')
                boardmode_setted = True
                break
            time.sleep(0.1)

        self.boardmode = self.openbci.boardmode
        if not boardmode_setted:
            logging.warning('Boardmode not setted!')
            Dialogs.warning_message(
                self.parent, 'Boardmode', f'Boardmode could no be setted correctly.\n{self.boardmode}')
            self.parent.comboBox_boardmode.setCurrentText(
                self.boardmode.capitalize())

        self.openbci.leadoff_impedance(channels, pchan=pchan, nchan=nchan)

        self.openbci.channel_settings(channels, power_down=CytonBase.POWER_DOWN_ON,
                                      gain=gain,
                                      input_type=adsinput,
                                      bias=bias,
                                      srb2=srb2,
                                      srb1=srb1)

        self.openbci.start_stream()

        if self.parent.checkBox_test_signal.isChecked():
            test_signal = self.parent.comboBox_test_signal.currentText()
            test_signal = getattr(
                CytonBase, f"TEST_{test_signal.replace(' ', '_')}")
            self.openbci.command(test_signal)

            self.core.status_bar(
                f'OpenBCI connected on test mode ({test_signal}) to <b>{endpoint}</b> running in <b>{host}</b>')

        else:

            self.openbci.activate_channel(channels)
            self.core.status_bar(
                f'OpenBCI connected and streaming in <b>{self.boardmode}</b> mode to <b>{endpoint}</b> running in <b>{host}</b>')

        self.parent.pushButton_connect.setText('Disconnect')
        self.update_environ()

    # ----------------------------------------------------------------------
    def openbci_disconnect(self):
        """"""
        # self.openbci.
        if self.parent.checkBox_test_signal.isChecked():
            self.parent.groupBox_settings.setEnabled(False)
            self.parent.groupBox_leadoff_impedance.setEnabled(False)
        try:
            self.openbci.stop_stream()
        except:
            pass
        self.parent.pushButton_connect.setText('Connect')
        self.core.status_bar(f'Disconnect')

    # ----------------------------------------------------------------------

    def update_environ(self):
        """"""
        os.environ['BCISTREAM_HOST'] = json.dumps(
            self.parent.comboBox_host.currentText())

        sps = self.parent.comboBox_sample_rate.currentText()
        if 'k' in sps.lower():
            sps = int(sps.lower().replace('k', '')) * 1000
        else:
            sps = int(sps)
        os.environ['BCISTREAM_SAMPLE_RATE'] = json.dumps(sps)
        os.environ['BCISTREAM_STREAMING_SAMPLE_RATE'] = json.dumps(
            int(self.parent.comboBox_streaming_sample_rate.currentText()))

        os.environ['BCISTREAM_BOARDMODE'] = json.dumps(
            self.parent.comboBox_boardmode.currentText().lower())



