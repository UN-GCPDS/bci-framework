from .visualization_widget import VisualizationWidget


########################################################################
class Visualization:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, core):
        """Constructor"""

        self.parent = core.main
        self.core = core

        self.update_visualizations_list()
        self.connect()

    # ----------------------------------------------------------------------
    def connect(self):
        """"""
        # self.parent.comboBox_load_visualization.activated.connect(
            # self.add_subwindow)
        self.parent.pushButton_load_visualizarion.clicked.connect(
            self.add_subwindow)

    # ----------------------------------------------------------------------
    def update_visualizations_list(self, event=None):
        """"""
        for i in range(self.parent.listWidget_projects.count()):
            item = self.parent.listWidget_projects.item(i)
            if item.icon_name == 'icon_viz':
                self.parent.comboBox_load_visualization.addItem(item.text())

    # ----------------------------------------------------------------------
    def add_subwindow(self, event=None):
        """"""
        sub = VisualizationWidget(self.parent)
        self.parent.mdiArea.addSubWindow(sub)
        sub.show()
        self.parent.mdiArea.tileSubWindows()

        # self.parent.mdiArea.closeAllSubWindows()
        sub.load_visualization(
            self.parent.comboBox_load_visualization.currentText())

