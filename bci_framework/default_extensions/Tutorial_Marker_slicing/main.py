from bci_framework.extensions.data_analysis import DataAnalysis, marker_slicing


########################################################################
class Analysis(DataAnalysis):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        self.create_buffer(seconds=30, aux_shape=3)
        self.slicing()

    # ----------------------------------------------------------------------
    @marker_slicing(['Right', 'Left', 'Up', 'Bottom'], t0=-2, duration=6)
    def slicing(self, eeg, aux, timestamp, marker):
        """"""


if __name__ == '__main__':
    Analysis()
