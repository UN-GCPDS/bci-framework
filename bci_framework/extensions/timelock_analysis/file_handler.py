from openbci_stream.utils.hdf5 import HDF5Reader


########################################################################
class FileHandler:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, filename):
        """Constructor"""

        if filename.endswith('.h5'):
            self.file = HDF5Reader(filename)
            print(self.file)

    # ----------------------------------------------------------------------
    @property
    def eeg(self):
        """"""
        return self.file.eeg.copy()

    # ----------------------------------------------------------------------
    @property
    def timestamp(self):
        """"""
        return self.file.timestamp.copy()

    # ----------------------------------------------------------------------

    @property
    def markers(self):
        """"""
        return self.file.markers.copy()

    # ----------------------------------------------------------------------
    @property
    def header(self):
        """"""
        return self.file.header

    # ----------------------------------------------------------------------
    @property
    def description(self):
        """"""
        return self.file.__str__()

    # ----------------------------------------------------------------------
    def close(self):
        """"""
        self.file.close()

