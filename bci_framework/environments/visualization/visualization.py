from .visualization_widget import VisualizationWidget


########################################################################
class Visualization:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, core):
        """Constructor"""

        self.parent = core.main
        self.core = core

        self.connect()

    # ----------------------------------------------------------------------
    def connect(self):
        """"""
        self.parent.pushButton_add_visualizarion.clicked.connect(
            self.add_subwindow)

    # ----------------------------------------------------------------------
    def add_subwindow(self):
        """"""
        sub = VisualizationWidget(self.parent)
        # sub.update_visualizations_list()

        self.parent.mdiArea.addSubWindow(sub)
        sub.show()

        self.parent.mdiArea.tileSubWindows()

