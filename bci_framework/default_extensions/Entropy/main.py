from bci_framework.extensions.visualizations import EEGStream, Widgets
from bci_framework.extensions.data_analysis import loop_consumer
from bci_framework.extensions import properties as prop

import numpy as np
import logging

from scipy.fftpack import rfft, rfftfreq

from cycler import cycler
import matplotlib 


########################################################################
class Stream(EEGStream, Widgets):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        
        self.enable_widgets('BandPass',
                            'Notch',
                            # 'Channels',
                            'Window time',
                            )
            
        self.axisFP1 = self.add_subplot(211)
        self.axisFP2 = self.add_subplot(212)
        
        self.linesFP1 = [self.axisFP1.plot([], [], '-', label=['SE', 'RE'][i], color=f'C{i*15}')[0] for i in range(2)]
        self.linesFP2 = [self.axisFP2.plot([], [], '-', label=['SE', 'RE'][i], color=f'C{i*15}')[0] for i in range(2)]
            

        self.axisFP1.set_title('Fp1')
        # self.axisFP1.set_xlabel('Time [s]')
        self.axisFP1.set_ylabel('Entropy')
        self.axisFP1.grid(True)
        
        self.axisFP2.set_title('Fp2')
        self.axisFP2.set_xlabel('Time [s]')
        self.axisFP2.set_ylabel('Entropy')
        self.axisFP2.grid(True)

        self.axisFP1.legend(loc='lower center', ncol=2)
        self.axisFP2.legend(loc='lower center', ncol=2)

        self.create_buffer(30)
        # self.create_buffer(60*5)
        self.dataSE = np.empty((2, 30*(prop.SAMPLE_RATE//prop.STREAMING_PACKAGE_SIZE)))
        self.dataSE.fill(0)
        self.dataRE = self.dataSE.copy()
        self.stream()
        
    
    # ----------------------------------------------------------------------
    @loop_consumer('eeg')
    def stream(self, data):
        """"""
        # channels = self.widget_value['Channels']
        window_time = self.widget_value['Window time']
        
        self.axisFP1.set_xlim(-window_time, 0)
        self.axisFP1.set_ylim(0, 15)
        self.axisFP2.set_xlim(-window_time, 0)
        self.axisFP2.set_ylim(0, 15)
        
        eeg = self.buffer_eeg[:2,-15000:]
        # eeg = eeg[eeg!=np.nan]
        
        # logging.warning(f'{self.buffer_eeg.shape}, {eeg.shape}')
        
        # SE      
        EEG_ = np.abs(rfft(eeg, axis=1))  
        W = rfftfreq(EEG_.shape[1], 1/prop.SAMPLE_RATE)
        EEG = EEG_[:,abs(W-0.8).argmin():abs(W-32).argmin()]  # [.8 Hz, 32 Hz]
        p = EEG / EEG.sum(axis=1)[:,None]
        E = np.sum(p * np.log(1/p), axis=1)
        N = len(EEG[:,abs(W-0.8).argmin():abs(W-47).argmin()])

        # logging.warning(f'{E}')
        
        SE = E / np.log(N) 
        
        
        # RE
        # EEG = np.abs(rfft(eeg, axis=1))
        W = rfftfreq(EEG_.shape[1], 1/prop.SAMPLE_RATE)
        EEG = EEG_[:,abs(W-0.8).argmin():abs(W-47).argmin()]  # [.8 Hz, 47 Hz]
        p = EEG / EEG.sum(axis=1)[:,None]
        E = np.sum(p * np.log(1/p), axis=1)
        # N = len(EEG[abs(W2-0.8).argmin():abs(W2-47).argmin()])
        RE = E / np.log(N) 
        
        # logging.warning(f'{SE}, {RE}')

        self.dataSE = np.roll(self.dataSE, -1, axis=1)
        self.dataSE[:,-1] = SE
        self.dataRE = np.roll(self.dataRE, -1, axis=1)
        self.dataRE[:,-1] = RE
        
        time = np.linspace(-30, 0, self.dataSE.shape[1])
        
        self.linesFP1[0].set_data(time, self.dataSE[0])
        self.linesFP1[1].set_data(time, self.dataRE[0])
        self.linesFP2[0].set_data(time, self.dataSE[1])
        self.linesFP2[1].set_data(time, self.dataRE[1])

        self.feed()


if __name__ == '__main__':
    Stream()
