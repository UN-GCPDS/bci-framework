from bci_framework.extensions.timelock_analysis import TimelockDashboard
from bci_framework.extensions.timelock_analysis import timelock_analysis as ta
import numpy as np


########################################################################
class SelectMarkers(ta.ScriptProcess):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, height, *args, **kwargs):
        """Constructor"""
        super().__init__(0, *args, **kwargs)
        self.title = 'Script process'
        self.pipeline_tunned = True

    # ----------------------------------------------------------------------
    def fit(self):
        """"""
        self.clear_widgets(areas=['top'])
        self.marker_sync = self.add_checkbox('Markers', self.pipeline_input.markers.keys(
        ), callback=self.process, area='top', stretch=0)
        self.add_spacer(stretch=1, area='top')

    # ----------------------------------------------------------------------
    def process(self, *args, **kwargs):
        """"""
        self.pipeline_input.reset_markers()
        target_markers = [ch.text()
                          for ch in self.marker_sync if ch.isChecked()]
        markers = self.discrimine_marker(
            self.pipeline_input.markers, target_markers)

        self.pipeline_input.reset_markers(markers)
        self.pipeline_output = self.pipeline_input

    # ----------------------------------------------------------------------
    def discrimine_marker(self, markers, target_markers):
        """"""
        markers = markers.copy()
        discarted = 0
        no_response = 0
        errors = 0

        def min_distance(m, mks):
            min_ = np.argmin(abs(np.array([markers[mk][np.argmin(
                abs(markers[mk] - m))] for mk in mks if len(markers[mk])]) - m))
            return mks[min_]

        for mk in target_markers:
            for m in markers[mk]:

                min_ = min_distance(m, ['Left', 'Right'])[0]

                response = min_distance(
                    m, ['Different', 'Identical', 'No-response'])
                changed = min_distance(m, ['Changed', 'No-changed'])

                if (response != 'No-response') and \
                    (response == 'Different' and changed == 'Changed') or \
                        (response == 'Identical' and changed == 'No-changed'):
                    markers.setdefault(
                        f'{mk.replace("_fixed", "")}{min_}', []).append(m)

                else:
                    discarted += 1

                if (response == 'No-response'):
                    no_response += 1

                if (response == 'Different' and changed == 'No-changed') or (response == 'Identical' and changed == 'Changed'):
                    errors += 1

        print(f'{discarted} trials discarded!!')
        print(f'{no_response} trials without response.')
        print(f'{errors} trials with wrong response.')

        return markers


########################################################################
class Analysis(TimelockDashboard):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """Constructor"""
        super().__init__(*args, **kwargs)

        self.columns = 1

        self.add_widgets(
            ta.LoadDatabase,
            ta.Filters,
            ta.AddMarkers,
            ta.AmplitudeAnalysis,
            ta.MarkersSynchronization,
            SelectMarkers,
            ta.EpochsVisualization,
        )


if __name__ == '__main__':
    Analysis()


