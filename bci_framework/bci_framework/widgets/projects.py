import os
import sys
import pickle

from PySide2.QtGui import QIcon
from PySide2.QtCore import Qt, QSize
from PySide2.QtWidgets import QListWidgetItem, QTreeWidgetItem, QDialogButtonBox, QDesktopWidget
from PySide2.QtUiTools import QUiLoader

import shutil

from ..editor import BCIEditor, Autocompleter


########################################################################
class Projects:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, parent, core):
        """Constructor"""

        self.project_files = []

        self.parent_frame = parent
        self.core = core

        if '--local' in sys.argv:
            self.projects_dir = os.path.join(
                os.getenv('BCISTREAM_ROOT'), 'default_projects')
        else:
            self.projects_dir = os.path.join(
                os.getenv('BCISTREAM_HOME'), 'projects')

        self.parent_frame.label_projects_path.setText(self.projects_dir)
        self.parent_frame.label_projects_path.setStyleSheet(
            '*{font-family: "DejaVu Sans Mono";}')

        self.parent_frame.stackedWidget_projects.setCurrentWidget(
            getattr(self.parent_frame, "page_projects"))

        self.load_projects()
        self.connect()

    # ----------------------------------------------------------------------
    def connect(self):
        """"""
        self.parent_frame.pushButton_projects.clicked.connect(
            lambda evt: self.parent_frame.stackedWidget_projects.setCurrentWidget(getattr(self.parent_frame, "page_projects")))

        self.parent_frame.pushButton_projects.clicked.connect(lambda evt:
                                                              self.core.development.stop_preview())

        self.parent_frame.listWidget_projects_visualizations.itemDoubleClicked.connect(
            lambda evt: self.open_project(evt.text()))
        self.parent_frame.listWidget_projects_delivery.itemDoubleClicked.connect(
            lambda evt: self.open_project(evt.text()))

        self.parent_frame.checkBox_projects_show_tutorials.stateChanged.connect(
            self.load_projects)
        self.parent_frame.listWidget_projects_visualizations.itemClicked.connect(
            self.there_can_only_be_one)
        self.parent_frame.listWidget_projects_delivery.itemClicked.connect(
            self.there_can_only_be_one)
        self.parent_frame.listWidget_projects_visualizations.itemChanged.connect(
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
            self.remove)
        self.parent_frame.pushButton_add_project.clicked.connect(
            self.show_create_project_dialog)
        self.parent_frame.pushButton_remove_project.clicked.connect(
            self.remove_project)
        self.parent_frame.tabWidget_project.tabCloseRequested.connect(
            self.close_tab)
        self.parent_frame.tabWidget_project.currentChanged.connect(
            self.tab_changed)

    # ----------------------------------------------------------------------
    def there_can_only_be_one(self, event):
        """"""
        self.parent_frame.listWidget_projects_delivery.clearSelection()
        self.parent_frame.listWidget_projects_visualizations.clearSelection()
        event.setSelected(True)

    # ----------------------------------------------------------------------
    def tab_changed(self, index):
        """"""
        if editor := self.parent_frame.tabWidget_project.widget(index):
            editor.update_linenumber()

    # ----------------------------------------------------------------------
    def open_script(self, item):
        """"""
        if not item.path in self.project_files:
            self.load_script_in_textedit(item.path)
        self.show_script_in_textedit(item.path)
        self.core.show_interface('Development')
        self.parent_frame.actionDevelopment.setEnabled(True)

    # ----------------------------------------------------------------------
    def load_projects(self):
        """"""
        self.parent_frame.listWidget_projects_visualizations.clear()
        self.parent_frame.listWidget_projects_delivery.clear()

        projects = os.listdir(self.projects_dir)
        projects = filter(lambda f: os.path.isdir(
            os.path.join(self.projects_dir, f)), projects)
        projects = filter(lambda f: not f.startswith('__'), projects)

        if (not self.parent_frame.checkBox_projects_show_tutorials.isChecked()) and ('--local' in sys.argv):
            projects = filter(lambda f: not f.startswith('_'), projects)

        projects = sorted(list(projects))

        for project in projects:

            if project.startswith('Tutorial |') and not self.parent_frame.checkBox_projects_show_tutorials.isChecked():
                continue

            with open(os.path.join(self.projects_dir, project, 'main.py'), 'r') as file:
                lines = file.readlines()

                modules = {'FigureStream': (self.parent_frame.listWidget_projects_visualizations, 'icon_viz'),
                           'StimuliServer': (self.parent_frame.listWidget_projects_delivery, 'icon_sti'),
                           }
                for module in modules:
                    if [line for line in lines if f'import {module}' in ' '.join(line.split()) and not line.strip().startswith("#")]:
                        widget, icon_name = modules[module]
                        break

            item = QListWidgetItem(widget)
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable
                          | Qt.ItemIsDragEnabled | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item.setText(project)
            item.previous_name = project

            icon = QIcon()
            icon.addFile(
                f"bci:/primary/{icon_name}.svg", QSize(), QIcon.Normal, QIcon.Off)
            item.setIcon(icon)
            item.icon_name = icon_name

    # ----------------------------------------------------------------------
    def open_project(self, project_name):
        """"""
        global files_count, dir_count, project_name_

        if self.parent_frame.listWidget_projects_visualizations.selectedItems():
            self.mode = 'visualization'
        elif self.parent_frame.listWidget_projects_delivery.selectedItems():
            self.mode = 'stimuli'

        self.parent_frame.stackedWidget_projects.setCurrentWidget(
            getattr(self.parent_frame, "page_projects_files"))

        path = os.path.join(self.projects_dir, project_name)
        # path = project_name

        self.parent_frame.tabWidget_project.clear()

        parent = self.parent_frame.treeWidget_project
        parent.project_name = project_name
        parent.clear()

        files_count = 0
        dir_count = 0
        open_item = None
        project_name_ = project_name

        def add_leaves(parent, path):
            global files_count, dir_count, project_name_

            files = sorted(filter(lambda f: os.path.isfile(
                os.path.join(path, f)), os.listdir(path)))
            dirs = sorted(filter(lambda f: os.path.isdir(
                os.path.join(path, f)), os.listdir(path)))

            for file in dirs:
                if file == '__pycache__':
                    continue

                tree = QTreeWidgetItem(parent)
                tree.setText(0, file)
                tree.path = os.path.join(path, file)
                tree.previous_name = file
                add_leaves(tree, os.path.join(path, file))
                dir_count += 1

                # print(file)

            for file in files:

                if file.startswith('.'):
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
            self.open_project(project_name)

        parent.sortItems(0, Qt.AscendingOrder)
        parent.path = path
        parent.setHeaderLabel(
            f"{os.path.split(path)[1]} [{files_count} files / {dir_count} dirs]")

        if os.path.exists(os.path.join(path, '.bcifr')):
            files = list(
                set(pickle.load(open(os.path.join(path, '.bcifr'), 'rb'))))

            if 'main.py' in files:
                files.pop(files.index('main.py'))

            self.load_script_in_textedit(os.path.join(path, 'main.py'))
            for file in files:
                if os.path.exists(os.path.join(path, file)):
                    self.load_script_in_textedit(os.path.join(path, file))
            self.core.show_interface('Development')
        else:
            if os.path.exists(os.path.join(path, 'main.py')):
                self.load_script_in_textedit(os.path.join(path, 'main.py'))

        self.core.development.build_preview()
        self.core.show_interface('Development')

    # ----------------------------------------------------------------------
    def load_scripts(self):
        """"""
        projects = os.listdir(self.projects_dir)
        projects = filter(lambda d: os.path.isdir(os.path.join(self.projects_dir, d)) and os.path.isfile(
            os.path.join(self.projects_dir, d, f"main.py")), projects)

        self.available_scripts = {'visualization': {},
                                  'stimuli': {},
                                  }

        for project in projects:

            path = '.'.join([self.projects_dir, project, project])
            module = __import__(path, fromlist=[None])

            if hasattr(module, 'SCRIPT'):
                if mode := module.SCRIPT.get('mode', False):

                    name = module.SCRIPT.get('name', 'NO NAME')
                    # os.path.join(*scripts, file)
                    self.available_scripts[mode][name] = path

    # ----------------------------------------------------------------------
    def show_script_in_textedit(self, module):
        """"""
        for i in range(self.parent_frame.tabWidget_project.count()):
            editor = self.parent_frame.tabWidget_project.widget(i)
            if editor.path == module:
                self.parent_frame.tabWidget_project.setCurrentIndex(i)
                return

    # ----------------------------------------------------------------------
    def load_script_in_textedit(self, module):
        """"""
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

            if 'bci_framework.extensions.stimuli_delivery' in content:
                completer = Autocompleter(mode='stimuli')
                editor.setCompleter(completer)
            elif 'bci_framework.projects.figure' in content:
                completer = Autocompleter(mode='visualization')
                editor.setCompleter(completer)

            editor.textChanged.connect(lambda: self.parent_frame.tabWidget_project.setTabText(
                tab, f"{self.parent_frame.tabWidget_project.tabText(tab).strip('*')}*"))

        parent = os.path.split(module)[0]

        files = []
        for i in range(self.parent_frame.tabWidget_project.count()):
            files.append(self.parent_frame.tabWidget_project.tabText(i))
        pickle.dump(set(files), open(os.path.join(parent, '.bcifr'), 'wb'))

        if module not in self.project_files:
            self.project_files.append(module)

    # ----------------------------------------------------------------------
    def show_create_project_dialog(self):
        """"""
        file = os.path.join(
            os.environ['BCISTREAM_ROOT'], 'bci_framework', 'qtgui', 'new_project.ui')
        project = QUiLoader().load(file, self.parent_frame)
        project.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(
            lambda evt: self.create_project(project.lineEdit_project_name.text(),
                                            project.radioButton_visualization.isChecked(),
                                            project.radioButton_stimulus_delivery.isChecked()))

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
    def create_project(self, project_name, visualization, stimulus):
        """"""
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

        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable
                      | Qt.ItemIsDragEnabled | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        item.setText(project_name)
        item.previous_name = project_name

        icon.addFile(f"bci:primary/{icon_name}.svg",
                     QSize(), QIcon.Normal, QIcon.Off)
        item.setIcon(icon)
        item.icon_name = icon_name

        source = os.path.join(os.getenv('BCISTREAM_ROOT'),
                              'default_projects', default_project)
        target = os.path.join(self.projects_dir, project_name)
        shutil.copytree(source, target)

        self.open_project(project_name)

    # ----------------------------------------------------------------------
    def remove_project(self, evt):
        """"""
        items = [self.parent_frame.listWidget_projects_delivery.currentItem(),
                 self.parent_frame.listWidget_projects_visualizations.currentItem(),
                 ]
        selected_project = list(filter(None, items))[0]
        shutil.rmtree(os.path.join(
            self.projects_dir, selected_project.text()))
        self.load_projects()

    # ----------------------------------------------------------------------
    def add_file(self):
        """"""
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
    def add_folder(self):
        """"""
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
    def remove(self):
        """"""
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
    def project_renamed(self, evt):
        """"""
        if hasattr(evt, 'previous_name'):
            if evt.previous_name.strip() != evt.text().strip():
                shutil.move(os.path.join(self.projects_dir, evt.previous_name), os.path.join(
                    self.projects_dir, evt.text()))
                evt.previous_name == evt.text()

    # ----------------------------------------------------------------------
    def project_file_renamed(self, evt):
        """"""
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
    def close_tab(self, evt):
        """"""
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

