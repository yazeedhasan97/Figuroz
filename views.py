import re
import sys, json, glob, os
from datetime import datetime
from PIL import ImageGrab

from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QVBoxLayout, QHBoxLayout, QPushButton, QGridLayout, \
    QLabel, QStackedLayout, QMenu, QMainWindow, QAction, QFileDialog, QLayout
from PyQt5.QtGui import QIcon

# from PySide2.QtCore import *
# from PySide2.QtWidgets import *


TASKS = 'tasks'
SUBS = 'tasks'
STATE = 'state'
TOTAL_TIME = 'total_time'
TIME = 'time'
DESCRIPTION = 'description'
WORK_TODAY = 'work_today'
ACTIVE_TASK = 'active_task'
NAME = 'name'


class MainApp(QMainWindow):
    def __init__(self, title, left, top, height, parent=None):
        super(QMainWindow, self).__init__(parent)
        self.__init_ui(title, left, top, height)
        self.__createMenuBar()
        self.__init_layouts()

    def __init_ui(self, title, left, top, height):
        self.setWindowTitle(title)
        self.setGeometry(left, top, int(height * 1.4), height)

    def __init_layouts(self):
        # Define The Project Description Layout
        self.title_layout = QGridLayout()
        self.lbl_pr_name = QLabel('Project: ')
        self.title_layout.addWidget(self.lbl_pr_name, 0, 0)

        self.lbl_pr_state = QLabel('State: ')
        self.title_layout.addWidget(self.lbl_pr_state, 1, 0)

        self.lbl_pr_total_time = QLabel('Total Time: ', )
        self.title_layout.addWidget(self.lbl_pr_total_time, 0, 1)

        self.lbl_pr_active_task = QLabel('Current Active Task: ')
        self.title_layout.addWidget(self.lbl_pr_active_task, 1, 1)

        # Define The Project TASKS and SUB-TASKS Layout

        self.tasks_layout = QVBoxLayout()
        self.sub_tasks_layout = QVBoxLayout()
        self.sub_tasks_lst = QListWidget()
        self.sub_tasks_layout.addWidget(self.sub_tasks_lst)

        self.lower_layout = QHBoxLayout()
        self.lower_layout.addLayout(self.tasks_layout)
        self.lower_layout.addLayout(self.sub_tasks_layout)

        # self.main_layout = QVBoxLayout()
        self.main_widget = QWidget()
        self.layout = QVBoxLayout()
        self.layout.sizeConstraint = QLayout.SetDefaultConstraint

        self.layout.addLayout(self.title_layout)
        self.layout.addLayout(self.lower_layout)

        self.main_widget.setLayout(self.layout)
        self.setCentralWidget(self.main_widget)

    def __createMenuBar(self):
        menuBar = self.menuBar()
        # Creating menus using a QMenu object
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)

        self.open_action = QAction("&Open...", self)
        self.open_action.triggered.connect(self.open_file)
        fileMenu.addAction(self.open_action)
        fileMenu.addSeparator()

        self.start_action = QAction("&Start", self)
        self.start_action.triggered.connect(self.start_timer)
        fileMenu.addAction(self.start_action)

        self.pause_action = QAction("&Pause", self)
        self.pause_action.triggered.connect(self.pause_timer)
        fileMenu.addAction(self.pause_action)

        self.reset_action = QAction("&Reset...", self)
        self.reset_action.triggered.connect(self.reset_timer)
        fileMenu.addAction(self.reset_action)
        fileMenu.addSeparator()

        self.screenshot_action = QAction("&Screenshot...", self)
        self.screenshot_action.triggered.connect(self.take_screenshot)
        fileMenu.addAction(self.screenshot_action)
        fileMenu.addSeparator()

        self.exit_action = QAction("&Exit", self)
        self.exit_action.triggered.connect(self.close)
        fileMenu.addAction(self.exit_action)

    def take_screenshot(self):
        snapshot = ImageGrab.grab()
        snapshot.save(f'./Image_{datetime.now():%Y%m%d_%H%H%S}.png')
        pass

    def start_timer(self):
        pass

    def pause_timer(self):
        pass

    def reset_timer(self):
        pass

    def open_file(self):
        path = QFileDialog.getOpenFileName(self, "Open File", './', 'All Files (*);;JSON Files(*.json)')

        if path and path[0].endswith('.json'):
            self.project = self.load_project(path[0])
            self.lbl_pr_name.setText(f'Project: {self.project[NAME]}')
            self.lbl_pr_state.setText(f'State: {self.project[STATE]}')
            self.lbl_pr_total_time.setText(f'Total Time: {self.project[TOTAL_TIME]}')
            self.lbl_pr_active_task.setText(f'Current Active Task: {self.project[ACTIVE_TASK]}')
            self.load_tasks()
        else:
            raise FileNotFoundError('The selected JSON file is unable to load.')

    def load_project(self, path):
        with open(path) as file:
            project = json.load(file)
        return project

    def load_tasks(self):
        for i in reversed(range(self.tasks_layout.count() - 1)):
            self.tasks_layout.takeAt(i).widget().deleteLater()

        self.available_tasks = {}
        for task in self.project[TASKS].keys():
            self.available_tasks[task] = QPushButton(task)
            self.tasks_layout.addWidget(self.available_tasks[task])

        self.connect_tasks_to_actions()
        pass

    def connect_tasks_to_actions(self):
        for task in self.available_tasks.keys():
            sub_tasks = self.project[TASKS][task][SUBS]
            self.available_tasks[task].clicked.connect(lambda x: self.load_sub_tasks(sub_tasks))
        pass

    def load_sub_tasks(self, sub_tasks_dct):
        self.sub_tasks_lst.clear()
        print(sub_tasks_dct)
        for sub in sub_tasks_dct.keys():
            print(sub)
            passed_time = sub_tasks_dct[sub][TIME]
            self.sub_tasks_lst.addItems([sub, passed_time])
        pass




# import ctypes
# user32 = ctypes.windll.User32
# lst = ['Unlocked']
# print('Unlocked')
# while True:
#     if user32.GetForegroundWindow() == 0: # check if the user changed the window he is working on
#         if lst[-1] != 'Locked':
#             lst.append('Locked')
#             print('Locked')
#     else:
#         if lst[-1] != 'Unlocked':
#             lst.append('Unlocked')
#             print('Unlocked')


# import psutil
#
# name = ''
# while True:
#     for proc in psutil.process_iter():
#         if proc.name() == "LogonUI.exe":
#             print("Locked")
#             break

