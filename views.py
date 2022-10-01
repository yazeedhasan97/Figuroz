import re
import sys, json, glob, os
from datetime import datetime
from PIL import ImageGrab

from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QVBoxLayout, QHBoxLayout, QPushButton, QGridLayout, \
    QLabel, QStackedLayout, QMenu, QMainWindow, QAction, QFileDialog, QLayout
from PyQt5.QtGui import QIcon

import main

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

import os.path
import pickle
import sys

import pandas as pd
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, QLineEdit, QGridLayout, QMessageBox, QCheckBox)
from qtwidgets import PasswordEdit

import db_models
from db import create_db_connection

REMEMBER_ME_FILE_PATH = './env/user.pkl'


class QClickableLabel(QLabel):
    def __init__(self, msg, whenClicked, parent=None):
        QLabel.__init__(
            self,
            msg,
            parent=parent
        )
        self._whenClicked = whenClicked

    def mouseReleaseEvent(self, event):
        self._whenClicked(event)


class ForgetPasswordForm(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """

    def __init__(self, parent=None):
        super().__init__()
        self.login_form = None
        self.parent = parent
        self.setWindowTitle('Forget Password Form')
        self.resize(500, 300)

        layout = QGridLayout()

        label_name = QLabel('<font size="4"> Email </font>')
        layout.addWidget(label_name, 0, 0)

        self.lineEdit_username = QLineEdit()
        self.lineEdit_username.setPlaceholderText('Please enter your Email')
        layout.addWidget(self.lineEdit_username, 0, 1, )

        button_login = QPushButton('Check')
        button_login.clicked.connect(self.check_password)
        layout.addWidget(button_login, 1, 0, 1, 1)

        button_login = QPushButton('Back')
        button_login.clicked.connect(self.return_to_login_page)
        layout.addWidget(button_login, 1, 2, )

        layout.setRowMinimumHeight(10, 75)
        layout.setContentsMargins(65, 65, 65, 65)
        self.setLayout(layout)

    def check_password(self):
        print('Do something')
        pass

    def return_to_login_page(self):
        self.parent.show()
        self.hide()
        self.destroy()
        # self = None
        del self
        pass


class LoginForm(QWidget):
    def __init__(self, ):
        super().__init__()
        self.forget_password_form = None
        self.main_screen = None
        self.setWindowTitle('Login Form')
        self.resize(500, 300)

        layout = QGridLayout()

        label_name = QLabel('<font size="4"> Username </font>')
        self.lineEdit_username = QLineEdit()
        self.lineEdit_username.setPlaceholderText('Please enter your username')
        layout.addWidget(label_name, 0, 0)
        layout.addWidget(self.lineEdit_username, 0, 2, )

        label_password = QLabel('<font size="4"> Password </font>')
        self.lineEdit_password = PasswordEdit()
        self.lineEdit_password.setEchoMode(QLineEdit.Password)
        self.lineEdit_password.setPlaceholderText('Please enter your password')
        layout.addWidget(label_password, 1, 0)
        layout.addWidget(self.lineEdit_password, 1, 2, )

        self.remember_me = QCheckBox('Remember me')
        layout.addWidget(self.remember_me, 2, 0)

        label_forget_password = QClickableLabel('<font size="3"> Forget Password? </font>', self.forget_password, )
        layout.addWidget(label_forget_password, 2, 2)

        button_login = QPushButton('Login')
        button_login.clicked.connect(self.check_password)
        layout.addWidget(button_login, 3, 0, 3, 3)
        layout.setRowMinimumHeight(2, 75)
        layout.setContentsMargins(65, 65, 65, 65)
        self.setLayout(layout)

        self.__try_remember_me_login()

    def check_password(self):
        msg = QMessageBox()
        name = self.lineEdit_username.text()
        password = self.lineEdit_password.text()
        if name is None or not name:
            msg.setText('Please enter a username.')
            msg.exec_()
            return

        if password is None or not password:
            msg.setText('Please enter a password.')
            msg.exec_()
            return

        conn = create_db_connection(host_config='local', config_path='env')
        df = conn.select(f"select * from Uzers where Name = '{name}' and Password = '{password}'")
        conn.close()

        if df.shape[0] == 0:
            msg.setText("Sorry, this user is not registered in teh system.")
            msg.exec_()
            return

        if password not in df['Password'].to_numpy():
            msg.setText('Incorrect Password.')
            msg.exec_()
            return

        user = db_models.User(
            company_id=df['companyId'].iloc[0],
            status=df['status'].iloc[0],
            password=df['Password'].iloc[0],
            user_id=df['UserID'].iloc[0],
            logout=df['Logout'].iloc[0],
            syncid=df['SYNCID'].iloc[0],
            token=df['token'].iloc[0],
            email_address=df['emailAddress'].iloc[0],
            access_level=df['accessLevel'].iloc[0],
            name=df['Name'].iloc[0],
            start_work_at=pd.to_datetime(df['Start_work']).iloc[0],
        )
        print(user)

        if self.remember_me.isChecked():
            self.__rememberMe(user)

        self.next_screen(user)

    def forget_password(self, event):
        if self.forget_password_form is None:
            self.forget_password_form = ForgetPasswordForm(self)
            self.forget_password_form.show()
            self.hide()
        else:
            self.forget_password_form.close()  # Close window.
            self.forget_password_form = None
            self.show()

        pass

    def __try_remember_me_login(self, ):
        if os.path.exists(REMEMBER_ME_FILE_PATH):
            user = self.__getMe()
            if user is None or not user.email_address:
                return None
            else:
                self.next_screen(user)
                return True
        else:
            return None
        pass

    def __rememberMe(self, user):
        with open(REMEMBER_ME_FILE_PATH, 'bw') as file:
            pickle.dump(user, file)

    def __getMe(self):
        with open(REMEMBER_ME_FILE_PATH, 'rb') as file:
            user = pickle.load(file)
        return user

    def next_screen(self, user):

        if self.main_screen is None:
            self.main_screen = MainApp(
                title='FigurozTimeTracker',
                left=100,
                top=100,
                height=500,
                parent=self,
                user=user,
            )
            self.main_screen.show()
            self.hide()
        else:
            self.main_screen.close()  # Close window.
            self.main_screen = None
            self.show()
        pass


class MainApp(QMainWindow):
    def __init__(self, title, left, top, height, parent=None, user=None):
        super().__init__()
        self.user = user
        self.parent = parent
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

        self.screenshot_action = QAction("&Screenshot...", self)
        self.screenshot_action.triggered.connect(self.take_screenshot)
        fileMenu.addAction(self.screenshot_action)
        fileMenu.addSeparator()

        self.logout_action = QAction("&Logout", self)
        self.logout_action.triggered.connect(self.logout)
        fileMenu.addAction(self.logout_action)

        self.exit_action = QAction("&Exit", self)
        self.exit_action.triggered.connect(self.close)
        fileMenu.addAction(self.exit_action)

    def take_screenshot(self):
        snapshot = ImageGrab.grab()
        snapshot.save(f'./Image_{datetime.now():%Y%m%d_%H%H%S}.png')
        pass

    def logout(self):
        if os.path.exists(REMEMBER_ME_FILE_PATH):
            os.remove(REMEMBER_ME_FILE_PATH)
        self.hide()
        self.parent.show()

        self.destroy()
        del self

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


if __name__ == '__main__':
    app = QApplication(sys.argv)

    form = LoginForm()
    if not os.path.exists(REMEMBER_ME_FILE_PATH):
        form.show()

    # main_screen = MainApp(
    #     title='FigurozTimeTracker',
    #     left=100,
    #     top=100,
    #     height=500,
    #     parent=LoginForm(),
    #     user=None,
    # )
    # main_screen.show()
    sys.exit(app.exec_())
