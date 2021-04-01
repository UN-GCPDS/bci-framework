from bci_framework.extensions.data_analysis import DataAnalysis, loop_consumer
from bci_framework.extensions import properties as prop
# from gcpds.utils.processing import fourier


class Analysis(DataAnalysis):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stream()

    @loop_consumer('spectrum')
    def stream(self, data):
        data = data.value['data']

        EEG = data['amplitude']
        W = data['frequency']


if __name__ == '__main__':
    Analysis()
