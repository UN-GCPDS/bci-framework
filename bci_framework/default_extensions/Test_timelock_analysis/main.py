from bci_framework.extensions.timelock_analysis import TimelockDashboard
from bci_framework.extensions.timelock_analysis import timelock_analysis as ta


########################################################################
class Analysis(TimelockDashboard):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """Constructor"""
        super().__init__(*args, **kwargs)

        self.add_widgets(
            (ta.LoadDatabase, {'title': 'Raw EEG signal'}),
            (ta.TimelockFilters, {'title': 'Filter EEG'}),
            (ta.AddMarkers, {'title': 'Add new markers'}),
            (ta.TimelockAmplitudeAnalysis, {'title': 'Amplitude analysis'}),
            (ta.EpochsVisualization, {'title': 'Visualize epochs'}),
            # {'analyzer': AnalysisWidget,  'row': 1, 'col': 0, 'row_span': 1, 'col_span': 1},
            # {'analyzer': AnalysisWidget,  'row': 1, 'col': 1, 'row_span': 1, 'col_span': 1},
        )


if __name__ == '__main__':
    Analysis()


