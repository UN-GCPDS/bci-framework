"""
================
Neuropathic pain
================

"""

from bci_framework.extensions.stimuli_delivery import StimuliAPI


########################################################################
class NeuropathicPain(StimuliAPI):
    """Visual working memory: change detection task."""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        self.add_stylesheet('styles.css')
        self.build_areas()
        self.show_cross()

        self.dashboard <= w.label(
            'Neuropathic pain', 'headline4')
        self.dashboard <= html.BR()
        
        self.dashboard <= w.subject_information(paradigm='Neuropathic pain')

if __name__ == '__main__':
    NeuropathicPain()


