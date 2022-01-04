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
    @property
    def original_eeg(self):
        """"""
        return self.file.eeg.copy()

    # ----------------------------------------------------------------------
    @eeg.setter
    def eeg(self, value):
        """"""
        self._modified_eeg = value

    # ----------------------------------------------------------------------
    @property
    def aux(self):
        """"""
        if hasattr(self, '_modified_aux'):
            return self._modified_aux
        else:
            return self.file.aux.copy()

    # ----------------------------------------------------------------------
    @aux.setter
    def aux(self, value):
        """"""
        self._modified_aux = value

    # ----------------------------------------------------------------------
    @property
    def timestamp(self):
        """"""
        return self.file.timestamp.copy()

    # ----------------------------------------------------------------------
    @property
    def aux_timestamp(self):
        """"""
        return self.file.aux_timestamp.copy()

    # ----------------------------------------------------------------------
    @property
    def markers(self):
        """"""
        if hasattr(self, '_modified_markers'):
            return self._modified_markers
        else:

            if not hasattr(self, '_original_markers'):
                self._original_markers = self.file.markers.copy()
            return self.file.markers.copy()

    # ----------------------------------------------------------------------
    @markers.setter
    def markers(self, value):
        """"""
        # self.file.markers = value
        self._modified_markers = value

    # ----------------------------------------------------------------------
    def reset_markers(self, markers=None):
        """"""
        if markers:
            self.file.markers = markers
        else:
            self.file.markers = self._original_markers.copy()
        # return self._original_markers

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

    # ----------------------------------------------------------------------
    def get_rises(self, signal, timestamp, lower, upper):
        """"""
        return self.file.get_rises(signal, timestamp, lower, upper)

    # ----------------------------------------------------------------------

    def fix_markers(self, target_markers, rises, range_=2000):
        """"""
        return self.file.fix_markers(target_markers, rises)

