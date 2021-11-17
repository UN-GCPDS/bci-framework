from openbci_stream.utils.hdf5 import HDF5Reader


########################################################################
class FileHandler:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, filename):
        """Constructor"""

        if filename.endswith('.h5'):
            self.file = HDF5Reader(filename)

    # ----------------------------------------------------------------------
    def data(self):
        """"""
        return self.file.eeg, self.file.timestamp

    # ----------------------------------------------------------------------
    def close(self):
        """"""
        self.file.close()

    # ----------------------------------------------------------------------
    @property
    def header(self):
        """"""
        return self.file.header

