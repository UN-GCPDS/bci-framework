import os
# import sys

from PySide2.QtGui import QIcon
from PySide2.QtCore import Qt, QSize
from PySide2.QtWidgets import QListWidgetItem, QTreeWidgetItem, QDialogButtonBox, QWidget
# from bci_framework.highlighters import PythonHighlighter
from bci_framework.editor import BCIEditor

from PySide2.QtUiTools import QUiLoader
import shutil


########################################################################
class Projects:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, parent, core):
        """Constructor"""

        self.project_files = []

        self.parent = parent
        self.core = core

        self.parent.stackedWidget_projects.setCurrentWidget(getattr(self.parent, "page_projects"))

        self.load_projects()
        self.connect()

    # ----------------------------------------------------------------------
    def connect(self):
        """"""
        self.parent.pushButton_projects.clicked.connect(lambda evt: self.parent.stackedWidget_projects.setCurrentWidget(getattr(self.parent, "page_projects")))
        # self.parent.pushButton_files.clicked.connect(lambda evt: self.parent.stackedWidget_projects.setCurrentWidget(getattr(self.parent, "page_projects_files")))
        self.parent.listWidget_projects.itemDoubleClicked.connect(lambda evt: self.open_project(evt.text()))
        self.parent.listWidget_projects.itemChanged.connect(self.project_renamed)

        self.parent.treeWidget_project.itemDoubleClicked.connect(self.open_script)
        self.parent.treeWidget_project.itemChanged.connect(self.project_file_renamed)
        self.parent.pushButton_projects_add_file.clicked.connect(self.add_file)
        self.parent.pushButton_projects_add_folder.clicked.connect(self.add_folder)
        self.parent.pushButton_projects_remove.clicked.connect(self.remove)

        self.parent.pushButton_add_project.clicked.connect(self.show_create_project_dialog)
        self.parent.pushButton_remove_project.clicked.connect(self.remove_project)

        self.parent.tabWidget_project.tabCloseRequested.connect(self.close_tab)
        self.parent.tabWidget_project.currentChanged.connect(self.tab_changed)

    # ----------------------------------------------------------------------
    def tab_changed(self, index):
        """"""
        editor = self.parent.tabWidget_project.widget(index)
        editor.update_linenumber()

    # ----------------------------------------------------------------------
    def open_script(self, item):
        """"""
        if not item.path in self.project_files:
            self.project_files.append(item.path)
            self.load_script_in_textedit(item.path)
        # else:
        self.show_script_in_textedit(item.path)
        self.core.show_interface('Development')

    # ----------------------------------------------------------------------
    def load_projects(self):
        """"""
        self.parent.listWidget_projects.clear()

        projects = os.listdir('default_projects')

        projects = filter(lambda f: os.path.isdir(os.path.join('default_projects', f)), projects)
        projects = filter(lambda f: not f.startswith('__'), projects)

        for project in projects:

            item = QListWidgetItem(self.parent.listWidget_projects)
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsDragEnabled | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item.setText(project)
            item.previous_name = project

            with open(os.path.join('default_projects', project, project + '.py'), 'r') as file:
                lines = file.readlines()

                modules = {'FigureStream': 'icon_viz',
                           'StimuliServer': 'icon_sti',
                           }
                icon_name = 'icon_dev'
                for module in modules:
                    if [line for line in lines if f'import {module}' in ' '.join(line.split()) and not line.strip().startswith("#")]:
                        icon_name = modules[module]
                        break

            icon = QIcon()
            icon.addFile(f":/bci/icons/bci/{icon_name}.svg", QSize(), QIcon.Normal, QIcon.Off)
            item.setIcon(icon)

    # ----------------------------------------------------------------------
    def open_project(self, project_name):
        """"""
        global files_count, dir_count, project_name_

        self.parent.stackedWidget_projects.setCurrentWidget(getattr(self.parent, "page_projects_files"))

        path = os.path.join('default_projects', project_name)

        # sys.path.append(path)
        parent = self.parent.treeWidget_project
        parent.project_name = project_name

        parent.clear()

        # tree = QTreeWidgetItem(parent)
        # tree.setText(0, '../Projects')
        # tree.path = "__action"

        files_count = 0
        dir_count = 0
        open_item = None
        project_name_ = project_name

        def add_leaves(parent, path):
            global files_count, dir_count, project_name_

            # for file in os.listdir(path):

            files = sorted(filter(lambda f: os.path.isfile(os.path.join(path, f)), os.listdir(path)))
            dirs = sorted(filter(lambda f: os.path.isdir(os.path.join(path, f)), os.listdir(path)))

            # print(dirs)
            # print(files)

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

                tree = QTreeWidgetItem(parent)
                tree.setText(0, file)
                tree.path = os.path.join(path, file)
                tree.previous_name = file
                if project_name_ + '.py' == file:
                    self.open_script(tree)
                    # open_item = tree

                tree.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)

                files_count += 1

                # print(file)

        add_leaves(parent, path)
        parent.sortItems(0, Qt.AscendingOrder)
        parent.path = path
        parent.setHeaderLabel(f"{os.path.split(path)[1]} [{files_count} files / {dir_count} dirs]")

        # if open_item:
            # self.open_script(open_item)

    # ----------------------------------------------------------------------
    def load_scripts(self):
        """"""
        projects = os.listdir('default_projects')
        projects = filter(lambda d: os.path.isdir(os.path.join('default_projects', d)) and os.path.isfile(os.path.join('default_projects', d, f"{d}.py")), projects)

        self.available_scripts = {'visualization': {},
                                  'stimuli': {},
                                  }

        for project in projects:

            path = '.'.join(['default_projects', project, project])
            module = __import__(path, fromlist=[None])

            if hasattr(module, 'SCRIPT'):
                if mode := module.SCRIPT.get('mode', False):

                    name = module.SCRIPT.get('name', 'NO NAME')
                    self.available_scripts[mode][name] = path  # os.path.join(*scripts, file)

    # ----------------------------------------------------------------------
    def show_script_in_textedit(self, module):
        """"""
        for i in range(self.parent.tabWidget_project.count()):
            editor = self.parent.tabWidget_project.widget(i)
            if editor.path == module:
                self.parent.tabWidget_project.setCurrentIndex(i)
                return

    # ----------------------------------------------------------------------
    def load_script_in_textedit(self, module):
        """"""
        editor = BCIEditor(linenumber=self.parent.textEdit_linenumber, extension=os.path.splitext(module)[1])

        tab = self.parent.tabWidget_project.addTab(editor, os.path.split(module)[1])
        self.parent.tabWidget_project.widget(tab).setContentsMargins(0, 0, 0, 0)
        self.parent.tabWidget_project.widget(tab).editor = editor
        with open(module, 'r') as file:
            editor.setPlainText(file.read())
            editor.path = module
            editor.module = module

            editor.textChanged.connect(lambda: self.parent.tabWidget_project.setTabText(tab, f"{self.parent.tabWidget_project.tabText(tab).strip('*')}*"))

    # ----------------------------------------------------------------------

    def show_create_project_dialog(self):
        """"""

        project = QUiLoader().load('bci_framework/qtgui/new_project.ui', self.parent)
        project.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(lambda evt: self.create_project(project.lineEdit_project_name.text(),
                                                                                                      project.radioButton_visualization.isChecked(),
                                                                                                      project.radioButton_stimulus_delivery.isChecked()))

        project.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(lambda evt: project.destroy())
        project.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(lambda evt: project.destroy())

        project.lineEdit_project_name.textChanged.connect(lambda str_:
                                                          project.buttonBox.button(QDialogButtonBox.Ok).setDisabled(os.path.isdir(
                                                              os.path.join('default_projects', str_))))

        project.show()

    # ----------------------------------------------------------------------

    def create_project(self, project_name, visualization, stimulus):
        """"""

        item = QListWidgetItem(self.parent.listWidget_projects)
        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsDragEnabled | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        item.setText(project_name)
        item.previous_name = project_name

        icon = QIcon()
        icon.addFile(u":/bci/icons/bci/icon_sti.svg", QSize(), QIcon.Normal, QIcon.Off)
        item.setIcon(icon)

        os.mkdir(os.path.join('default_projects', project_name))
        with open(os.path.join('default_projects', project_name, f'{project_name}.py'), 'wb') as file:
            file.write(b'')

    # ----------------------------------------------------------------------

    def remove_project(self, evt):
        """"""

        selected_project = self.parent.listWidget_projects.currentItem().text()
        shutil.rmtree(os.path.join('default_projects', selected_project))
        self.load_projects()

    # ----------------------------------------------------------------------
    def add_file(self):
        """"""
        if selected := self.parent.treeWidget_project.currentItem():
            path = selected.path
        else:
            path = os.path.join('default_projects', self.parent.treeWidget_project.project_name)

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

        self.open_project(self.parent.treeWidget_project.project_name)

    # ----------------------------------------------------------------------
    def add_folder(self):
        """"""
        if selected := self.parent.treeWidget_project.currentItem():
            path = selected.path
        else:
            path = os.path.join('default_projects', self.parent.treeWidget_project.project_name)

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

        self.open_project(self.parent.treeWidget_project.project_name)

    # ----------------------------------------------------------------------
    def remove(self):
        """"""
        if selected := self.parent.treeWidget_project.currentItem():
            path = selected.path
            self.close_tab(path)
        else:
            return

        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)

        self.open_project(self.parent.treeWidget_project.project_name)

    # ----------------------------------------------------------------------
    def project_renamed(self, evt):
        """"""
        if hasattr(evt, 'previous_name'):
            if evt.previous_name != evt.text():
                shutil.move(os.path.join('default_projects', evt.previous_name, f"{evt.previous_name}.py"), os.path.join('default_projects', evt.previous_name, f"{evt.text()}.py"))
                shutil.move(os.path.join('default_projects', evt.previous_name), os.path.join('default_projects', evt.text()))
                evt.previous_name == evt.text()

    # ----------------------------------------------------------------------
    def project_file_renamed(self, evt):
        """"""
        if hasattr(evt, 'previous_name'):
            if evt.previous_name != evt.text(0):
                new_path = os.path.join(os.path.split(evt.path)[0], evt.text(0))
                shutil.move(evt.path, new_path)

                if evt.path in self.project_files:
                    for i in range(self.parent.tabWidget_project.count()):
                        editor = self.parent.tabWidget_project.widget(i)
                        if editor.path == evt.path:
                            self.parent.tabWidget_project.setTabText(i, evt.text(0))
                            editor.path = new_path
                            break

                    self.project_files[self.project_files.index(evt.path)] = new_path

                evt.previous_name = evt.text(0)
                evt.path = new_path

    # ----------------------------------------------------------------------
    def close_tab(self, evt):
        """"""
        if isinstance(evt, (int, float)):
            editor_closed = self.parent.tabWidget_project.widget(evt)
            self.project_files.pop(self.project_files.index(editor_closed.path))
            self.parent.tabWidget_project.removeTab(evt)

        elif isinstance(evt, (str,)):
            if evt in self.project_files:
                for i in range(self.parent.tabWidget_project.count()):
                    editor = self.parent.tabWidget_project.widget(i)
                    if editor.path == evt:
                        return self.close_tab(i)

