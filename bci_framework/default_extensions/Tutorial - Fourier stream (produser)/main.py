from bci_framework.extensions.data_analysis import DataAnalysis, fake_loop_consumer
from bci_framework.extensions import properties as prop
from gcpds.utils.processing import fourier

class Analysis(DataAnalysis):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.create_buffer(seconds=30, resampling=1000)
        self.stream()

    @fake_loop_consumer('eeg')
    def stream(self):
         W, EEG = fourier(self.buffer_eeg, fs=prop.SAMPLE_RATE, axis=1)
         data = {'amplitude': EEG,
                 'frequency': W}
         self.generic_produser('spectrum', data)

if __name__ == '__main__':
    Analysis(enable_produser=True)