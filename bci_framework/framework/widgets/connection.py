"""
===========
Connections
===========
"""

import os
import json
import time
import types
import logging
import requests

from openbci_stream.acquisition import Cyton, CytonBase, wifi, restart_services
from PySide6.QtCore import Qt, Signal, QThread, Slot, QTimer
from PySide6.QtGui import QCursor, QIcon
from PySide6.QtWidgets import QApplication

from ..dialogs import Dialogs
from ...extensions import properties as prop
# from ...extensions.data_analysis.utils import thread_this


########################################################################
class OpenBCIThread(QThread):
    """Handle the OpenBCI connection."""

    connection_ok = Signal()
    connection_fail = Signal(object)
    disconnected_ok = Signal()
    connected = False

    # ----------------------------------------------------------------------
    def stop(self) -> None:
        """Kill the trhrad."""
        self.terminate()

    # ----------------------------------------------------------------------
    def run(self) -> None:
        """Connect and configure OpenBCI board."""

        if sum(self.channels_assignations) != len(self.montage):
            self.connection_fail.emit(
                ['* The number of electrodes defined in montage not correspon with the number of boards available.'])
            return

        try:
            self.openbci = Cyton(self.mode,
                                 self.endpoint,
                                 host=self.host,
                                 capture_stream=False,
                                 daisy=self.daisy,
                                 montage=self.montage,
                                 streaming_package_size=self.streaming_package_size,
                                 number_of_channels=self.channels_assignations,
                                 )

        except Exception as msg:
            logging.warning(msg)
            self.connection_fail.emit([])
            return

        self.session_settings(self.montage, self.bias,
                              self.gain, self.srb1, self.adsinput, self.srb2, self.sample_rate)

        if getattr(self.openbci, 'is_recycled', False):
            self.connected = True
            self.start_stream_()
            self.connection_ok.emit()
            return

        try:
            self.openbci.command(self.sample_rate)
            self.openbci.command(self.boardmode)
        except TimeoutError:
            self.connection_fail.emit(
                ['* OpenBCI board could not be connected the same network.'])
            return

        # Some time this command not take effect
        boardmode_setted = False
        for _ in range(10):
            response = self.openbci.command(self.boardmode)
            if response and all([b'Success:' in r for r in response]):
                logging.info(f'Bardmode setted in {self.boardmode} mode')
                boardmode_setted = True
                break
            time.sleep(0.1)

        # boardmode = self.openbci.boardmode
        if not boardmode_setted:
            logging.warning('Boardmode not setted!')
        # self.session_settings(self.montage, self.bias,
                              # self.gain, self.srb1, self.adsinput, self.srb2, self.sample_rate)

        if self.checkBox_send_leadoff:
            self.openbci.leadoff_impedance(
                self.montage, pchan=self.pchan, nchan=self.nchan)

        if self.checkBox_test_signal:
            test_signal = self.comboBox_test_signal
            test_signal = getattr(
                CytonBase, f"TEST_{test_signal.replace(' ', '_')}")
            self.openbci.command(test_signal)

        # else:
            # used_channels = set(self.montage.keys())
            # if used_channels:
                # self.openbci.activate_channel(used_channels)
            # # all_channels = set(range(1, 17 if prop.DAISY else 9))
            # # deactivated = all_channels.difference(used_channels)
            # # if deactivated:
                # # self.openbci.deactivate_channel(deactivated)

        self.start_stream_()

    # ----------------------------------------------------------------------
    def start_stream_(self):
        """"""
        if not self.streaming():
            try:
                self.openbci.start_stream()
                self.connected = True
                self.connection_ok.emit()

                if self.mode == 'wifi':
                    self.openbci.set_latency(self.tcp_latency)

            except Exception as e:
                if 'NoBrokersAvailable' in str(e):

                    self.connection_fail.emit(
                        ['* Kafka is not running on the remote acquisition system.'])

    # ----------------------------------------------------------------------
    def session_settings(self, *args) -> None:
        """Create a session setting to reuse it after an impedance measurement."""
        if hasattr(self, 'last_settings'):
            channels, bias, gain, srb1, adsinput, srb2, sample_rate = self.last_settings
        elif args:
            self.last_settings = args
            channels, bias, gain, srb1, adsinput, srb2, sample_rate = args
        else:
            return

        response = self.openbci.command(sample_rate)
        logging.warning(response)

        if self.checkBox_default_settings:
            self.openbci.command(self.openbci.DEFAULT_CHANNELS_SETTINGS)
        else:
            self.openbci.channel_settings(channels, power_down=CytonBase.POWER_DOWN_ON,
                                          gain=gain,
                                          input_type=adsinput,
                                          bias=bias,
                                          srb2=[f'{s}'.encode()
                                                for s in srb2],
                                          srb1=srb1)

    # ----------------------------------------------------------------------
    def disconnect(self) -> None:
        """Disconnect OpenBCI."""
        try:
            # self.openbci.stop_stream()
            self.openbci.close()
        except:
            pass
        self.disconnected_ok.emit()
        self.connected = False


########################################################################
class Connection:
    """Widget that handle the OpenBCI connection."""

    # ----------------------------------------------------------------------
    def __init__(self, core):
        """"""
        self.parent_frame = core.main
        self.core = core

        # self.parent.pushButton_disconnect.hide()
        self.openbci = OpenBCIThread()
        self.openbci.streaming = lambda: getattr(
            self.core, 'streaming', False)

        self.openbci.connection_ok.connect(self.connection_ok)
        self.openbci.connection_fail.connect(self.connection_fail)
        self.openbci.disconnected_ok.connect(self.disconnected_ok)
        self.channels_assignations = {}

        self.config = {
            'mode': self.parent_frame.comboBox_connection_mode,
            'check1': self.parent_frame.checkBox_board1,
            'check2': self.parent_frame.checkBox_board2,
            'check3': self.parent_frame.checkBox_board3,
            'check4': self.parent_frame.checkBox_board4,
            'port1': self.parent_frame.comboBox_port1,
            'port2': self.parent_frame.comboBox_port2,
            'port3': self.parent_frame.comboBox_port3,
            'port4': self.parent_frame.comboBox_port4,
            'ip1': self.parent_frame.comboBox_ip1,
            'ip2': self.parent_frame.comboBox_ip2,
            'ip3': self.parent_frame.comboBox_ip3,
            'ip4': self.parent_frame.comboBox_ip4,
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
            'tcp_latency': self.parent_frame.spinBox_tcp_latency,
        }

        self.load_config()
        self.update_connections()
        self.update_environ()
        self.connect()
        self.core.config.connect_widgets(self.update_config, self.config)

        QTimer().singleShot(1000, self.autoconnect)

    # ----------------------------------------------------------------------
    def restart_services(self):
        """"""
        if json.loads(os.getenv('BCISTREAM_RASPAD')):
            try:
                restart_services(prop.HOST)
                logging.warning(
                    f'Restarting services on {prop.HOST}')
            except:
                logging.warning(
                    f'Impossible to restart services on {prop.HOST}')

    # ----------------------------------------------------------------------
    def on_focus(self) -> None:
        """Try to autoconnect."""
        # if getattr(self.core, 'streaming', False) and not self.openbci.connected:
            # self.openbci_connect()

        for i in range(1, 5):
            combo = getattr(self.parent_frame, f'comboBox_ip{i}')
            target = getattr(self.parent_frame, f'pushButton_ip{i}')
            check = getattr(self.parent_frame, f'checkBox_board{i}')
            if check.isChecked():
                self.request_wifi(i, target, combo, no_cursor=True)()

    # ----------------------------------------------------------------------
    def load_config(self) -> None:
        """Load widgets."""
        self.core.config.load_widgets('connection', self.config)
        self.core.update_kafka(self.parent_frame.comboBox_host.currentText())

    # ----------------------------------------------------------------------
    def update_config(self, *args, **kwargs) -> None:
        """Save widgets status."""
        self.core.config.save_widgets('connection', self.config)

    # ----------------------------------------------------------------------
    def connect(self) -> None:
        """Connect events."""
        self.parent_frame.pushButton_connect.clicked.connect(self.on_connect)
        self.parent_frame.comboBox_connection_mode.activated.connect(
            self.update_connections)
        # self.parent_frame.comboBox_host.textActivated.connect(
            # self.load_config)

        # CheckWiFiModule
        for i in range(1, 5):
            combo = getattr(self.parent_frame, f'comboBox_ip{i}')
            target = getattr(self.parent_frame, f'pushButton_ip{i}')
            # combo.textActivated.connect(
                # self.request_wifi(i, target, combo))
            target.setStyleSheet("""*{
                background-color: transparent !important;
                 }""")

            getattr(self.parent_frame, f'pushButton_update_wifi{i}').clicked.connect(
                self.request_wifi(i, target, combo))

            getattr(self.parent_frame, f'checkBox_board{i}').stateChanged.connect(
                self.wrap_clear_text(target))

            # check = getattr(self.parent_frame, f'checkBox_board{i}')
            # if check.isChecked():
                # self.request_wifi(i, target, combo)()

    # ----------------------------------------------------------------------
    def wrap_clear_text(self, target):
        """"""
        def wrapped():
            target.setText('')
        return wrapped

    # ----------------------------------------------------------------------
    def request_wifi(self, board, target, combo, no_cursor=False):
        """"""
        target.setText('')
        target.hide()

        # @thread_this
        def inset():
            if not no_cursor:
                QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))

            ip = combo.currentText()
            combo.valid = False

            try:
                target.setStyleSheet("""*{
                background-color: transparent !important;
                 }""")

                response = wifi(
                    self.parent_frame.comboBox_host.currentText(), ip)

                if response['board_connected']:
                    target.setText(
                        f"connected ({response['num_channels']} ch)")
                    target.setProperty('class', 'success icon_button')
                    combo.valid = True
                    self.channels_assignations[board] = response['num_channels']
                else:
                    target.setText('connected (no board detected)')
                    target.setProperty('class', 'danger icon_button')
                    if board in self.channels_assignations:
                        del self.channels_assignations[board]

                target.style().unpolish(target)
                target.style().polish(target)
                target.update()

            except:
                target.setStyleSheet("""*{
                background-color: transparent !important;
                 }""")
                target.setText('No WiFi module found')
                target.setProperty('class', 'danger icon_button')
                target.style().unpolish(target)
                target.style().polish(target)
                target.update()
                if board in self.channels_assignations:
                    del self.channels_assignations[board]

            target.show()
            if not no_cursor:
                QApplication.restoreOverrideCursor()
        return inset

    # ----------------------------------------------------------------------
    def update_connections(self) -> None:
        """Set widgets for connection modes."""
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

            # self.parent_frame.label_port_ip.setText('Port')
            for i in range(1, 5):
                getattr(self.parent_frame, f'comboBox_ip{i}').hide()
                getattr(self.parent_frame, f'comboBox_port{i}').show()
                getattr(self.parent_frame,
                        f'pushButton_update_wifi{i}').hide()
                getattr(self.parent_frame,
                        f'pushButton_ip{i}').hide()
            # self.parent_frame.comboBox_ip.hide()
            # self.parent_frame.comboBox_port.show()
            self.parent_frame.label_latency.setEnabled(False)
            self.parent_frame.spinBox_tcp_latency.setEnabled(False)

        else:

            for index in range(1, self.parent_frame.comboBox_sample_rate.count()):
                self.parent_frame.comboBox_sample_rate.model().item(index).setEnabled(True)

            for index in range(3, self.parent_frame.comboBox_streaming_sample_rate.count()):
                self.parent_frame.comboBox_streaming_sample_rate.model().item(index).setEnabled(True)

            # self.parent_frame.label_port_ip.setText('IP')
            for i in range(1, 5):
                getattr(self.parent_frame, f'comboBox_ip{i}').show()
                getattr(self.parent_frame, f'comboBox_port{i}').hide()
                getattr(self.parent_frame,
                        f'pushButton_update_wifi{i}').show()
                getattr(self.parent_frame,
                        f'pushButton_ip{i}').show()
            # self.parent_frame.comboBox_ip.show()
            # self.parent_frame.comboBox_port.hide()
            self.parent_frame.label_latency.setEnabled(True)
            self.parent_frame.spinBox_tcp_latency.setEnabled(True)

    # ----------------------------------------------------------------------
    def autoconnect(self) -> None:
        """"""
        logging.info('Trying to auto connect')
        self.core.calculate_offset()
        if getattr(self.core, 'streaming', False) and not self.openbci.connected:
            self.openbci_connect()

    # ----------------------------------------------------------------------
    def on_connect(self, toggled: bool) -> None:
        """Event to handle connection."""

        self.core.calculate_offset()
        if getattr(self.core, 'streaming', False) and not self.openbci.connected:
            self.openbci_connect()
        else:
            if toggled:  # Connect
                QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
                self.core.update_kafka(
                    self.parent_frame.comboBox_host.currentText())
                self.restart_services()
                self.openbci_connect()

            else:   # Disconnect
                self.openbci.disconnect()

    # ----------------------------------------------------------------------
    def openbci_connect(self) -> None:
        """Recollect values from GUI."""
        if 'serial' in self.parent_frame.comboBox_connection_mode.currentText().lower():
            mode = 'serial'
            endpoint = [getattr(self.parent_frame, f'comboBox_port{i}').currentText() for i in range(
                1, 5) if getattr(getattr(self.parent_frame, f'comboBox_ip{i}'), 'valid', False)]
            os.environ['BCISTREAM_CONNECTION'] = json.dumps('serial')
        else:
            mode = 'wifi'
            endpoint = [getattr(self.parent_frame, f'comboBox_ip{i}').currentText() for i in range(
                1, 5) if getattr(getattr(self.parent_frame, f'comboBox_ip{i}'), 'valid', False)]
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

        tcp_latency = self.parent_frame.spinBox_tcp_latency.value()

        # channels = self.core.montage.get_mne_montage().ch_names

        # self.openbci = OpenBCIThread()
        # self.openbci.connection_ok.connect(self.connection_ok)
        # self.openbci.connection_fail.connect(self.connection_fail)
        # self.openbci.disconnected_ok.connect(self.disconnected_ok)

        self.openbci.mode = mode
        self.openbci.endpoint = endpoint
        self.openbci.host = host
        self.openbci.tcp_latency = tcp_latency
        self.openbci.montage = prop.CHANNELS
        self.openbci.streaming_package_size = int(streaming_sample_rate)
        self.openbci.sample_rate = sample_rate
        self.openbci.boardmode = boardmode
        self.openbci.adsinput = adsinput
        self.openbci.bias = bias
        self.openbci.srb1 = srb1
        # self.openbci.srb2 = srb2
        self.openbci.srb2 = prop.MONTAGE_TYPE
        self.openbci.pchan = pchan
        self.openbci.nchan = nchan
        self.openbci.gain = gain

        for i in range(1, 5):
            check = getattr(self.parent_frame, f'checkBox_board{i}')
            # combo = getattr(self.parent_frame, f'comboBox_ip{i}')
            # target = getattr(self.parent_frame, f'pushButton_ip{i}')
            if (not check.isChecked()) and (i in self.channels_assignations):
                del self.channels_assignations[i]

        self.openbci.channels_assignations = [
            e[1] for e in sorted(list(self.channels_assignations.items()))]

        self.openbci.daisy = [
            True if chs == 16 else False for chs in self.openbci.channels_assignations]
        os.environ['BCISTREAM_DAISY'] = json.dumps(all(self.openbci.daisy))
        os.environ['BCISTREAM_CHANNELS_BY_BOARD'] = json.dumps(
            self.openbci.channels_assignations)

        # self.openbci.checkBox_send_leadoff = self.parent_frame.checkBox_send_leadoff.isChecked()
        self.openbci.checkBox_send_leadoff = self.parent_frame.groupBox_leadoff_impedance.isChecked()
        # self.openbci.checkBox_default_settings = self.parent_frame.checkBox_default_settings.isChecked()
        self.openbci.checkBox_default_settings = not self.parent_frame.groupBox_settings.isChecked()

        self.openbci.checkBox_test_signal = self.parent_frame.checkBox_test_signal.isChecked()
        self.openbci.comboBox_test_signal = self.parent_frame.comboBox_test_signal.currentText()

        self.parent_frame.pushButton_connect.setText('Connecting...')
        self.parent_frame.pushButton_connect.setEnabled(False)
        self.update_environ()

        self.openbci.start()

    # ----------------------------------------------------------------------
    def update_environ(self) -> None:
        """Update environment variables."""
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
    def connection_ok(self) -> None:
        """Event for OpenBCI connected."""
        QApplication.restoreOverrideCursor()
        self.parent_frame.pushButton_connect.setText('Disconnect')
        self.parent_frame.pushButton_connect.setEnabled(True)
        self.parent_frame.pushButton_connect.setChecked(True)

    # ----------------------------------------------------------------------
    @Slot()
    def connection_fail(self, reasons):
        """Event for OpenBCI failed connection."""
        QApplication.restoreOverrideCursor()

        checks = []

        if reasons:
            checks.extend(reasons)

        else:
            if 'serial' in self.parent_frame.comboBox_connection_mode.currentText().lower():
                checks.extend(['* Check that USB dongle were connected.',
                               '* Verify serial permissions.',
                               ])
            else:
                checks.extend([f"* The WiFi moudule could be running in a different IP",
                               ])

            if self.parent_frame.comboBox_host.currentText() != 'localhost':
                checks.extend([f'* The server could not be running, or running on a different IP that {self.parent_frame.comboBox_host.currentText()}',
                               '* This machine must have access to the server or running on the same network.',
                               '* The daemons `stream_eeg` `stream_rpyc` could not be running',  # todo
                               ])

            if hasattr(self.core, 'conection_message'):
                checks.extend([self.core.conection_message])
                self.core.conection_message = ""

        checks = '\n'.join(checks)
        Dialogs.critical_message(
            self.parent_frame, 'Connection error', f"{checks}")

        self.parent_frame.pushButton_connect.setText('Connect')
        self.parent_frame.pushButton_connect.setEnabled(True)
        self.parent_frame.pushButton_connect.setChecked(False)

    # ----------------------------------------------------------------------
    @Slot()
    def disconnected_ok(self) -> None:
        """OpenBCI disconnected."""
        self.core.stop_kafka()
        if self.parent_frame.checkBox_test_signal.isChecked():
            self.parent_frame.groupBox_settings.setEnabled(False)
            self.parent_frame.groupBox_leadoff_impedance.setEnabled(False)

        self.parent_frame.pushButton_connect.setText('Connect')
        self.parent_frame.pushButton_connect.setEnabled(True)
        self.parent_frame.pushButton_connect.setChecked(False)
        self.core.status_bar(right_message=('Disconnected', None))
        self.parent_frame.checkBox_view_impedances.setChecked(False)
        self.parent_frame.stackedWidget_montage.setCurrentIndex(0)
