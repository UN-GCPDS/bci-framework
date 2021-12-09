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
        if hasattr(self, '_modified_eeg'):
            return self._modified_eeg
        else:
            return self.file.eeg.copy()

    # ----------------------------------------------------------------------
    @eeg.setter
    def eeg(self, value):
        """"""
        self._modified_eeg = value

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
        return self.file.header.copy()

    # ----------------------------------------------------------------------
    @property
    def description(self):
        """"""
        return self.file.__str__()

    # ----------------------------------------------------------------------
    def close(self):
        """"""
        self.file.close()

    # ----------------------------------------------------------------------
    def epochs(self, tmax, tmin, markers):
        """"""
        return self.file.get_epochs(tmax=tmax, tmin=tmin, markers=markers, eeg=self.eeg)
