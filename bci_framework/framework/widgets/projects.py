"""
========
Projects
========
"""

import os
import re
import sys
import pickle
import shutil
from typing import TypeVar

from PySide2.QtGui import QIcon
from PySide2.QtCore import Qt, QSize
from PySide2.QtWidgets import QListWidgetItem, QTreeWidgetItem, QDialogButtonBox, QDesktopWidget
from PySide2.QtUiTools import QUiLoader

from ..editor import BCIEditor  # , Autocompleter

PATH = TypeVar('path')


LINE_DELIVERY = 'bci_framework.extensions.stimuli_delivery'
LINE_VISUALIZATION = 'bci_framework.extensions.visualizations'
LINE_ANALYSIS = 'bci_framework.extensions.data_analysis'
BCIFR_FILE = 'bcifr'


########################################################################
class Projects:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, parent, core):
        """"""

        self.project_files = []

        self.parent_frame = parent
        self.core = core

        if '--local' in sys.argv:
            self.projects_dir = os.path.join(
                os.getenv('BCISTREAM_ROOT'), 'default_extensions')
        else:
            self.projects_dir = os.path.join(
                os.getenv('BCISTREAM_HOME'), 'default_extensions')

        self.parent_frame.label_projects_path.setText(self.projects_dir)
        self.parent_frame.label_projects_path.setStyleSheet(
            '*{font-family: "DejaVu Sans Mono";}')

        self.parent_frame.stackedWidget_projects.setCurrentWidget(
            getattr(self.parent_frame, "page_projects"))

        self.load_projects()
        self.connect()

    # ----------------------------------------------------------------------
    def connect(self) -> None:
        """Connect events."""
        self.parent_frame.pushButton_projects.clicked.connect(
            self.show_projects)

        self.parent_frame.checkBox_projects_show_tutorials.stateChanged.connect(
            self.load_projects)

        self.parent_frame.listWidget_projects_visualizations.itemDoubleClicked.connect(
            lambda evt: self.open_project(evt.path))
        self.parent_frame.listWidget_projects_delivery.itemDoubleClicked.connect(
            lambda evt: self.open_project(evt.path))
        self.parent_frame.listWidget_projects_analysis.itemDoubleClicked.connect(
            lambda evt: self.open_project(evt.path))

        self.parent_frame.listWidget_projects_visualizations.itemClicked.connect(
            self.there_can_only_be_one)
        self.parent_frame.listWidget_projects_analysis.itemClicked.connect(
            self.there_can_only_be_one)
        self.parent_frame.listWidget_projects_delivery.itemClicked.connect(
            self.there_can_only_be_one)

        self.parent_frame.listWidget_projects_visualizations.itemChanged.connect(
            self.project_renamed)
        self.parent_frame.listWidget_projects_analysis.itemChanged.connect(
            self.project_renamed)
        self.parent_frame.listWidget_projects_delivery.itemChanged.connect(
            self.project_renamed)

        self.parent_frame.treeWidget_project.itemDoubleClicked.connect(
            self.open_script)
        self.parent_frame.treeWidget_project.itemChanged.connect(
            self.project_file_renamed)
        self.parent_frame.pushButton_projects_add_file.clicked.connect(
            self.add_file)
        self.parent_frame.pushButton_projects_add_folder.clicked.connect(
            self.add_folder)
        self.parent_frame.pushButton_projects_remove.clicked.connect(
            self.remove_file)
        self.parent_frame.pushButton_add_project.clicked.connect(
            self.show_create_project_dialog)
        self.parent_frame.pushButton_remove_project.clicked.connect(
            self.remove_project)
        self.parent_frame.tabWidget_project.tabCloseRequested.connect(
            self.close_tab)
        self.parent_frame.tabWidget_project.currentChanged.connect(
            self.tab_changed)

    # ----------------------------------------------------------------------
    def show_projects(self, evt) -> None:
        """Save files and update projects before load view."""
        self.parent_frame.stackedWidget_projects.setCurrentWidget(
            getattr(self.parent_frame, "page_projects"))
        self.core.development.stop_preview()
        self.core.development.save_all_files()
        self.load_projects()

    # ----------------------------------------------------------------------
    def there_can_only_be_one(self, event) -> None:
        """Only one project can be selected at once."""
        self.parent_frame.listWidget_projects_delivery.clearSelection()
        self.parent_frame.listWidget_projects_analysis.clearSelection()
        self.parent_frame.listWidget_projects_visualizations.clearSelection()
        event.setSelected(True)

    # ----------------------------------------------------------------------
    def tab_changed(self, index) -> None:
        """Update linenumber."""
        if editor := self.parent_frame.tabWidget_project.widget(index):
            editor.update_linenumber()

    # ----------------------------------------------------------------------
    def open_script(self, item) -> None:
        """Load file in the editor."""
        if not item.path in self.project_files:
            self.load_script_in_textedit(item.path)
        self.show_script_in_textedit(item.path)
        self.core.show_interface('Development')
        self.parent_frame.actionDevelopment.setEnabled(True)

    # ----------------------------------------------------------------------
    def normalize_path(self, path):
        """"""
        path = re.sub('[^0-9a-zA-Z]+', '_',
                      path).lstrip('1234567890_').rstrip('_')
        return path

    # ----------------------------------------------------------------------
    def load_projects(self) -> None:
        """Load projects."""
        self.parent_frame.listWidget_projects_visualizations.clear()
        self.parent_frame.listWidget_projects_analysis.clear()
        self.parent_frame.listWidget_projects_delivery.clear()

        projects = os.listdir(self.projects_dir)
        projects = filter(lambda f: os.path.isdir(
            os.path.join(self.projects_dir, f)), projects)
        projects = filter(lambda f: not f.startswith('__'), projects)

        if (not self.parent_frame.checkBox_projects_show_tutorials.isChecked()) and ('--local' in sys.argv):
            projects = filter(lambda f: not f.startswith('_'), projects)

        projects = sorted(list(projects))

        for project_dir in projects:
            project = project_dir
            if os.path.exists(os.path.join(self.projects_dir, project_dir, BCIFR_FILE)):
                bcifr = pickle.load(
                    open(os.path.join(self.projects_dir, project_dir, BCIFR_FILE), 'rb'))
                if isinstance(bcifr, set):
                    pickle.dump({'name': project, 'files': bcifr}, open(
                        os.path.join(self.projects_dir, project_dir, BCIFR_FILE), 'wb'))
                elif isinstance(bcifr, dict):
                    project = bcifr.get('name', project)
            else:
                pickle.dump({'name': project, 'files': []}, open(
                    os.path.join(self.projects_dir, project_dir, BCIFR_FILE), 'wb'))

            if project.startswith('Tutorial |') and not self.parent_frame.checkBox_projects_show_tutorials.isChecked():
                continue

            if project.startswith('Tutorial: ') and not self.parent_frame.checkBox_projects_show_tutorials.isChecked():
                continue

            with open(os.path.join(self.projects_dir, project_dir, 'main.py'), 'r') as file:
                lines = file.readlines()

                modules = {LINE_VISUALIZATION: (self.parent_frame.listWidget_projects_visualizations, 'icon_viz'),
                           LINE_DELIVERY: (self.parent_frame.listWidget_projects_delivery, 'icon_sti'),
                           LINE_ANALYSIS: (self.parent_frame.listWidget_projects_analysis, 'icon_ana'),
                           }
                for module in modules:
                    if [line for line in lines if module in ' '.join(line.split()) and not line.strip().startswith("#")]:
                        widget, icon_name = modules[module]
                        break
                    widget, icon_name = modules[LINE_ANALYSIS]

            item = QListWidgetItem(widget)
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable
                          | Qt.ItemIsDragEnabled | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item.setText(project)
            item.previous_name = project
            item.path = project_dir

            icon = QIcon()
            icon.addFile(
                f"bci:/primary/{icon_name}.svg", QSize(), QIcon.Normal, QIcon.Off)
            item.setIcon(icon)
            item.icon_name = icon_name

    # ----------------------------------------------------------------------
    def open_project(self, project_path) -> None:
        """Open project in the code editor."""
        global files_count, dir_count, project_name_

        if self.parent_frame.listWidget_projects_visualizations.selectedItems():
            self.mode = 'visualization'
        elif self.parent_frame.listWidget_projects_delivery.selectedItems():
            self.mode = 'stimuli'
        elif self.parent_frame.listWidget_projects_analysis.selectedItems():
            self.mode = 'analysis'

        self.parent_frame.stackedWidget_projects.setCurrentWidget(
            getattr(self.parent_frame, "page_projects_files"))

        path = os.path.join(self.projects_dir, project_path)
        # path = project_name

        self.parent_frame.tabWidget_project.clear()

        parent = self.parent_frame.treeWidget_project
        parent.project_name = project_path
        parent.clear()

        files_count = 0
        dir_count = 0
        open_item = None
        project_name_ = project_path

        def add_leaves(parent, path):
            global files_count, dir_count, project_name_

            files = sorted(filter(lambda f: os.path.isfile(
                os.path.join(path, f)), os.listdir(path)))
            dirs = sorted(filter(lambda f: os.path.isdir(
                os.path.join(path, f)), os.listdir(path)))

            for file in dirs:
                if file == '__pycache__':
                    continue

                if self.ignore_file(file):
                    continue

                tree = QTreeWidgetItem(parent)
                tree.setText(0, file)
                tree.path = os.path.join(path, file)
                tree.previous_name = file
                add_leaves(tree, os.path.join(path, file))
                dir_count += 1

            for file in files:

                if self.ignore_file(file):
                    continue

                tree = QTreeWidgetItem(parent)
                tree.setText(0, file)
                tree.path = os.path.join(path, file)
                tree.previous_name = file
                # if 'main.py' == file:
                # self.open_script(tree)

                tree.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable
                              | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)

                files_count += 1

        try:
            add_leaves(parent, path)
        except FileNotFoundError:
            self.load_projects()
            self.open_project(project_path)

        parent.sortItems(0, Qt.AscendingOrder)
        parent.path = path
        parent.setHeaderLabel(
            f"{os.path.split(path)[1]} [{files_count} files / {dir_count} dirs]")

        if os.path.exists(os.path.join(path, BCIFR_FILE)):
            bcifr = pickle.load(open(os.path.join(path, BCIFR_FILE), 'rb'))
            files = list(bcifr['files'])
            parent.setHeaderLabel(
                f"{bcifr['name']} [{files_count} files / {dir_count} dirs]")

            if 'main.py' in files:
                files.pop(files.index('main.py'))

            self.load_script_in_textedit(os.path.join(path, 'main.py'))
            for file in files:
                if file.endswith('.py') or file.endswith('.css'):
                    if os.path.exists(os.path.join(path, file)):
                        self.load_script_in_textedit(
                            os.path.join(path, file))
            self.core.show_interface('Development')
        else:
            if os.path.exists(os.path.join(path, 'main.py')):
                self.load_script_in_textedit(os.path.join(path, 'main.py'))

        self.core.development.build_preview()
        self.core.show_interface('Development')

    # ----------------------------------------------------------------------
    def ignore_file(self, file: str) -> bool:
        """Evaluate if the file must be showed on the interface."""
        if file == '__pycache__':
            return True

        elif file.startswith('.'):
            return True

        elif file.endswith('.ipynb'):
            return True

        elif file.endswith('.png'):
            return True

        elif file == BCIFR_FILE:
            return True

        return False

    # ----------------------------------------------------------------------
    def show_script_in_textedit(self, module: PATH) -> None:
        """Focus editor with module."""
        for i in range(self.parent_frame.tabWidget_project.count()):
            editor = self.parent_frame.tabWidget_project.widget(i)
            if editor.path == module:
                self.parent_frame.tabWidget_project.setCurrentIndex(i)
                return

    # ----------------------------------------------------------------------
    def load_script_in_textedit(self, module: PATH) -> None:
        """Build editor with autocompleter and syntax highlighters."""
        editor = BCIEditor(linenumber=self.parent_frame.textEdit_linenumber,
                           extension=os.path.splitext(module)[1])

        tab = self.parent_frame.tabWidget_project.addTab(
            editor, os.path.split(module)[1])
        self.parent_frame.tabWidget_project.widget(
            tab).setContentsMargins(0, 0, 0, 0)
        self.parent_frame.tabWidget_project.widget(tab).editor = editor
        with open(module, 'r') as file:
            content = file.read()
            editor.setPlainText(content)
            editor.path = module
            editor.module = module

            # if LINE_DELIVERY in content:
            # completer = Autocompleter(mode='stimuli')
            # editor.set_completer(completer)
            # elif LINE_VISUALIZATION in content:
            # completer = Autocompleter(mode='visualization')
            # editor.set_completer(completer)
            # elif LINE_ANALYSIS in content:
            # completer = Autocompleter(mode='analysis')
            # editor.set_completer(completer)

            editor.textChanged.connect(lambda: self.parent_frame.tabWidget_project.setTabText(
                tab, f"{self.parent_frame.tabWidget_project.tabText(tab).strip('*')}*"))

        parent = os.path.split(module)[0]

        files = []
        for i in range(self.parent_frame.tabWidget_project.count()):
            files.append(self.parent_frame.tabWidget_project.tabText(i))

        bcifr = pickle.load(open(os.path.join(parent, BCIFR_FILE), 'rb'))
        bcifr['files'] = set(files)
        pickle.dump(bcifr, open(os.path.join(parent, BCIFR_FILE), 'wb'))

        if module not in self.project_files:
            self.project_files.append(module)

    # ----------------------------------------------------------------------
    def show_create_project_dialog(self) -> None:
        """Dialog to create new project."""
        file = os.path.join(
            os.environ['BCISTREAM_ROOT'], 'framework', 'qtgui', 'new_project.ui')
        project = QUiLoader().load(file, self.parent_frame)
        project.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(
            lambda evt: self.create_project(project.lineEdit_project_name.text(),
                                            project.radioButton_visualization.isChecked(),
                                            project.radioButton_stimulus_delivery.isChecked(),
                                            project.radioButton_data_analysis.isChecked()))

        project.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(
            lambda evt: project.destroy())
        project.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(
            lambda evt: project.destroy())

        project.lineEdit_project_name.textChanged.connect(
            lambda str_:
            project.buttonBox.button(QDialogButtonBox.Ok).setDisabled(os.path.isdir(
                os.path.join(self.projects_dir, str_))))

        center = QDesktopWidget().availableGeometry().center()
        geometry = project.frameGeometry()
        geometry.moveCenter(center)
        project.move(geometry.topLeft())

        project.show()

    # ----------------------------------------------------------------------
    def create_project(self, project_name: str, visualization: bool = False, stimulus: bool = False, analysis: bool = False) -> None:
        """Create a new project with a template and open it."""
        icon = QIcon()
        icon_name = 'icon_sti'

        if visualization:
            icon_name = 'icon_viz'
            item = QListWidgetItem(
                self.parent_frame.listWidget_projects_visualizations)
            default_project = '_default_visualization'
            self.mode = 'visualization'
        elif stimulus:
            icon_name = 'icon_sti'
            item = QListWidgetItem(
                self.parent_frame.listWidget_projects_delivery)
            default_project = '_default_stimuli_delivery'
            self.mode = 'delivery'
        elif analysis:
            icon_name = 'icon_ana'
            item = QListWidgetItem(
                self.parent_frame.listWidget_projects_analysis)
            default_project = '_default_data_analysis'
            self.mode = 'analysis'

        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable
                      | Qt.ItemIsDragEnabled | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        item.setText(project_name)
        item.previous_name = project_name
        item.path = self.normalize_path(project_name)

        ext = 0
        while item.path in os.listdir(self.projects_dir):
            ext += 1
            item.path = f"{self.normalize_path(project_name)}{ext}"

        icon.addFile(f"bci:primary/{icon_name}.svg",
                     QSize(), QIcon.Normal, QIcon.Off)
        item.setIcon(icon)
        item.icon_name = icon_name

        source = os.path.join(os.getenv('BCISTREAM_ROOT'),
                              'default_extensions', default_project)
        target = os.path.join(self.projects_dir, item.path)
        shutil.copytree(source, target)

        pickle.dump({'name': project_name, 'files': []}, open(
            os.path.join(self.projects_dir, item.path, BCIFR_FILE), 'wb'))
        self.open_project(item.path)

    # ----------------------------------------------------------------------
    def remove_project(self, evt) -> None:
        """Remove project from directory."""
        items = [self.parent_frame.listWidget_projects_delivery.currentItem(),
                 self.parent_frame.listWidget_projects_visualizations.currentItem(),
                 self.parent_frame.listWidget_projects_analysis.currentItem(),
                 ]
        selected_project = list(filter(None, items))[0]

        if hasattr(self.parent_frame.treeWidget_project, 'project_name') and self.parent_frame.treeWidget_project.project_name == selected_project.text():
            self.parent_frame.tabWidget_project.clear()
            self.core.show_interface('Home')
            self.parent_frame.actionDevelopment.setEnabled(False)

        shutil.rmtree(os.path.join(
            self.projects_dir, selected_project.path))
        self.load_projects()

    # ----------------------------------------------------------------------
    def add_file(self) -> None:
        """Create a new file in the project directory, by default is a Pyhon file."""
        if selected := self.parent_frame.treeWidget_project.currentItem():
            path = selected.path
        else:
            path = os.path.join(self.projects_dir,
                                self.parent_frame.treeWidget_project.project_name)

        if os.path.isfile(path):
            path = os.path.dirname(path)
        index = 0

        while True:
            filename = os.path.join(path, f'new_file-{index}.py')
            if os.path.exists(filename):
                index += 1
            else:
                file = open(filename, 'wb')
                file.close()
                break

        self.open_project(self.parent_frame.treeWidget_project.project_name)

    # ----------------------------------------------------------------------
    def add_folder(self) -> None:
        """Create new folder in the project directory."""
        if selected := self.parent_frame.treeWidget_project.currentItem():
            path = selected.path
        else:
            path = os.path.join(self.projects_dir,
                                self.parent_frame.treeWidget_project.project_name)

        if os.path.isfile(path):
            path = os.path.dirname(path)
        index = 0

        while True:
            filename = os.path.join(path, f'new_directory-{index}')
            if os.path.exists(filename):
                index += 1
            else:
                os.mkdir(filename)
                break

        self.open_project(self.parent_frame.treeWidget_project.project_name)

    # ----------------------------------------------------------------------
    def remove_file(self) -> None:
        """Remove file from project directory."""
        if selected := self.parent_frame.treeWidget_project.currentItem():
            path = selected.path
            self.close_tab(path)
        else:
            return

        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)

        self.open_project(self.parent_frame.treeWidget_project.project_name)

    # ----------------------------------------------------------------------
    def project_renamed(self, evt) -> None:
        """Rename project directory."""

        if (not evt.text()) or (not hasattr(evt, 'previous_name')):
            return

        if (evt.text() == evt.previous_name):
            return

        new_name = evt.text().strip()
        new_path = self.normalize_path(new_name)

        ext = 0
        while new_path in os.listdir(self.projects_dir):
            ext += 1
            new_path = f"{self.normalize_path(new_name)}{ext}"

        # name = evt.previous_name
        # if name := getattr(evt, 'previous_name', False):
            # if name.strip() != new_name:
        shutil.move(os.path.join(self.projects_dir, evt.path),
                    os.path.join(self.projects_dir, new_path))
        evt.previous_name = new_name
        evt.path = new_path

        bcifr = pickle.load(
            open(os.path.join(self.projects_dir, new_path, BCIFR_FILE), 'rb'))
        bcifr['name'] = new_name
        pickle.dump(bcifr, open(os.path.join(
            self.projects_dir, new_path, BCIFR_FILE), 'wb'))

    # ----------------------------------------------------------------------
    def project_file_renamed(self, evt) -> None:
        """Rename file."""
        if hasattr(evt, 'previous_name'):
            if evt.previous_name != evt.text(0):
                new_path = os.path.join(
                    os.path.split(evt.path)[0], evt.text(0))
                shutil.move(evt.path, new_path)

                if evt.path in self.project_files:
                    for i in range(self.parent_frame.tabWidget_project.count()):
                        editor = self.parent_frame.tabWidget_project.widget(
                            i)
                        if editor.path == evt.path:
                            self.parent_frame.tabWidget_project.setTabText(
                                i, evt.text(0))
                            editor.path = new_path
                            break

                    self.project_files[self.project_files.index(
                        evt.path)] = new_path

                evt.previous_name = evt.text(0)
                evt.path = new_path

    # ----------------------------------------------------------------------
    def close_tab(self, evt) -> None:
        """Close file."""
        if isinstance(evt, (int, float)):
            editor_closed = self.parent_frame.tabWidget_project.widget(evt)
            try:
                self.project_files.pop(
                    self.project_files.index(editor_closed.path))
            except:
                pass
            self.parent_frame.tabWidget_project.removeTab(evt)

        elif isinstance(evt, (str,)):
            if evt in self.project_files:
                for i in range(self.parent_frame.tabWidget_project.count()):
                    editor = self.parent_frame.tabWidget_project.widget(i)
                    if editor.path == evt:
                        return self.close_tab(i)

        if self.parent_frame.tabWidget_project.count():
            self.parent_frame.actionDevelopment.setEnabled(True)
        else:
            self.core.show_interface('Home')
            self.parent_frame.actionDevelopment.setEnabled(False)
