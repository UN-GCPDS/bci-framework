from bci_framework.extensions.visualizations import EEGStream, loop_consumer, fake_loop_consumer
from bci_framework.extensions import properties as prop

import logging
import numpy as np
from datetime import datetime
import seaborn as snb


########################################################################
class Stream(EEGStream):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """"""
        super().__init__(enable_produser=True)
        
        # self.N = int(prop.SAMPLE_RATE / prop.STREAMING_PACKAGE_SIZE)
        
        self.axis_wave = self.add_subplot(111)
        # self.axis_hist = self.add_subplot(223)
        # self.axis_log = self.add_subplot(222)
        # self.axis_time = self.add_subplot(224)
        
        # self.subplots_adjust(hspace=0.3)
        
        
        self.wave_line = self.axis_wave.plot([0], [0])[0]
        self.wave_line2 = self.axis_wave.plot([0], [0])[0]
        

        # self.latency_time = self.axis_time.plot([0], [0])[0]
        

        # self.axis, self.time, self.lines = self.create_lines(
            # mode='analog', time=-30, window=1000)

        self.timestamp_rises = np.array([])
        
        self.markers_timestamps = []
        
        self.latencies = []
        
        # self.create_boundary(self.axis, -0.5, 1.5)
        
        
        

        self.axis_wave.set_title('Synchronizations')
        self.axis_wave.set_xlabel('Elapsed time [s]')
        self.axis_wave.set_ylabel('Amplitude')
        self.axis_wave.grid(True)

        # self.axis_time.set_title('Latency timeline')
        # self.axis_time.set_xlabel('Elapsed time [s]')
        # self.axis_time.set_ylabel('Latency (ms)')
        # self.axis_time.grid(True)
        
        
        # self.axis_time.spines['right'].set_visible(False)
        # self.axis_time.spines['top'].set_visible(False)
        

        # self.axis.set_ylim(-0.5, 1.5)

        self.create_buffer(10, resampling=1000, fill=-1)
        
        self.stream()

    # ----------------------------------------------------------------------
    def get_rises(self, data, timestamp):
        """"""
        data = data.copy()

        data[data > data.mean()] = 1
        data[data < data.mean()] = 0

        diff = np.diff(data, prepend=0)
        diff[diff < 0] = 0
        diff[0] = 0

        return timestamp[np.nonzero(diff)[0]], diff

    # ----------------------------------------------------------------------
    @loop_consumer('eeg', 'marker')
    def stream(self, data, topic, frame, latency):
        """"""

        # if frame % 10 > 0:
            # return

        # logging.warning(f"L: {latency:.2f}")

        if topic == 'eeg':
            
            
            # Rise plot
            aux = self.buffer_aux[0]
            aux[aux==-1] = aux[-1]
            aux = aux - aux.min()
            aux = aux / aux.max()
            self.axis_wave.set_ylim(-0.1, 1.1)
            self.axis_wave.set_xlim(-1, 1.5)
            
            # t = np.linspace(0, 10, aux.shape[0])
            # self.axis_wave.set_xlim(0, 10)
            # self.axis_wave.set_ylim(aux.min(), aux.max())
            # self.wave_line.set_data(t, aux)
            
            self.timestamp_rises, diff = self.get_rises(aux, self.buffer_timestamp)    
            
            # self.wave_line2.set_data(t, diff)
            
                    
                                    
            q = np.argwhere(diff>0)
            # logging.warning(q)
            if q.size > 2 :
                v = q[-2]
                window = aux.copy()
                # window = aux[int(v-prop.SAMPLE_RATE):int(v+prop.SAMPLE_RATE)]
                t = np.linspace(0 ,10, 10000)
                self.wave_line.set_data(t, window)
                self.wave_line2.set_data(t, diff*2)
                self.axis_wave.set_xlim(0, 10)
                
                

            
            

        elif topic == 'marker' and self.timestamp_rises.size > 0:
            
            self.markers_timestamps.append(datetime.fromtimestamp(data.timestamp / 1000))
            if len(self.markers_timestamps)>=3:
                self.markers_timestamps.pop(0)
                
            x = []
            for mt in self.markers_timestamps:
                for rt in self.timestamp_rises:
                    x.append((mt - datetime.fromtimestamp(rt)).total_seconds())
                    
            x = np.array(x)
            sg = np.sign(x[np.argmin(abs(x))])
            latency = sg*min(abs(x))*1000
            
            self.latencies.append(latency)
            
            logging.warning(f"Latency: {latency:.3f} ms {np.var(self.latencies)}")
            self.send_annotation(f'Latency: {latency:.2f}')
            
            
        self.feed()
            
            
            
            
            
            

if __name__ == '__main__':
    Stream()
