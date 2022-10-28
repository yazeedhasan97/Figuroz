import json
import os
import re
from datetime import timedelta, datetime

import pandas as pd
from PyQt6 import QtGui
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QListWidget, QGridLayout, \
    QLabel, QMenu, QMainWindow, QLayout, QListWidgetItem, \
    QAbstractItemView, QMessageBox, QLineEdit, QPushButton, QCheckBox, QVBoxLayout, QStatusBar
from PyQt6.QtGui import QIcon, QAction

from scripts import db, utils, consts, SQLs
from scripts.models import User, Task, Project, ProjectTimeLine
from scripts.controllers import MainController, Periodic
from scripts.sync import Sync

from scripts.custom_views import QClickableLabel, TimeTracker, CustomTimer


class ForgetPasswordForm(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """

    def __init__(self, parent=None):
        super(ForgetPasswordForm, self).__init__()
        self.login_form = None
        self.parent = parent
        self.__init_ui()

        layout = QGridLayout()

        label_name = QLabel('Email')
        label_name.setStyleSheet(consts.GENERAL_QLabel_STYLESHEET)
        layout.addWidget(label_name, 0, 0)

        self.lineEdit_username = QLineEdit()
        self.lineEdit_username.setStyleSheet(consts.GENERAL_QLineEdit_STYLESHEET)
        self.lineEdit_username.setPlaceholderText('Please enter your email...')
        layout.addWidget(self.lineEdit_username, 0, 1, )

        button_check = QPushButton('Check')
        button_check.adjustSize()
        button_check.setStyleSheet(consts.GENERAL_QPushButton_STYLESHEET)

        button_check.clicked.connect(self.check_password)
        layout.addWidget(button_check, 1, 1, )

        button_back = QPushButton('Back')
        button_back.adjustSize()
        button_back.setStyleSheet(consts.GENERAL_QPushButton_STYLESHEET)
        button_back.clicked.connect(self.return_to_login_page)
        layout.addWidget(button_back, 1, 0, 1, 1)

        # layout.setRowMinimumHeight(10, 75)
        layout.setContentsMargins(10, 0, 10, 0)
        self.setLayout(layout)

    def __init_ui(self):
        self.setWindowTitle(consts.APP_NAME + ' -- Forget Password Form')
        height = consts.FORGET_PASSWORD_HEIGHT
        width = consts.FORGET_PASSWORD_WIDTH
        self.resize(width, height)
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)

        self.setMinimumWidth(width)
        self.setMaximumWidth(width)

        pass

    def check_password(self):
        msg = QMessageBox()
        email = self.lineEdit_username.text()
        if email is None or email == '':
            msg.setText('Please enter an email to validate.')
            msg.exec()
            return

        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not re.fullmatch(regex, email):
            msg.setText('Text must be in an email format.')
            msg.exec()
            return

        res = Sync.send_forget_password_request(email)
        if res:
            msg.setText('You will receive an email with the details.')
            print(res)
        else:
            msg.setText("Could not find this user in the system.")
        msg.exec()
        return

    def return_to_login_page(self):
        self.parent.show()
        self.hide()
        self.destroy()
        del self
        pass


class LoginForm(QWidget):
    def __init__(self, ):
        super(LoginForm, self).__init__()
        self.__init_ui()

        self.forget_password_form = None
        self.main_screen = None

        layout = QGridLayout()

        label_name = QLabel('Email')
        label_name.setStyleSheet(consts.GENERAL_QLabel_STYLESHEET)
        self.lineEdit_username = QLineEdit()
        self.lineEdit_username.setStyleSheet(consts.GENERAL_QLineEdit_STYLESHEET)
        self.lineEdit_username.setPlaceholderText('Please enter your email...')
        layout.addWidget(label_name, 0, 0)
        layout.addWidget(self.lineEdit_username, 0, 1, 1, 3, )

        label_password = QLabel('Password')
        label_password.setStyleSheet(consts.GENERAL_QLabel_STYLESHEET)
        self.lineEdit_password = QLineEdit()

        self.lineEdit_password.setStyleSheet(consts.GENERAL_QLineEdit_STYLESHEET)
        self.lineEdit_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.lineEdit_password.setPlaceholderText('Please enter your password...')

        self.__show_pass_action = QAction(QIcon(consts.UNHIDDEN_EYE_ICON_PATH), 'Show password', self)
        self.__show_pass_action.setCheckable(True)
        self.__show_pass_action.toggled.connect(self.show_password)
        self.lineEdit_password.addAction(self.__show_pass_action, QLineEdit.ActionPosition.TrailingPosition)

        layout.addWidget(label_password, 1, 0)
        layout.addWidget(self.lineEdit_password, 1, 1, 1, 3, )

        self.remember_me = QCheckBox('Remember me')
        self.remember_me.setStyleSheet(consts.SMALLER_QLabel_STYLESHEET)
        layout.addWidget(self.remember_me, 2, 0)

        label_forget_password = QClickableLabel('Forget Password?', self.forget_password, )
        label_forget_password.setStyleSheet(consts.SMALLER_QLabel_STYLESHEET)
        layout.addWidget(label_forget_password, 2, 3)

        button_login = QPushButton('Login')
        button_login.setStyleSheet(consts.GENERAL_QPushButton_STYLESHEET)
        button_login.clicked.connect(self.check_password)
        layout.addWidget(button_login, 3, 0, 1, 4, )

        layout.setRowMinimumHeight(2, 150)
        layout.setContentsMargins(15, 25, 15, 25)
        self.setLayout(layout)

        self.__try_remember_me_login()

    def show_password(self, ):
        if self.lineEdit_password.echoMode() == QLineEdit.EchoMode.Normal:
            self.lineEdit_password.setEchoMode(QLineEdit.EchoMode.Password)
            self.__show_pass_action.setIcon(QIcon(consts.UNHIDDEN_EYE_ICON_PATH))
        else:
            self.lineEdit_password.setEchoMode(QLineEdit.EchoMode.Normal)
            self.__show_pass_action.setIcon(QIcon(consts.HIDDEN_EYE_ICON_PATH))

    def __init_ui(self):
        self.setWindowTitle(consts.APP_NAME + ' -- Login Form')
        height = consts.LOGIN_PASSWORD_HEIGHT
        width = consts.LOGIN_PASSWORD_WIDTH
        self.resize(width, height)
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)

        self.setMinimumWidth(width)
        self.setMaximumWidth(width)

        pass

    def check_password(self):
        msg = QMessageBox()
        email = self.lineEdit_username.text()
        password = self.lineEdit_password.text()
        if email is None or not email:
            msg.setText('Please enter an email.')
            msg.exec()
            return

        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not re.fullmatch(regex, email):
            msg.setText('Email must be in an email format.')
            msg.exec()
            return

        if password is None or not password:
            msg.setText('Please enter a password.')
            msg.exec()
            return

        user = self.__load_user_data(email, password)

        if user is None or not user:
            msg.setText("Could not find user in the system.")
            msg.exec()
            return

        if self.remember_me.isChecked():
            utils.remember_me(user, consts.REMEMBER_ME_FILE_PATH)

        print('done checking')
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

    def __load_user_data(self, email, password):
        msg = QMessageBox()
        user = Sync.send_login_request(email, password)
        print(user)

        if not user:
            user_df = db.execute(SQLs.SELECT_ALL_USERS_WHERE_EMAIL_AND_PASSWORD.format(
                email=email, password=password
            ), conn_s=MainController.DB_CONNECTION)

            if user_df.empty:
                msg.setText("Password might be incorrect.")
                msg.exec()
                return

            user = [User(
                token=a.token,
                refresh_token=a.refresh_token,
                id=a.id,
                company_id=a.companyId,
                username=a.username,
                email_address=a.email_address,
                password=a.password,
                status=a.status,
                access_level=a.access_level,
                code=a.code,
                screenshot_interval=a.screenshot_interval,
                can_edit_time=a.can_edit_time,
                blur_screen=a.blur_screen,
                receive_daily_report=a.receive_daily_report,
                inactive_time=a.inactive_time,
                can_delete_screencast=a.can_delete_screencast,
                owner_user=a.owner_user,
                sync_data=a.sync_data,
                profile_image=a.profile_image,
                group_members=json.loads(a.group_members),
                group_managers=json.loads(a.group_managers),
            ) for a in user_df.itertuples()][0]

        return user

    def __try_remember_me_login(self, ):
        msg = QMessageBox()
        user = utils.get_me(consts.REMEMBER_ME_FILE_PATH)

        if user is None or not user.email_address:
            msg.setText("Could not load pre-saved user.")
            msg.exec()
            return

        user = self.__load_user_data(user.email_address, user.password)

        utils.remember_me(user, consts.REMEMBER_ME_FILE_PATH)
        self.next_screen(user)
        return True

    def next_screen(self, user):
        if self.main_screen is None:
            self.main_screen = MainAppA(
                title=consts.APP_NAME,
                left=100,
                top=100,
                height=400,
                parent=self,
                user=user,
            )
            self.main_screen.show()
        else:
            self.main_screen.show()  # Close window.
            self.main_screen = None

        self.hide()
        self.close()
        self.destroy()

        pass


class MainAppA(QMainWindow):

    def __init__(self, title, left, top, height, parent=None, user=None):
        super(MainAppA, self).__init__(parent)

        self.__init_ui(title, left, top, height)

        self.user = user
        self.parent = parent

        self.tasks_qlist_dict = {}
        self.tasks_timers_dict = {}
        self.projects = []
        self.projects_time_trackers = {}
        self.active_project = None
        self.active_task = None
        self.duration = timedelta(seconds=0)

        self.__init_data()

        self.__create_menu_bar()

        self.__init_layouts()

        self.setStatusBar(QStatusBar(self))

        self.__fill_projects_qlist()
        self.__fill_tasks_qlist_dict()

        self.__fill_with_last_active_project()

        if self.user.sync_data:  # TODO: ned the interval of updates
            Periodic(consts.DURATIONS_UPLOAD_INTERVAL, lambda: Sync.update_project_timelines_request(user=self.user))

        # if settings.take_screenshots:
        #     # TODO: time intervals should be from the DB
        #     screens = Periodic(5, lambda: utils.take_screenshot(consts.OUTPUT_DIR, settings.blur_screen))

    def __create_menu_bar(self):
        menu_bar = self.menuBar()
        # Creating menus using a QMenu object
        file_menu = QMenu("&File", self)
        menu_bar.addMenu(file_menu)

        self.screenshot_action = QAction("&Screenshot...", self)
        self.screenshot_action.triggered.connect(utils.take_screenshot)
        file_menu.addAction(self.screenshot_action)
        file_menu.addSeparator()

        self.logout_action = QAction("&Logout", self)
        self.logout_action.triggered.connect(self.__logout)
        file_menu.addAction(self.logout_action)

        self.exit_action = QAction("&Exit", self)
        self.exit_action.triggered.connect(self.close)
        file_menu.addAction(self.exit_action)

    def __logout(self):
        if os.path.exists(consts.REMEMBER_ME_FILE_PATH):
            os.remove(consts.REMEMBER_ME_FILE_PATH)

        if os.path.exists(consts.REMEMBER_LAST_ACTIVE_FILE_PATH):
            os.remove(consts.REMEMBER_LAST_ACTIVE_FILE_PATH)

        self.parent.show()
        self.hide()
        self.destroy()

    def __init_ui(self, title, left, top, height):
        self.setWindowTitle(title)
        self.setGeometry(left, top, int(height * 1.61), height)

        self.setMinimumHeight(height)
        self.setMaximumHeight(height)

        self.setMinimumWidth(int(height * 1.46))
        self.setMaximumWidth(int(height * 1.46))
        # self.setWindowIcon(QIcon('logo.png'))

    def __init_layouts(self):
        layout = QGridLayout()
        layout.setSpacing(5)
        layout.sizeConstraint = QLayout.SizeConstraint.SetDefaultConstraint

        main_widget = QWidget()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

        # Define The Project Description Layout
        title_layout = QGridLayout()
        self.lbl_active_project = QLabel()
        self.lbl_active_project.setStyleSheet(consts.BIGGER_QLabel_STYLESHEET)
        title_layout.addWidget(self.lbl_active_project, 0, 0)

        self.lbl_active_task = QLabel('Task')
        self.lbl_active_task.setStyleSheet(consts.GENERAL_QLabel_STYLESHEET)
        title_layout.addWidget(self.lbl_active_task, 1, 0)

        self.lbl_worked_today = QLabel('Worked Today: ')
        title_layout.addWidget(self.lbl_worked_today, 2, 2)

        # self.lbl_project_time_tracker = models.TimeTracker()
        # title_layout.addWidget(self.lbl_project_time_tracker, 0, 2)

        self.lbl_task_time_tracker = TimeTracker()
        title_layout.addWidget(self.lbl_task_time_tracker, 1, 1)

        self.lbl_total_time_tracker = TimeTracker()
        title_layout.addWidget(self.lbl_total_time_tracker, 2, 3)

        layout.addLayout(title_layout, 0, 0, 2, 3)

        # Define The Project Layout
        self.projects_layout = QVBoxLayout()
        layout.addLayout(self.projects_layout, 2, 0, )

        # Define The SubProjects Layout
        self.sub_projects_layout = QVBoxLayout()
        layout.addLayout(self.sub_projects_layout, 2, 1, )

    def __load_projects_related_data(self, ):
        msg = QMessageBox()
        projects = Sync.get_projects_request(self.user.token)
        print(projects)

        if not projects:  # If success insert to db else, load from db
            print('Try loading the projects from the local database...')
            projects_df = db.execute(SQLs.SELECT_ALL_PROJECTS_WHERE_COMPANY.format(
                company_id=self.user.company_id,
            ), conn_s=MainController.DB_CONNECTION)

            if projects_df.empty:
                msg.setText(
                    "Could not load any project for this user."
                    "\nTheir might be no projects assigned to this user."
                )
                msg.exec()
                return

            print('Projects data successfully loaded from the local database')
            self.projects = [Project(
                id=a.id,
                name=a.projectName.title(),
                status=a.status,
                company_id=a.companyId,
                project_access=a.projectAccess,
                project_groups=json.loads(a.projectGroups),
                project_members=json.loads(a.projectMembers),
            ) for a in projects_df.itertuples()]
        else:
            self.projects = projects

    def __load_tasks_related_data(self):
        msg = QMessageBox()
        tasks = Sync.get_tasks_request(self.user.token)
        print(tasks)

        if not tasks:
            print('Try loading the tasks from the local database...')
            tasks_df = db.execute(SQLs.SELECT_ALL_TASKS_IN_PROJECTS.format(
                project_id_tuple=tuple([p.id for p in self.projects])
            ), conn_s=MainController.DB_CONNECTION)

            if tasks_df.empty:
                msg.setText(
                    "Could not load any tasks for this user."
                    "\nTheir might be no tasks assigned to this user."
                    "\nIt is recommended to check with your admins."
                )
                msg.exec()
                return

            print('Tasks data successfully loaded from the local database')
            tasks = [Task(
                project_id=a.projectId,
                id=a.id,
                status=a.status,
                name=a.taskName.title(),
            ) for a in tasks_df.itertuples()]

        return tasks

    def __init_data(self):
        self.__load_projects_related_data()
        tasks = self.__load_tasks_related_data()

        # assign tasks to projects
        for i in range(len(self.projects)):
            self.projects[i].tasks = utils.id_filter(
                pid=self.projects[i].id,
                lst=tasks,
                compare='pid',
            )

    def __fill_projects_qlist(self):
        self.projects_list_widget = QListWidget()
        self.projects_list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.projects_list_widget.setSpacing(10)
        self.projects_list_widget.setStyleSheet(consts.PROJECTS_LIST_WIDGET_STYLESHEET)

        self.projects_layout.addWidget(
            self.projects_list_widget
        )

        for project in self.projects:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, project)
            item.setText(project.name)
            self.projects_list_widget.addItem(item)

        self.projects_list_widget.itemClicked.connect(self.__show_project_ui)

        df = db.execute(SQLs.SELECT_DURATIONS_WHERE_USER_AND_DATE.format(
            user=self.user.id,
            today=datetime.today().strftime('%Y%m%d')
        ), conn_s=MainController.DB_CONNECTION)
        self.lbl_total_time_tracker.reset(pd.to_timedelta(df.duration).sum())

    def __show_project_ui(self, item, ):
        if type(item) is not Project:
            project = item.data(Qt.ItemDataRole.UserRole)
            print(item.text())
        else:
            # self.active_project = item
            project = item
            self.lbl_active_project.setText(project.name)

        # Collect Durations from the DB
        df = db.execute(SQLs.SELECT_DURATION_TIMELINES_WHERE_PROJECT_AND_USER_AND_DATE.format(
            user=self.user.id,
            project_id=project.id,
            today=datetime.today().strftime('%Y%m%d')
        ), conn_s=MainController.DB_CONNECTION)
        self.duration = pd.to_timedelta(df.duration).sum()

        # if type(item) is db_models.Project:  # if and only if reloaded from remember me
        #     self.lbl_project_time_tracker.reset(
        #         self.duration
        #     )

        for key in self.tasks_qlist_dict.keys():
            self.tasks_qlist_dict[key].hide()

        self.sub_projects_layout.addWidget(self.tasks_qlist_dict[project.id])
        self.tasks_qlist_dict[project.id].show()
        self.tasks_qlist_dict[project.id].itemClicked.connect(self.__start_timer)
        self.tasks_qlist_dict[project.id].itemChanged.connect(self.__pause_timer)
        self.tasks_qlist_dict[project.id].itemDoubleClicked.connect(self.__pause_timer)

    def __fill_tasks_qlist_dict(self):
        for project in self.projects:
            sub_qlist = QListWidget()
            sub_qlist.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            sub_qlist.setSpacing(1)

            df = db.execute(
                SQLs.SELECT_TASKID_AND_DURATION_TIMELINES_WHERE_PROJECT_AND_USER_AND_DATE.format(
                    user=self.user.id,
                    project_id=project.id,
                    today=datetime.today().strftime('%Y%m%d')
                ), conn_s=MainController.DB_CONNECTION)

            if not df.empty:
                df.duration = pd.to_timedelta(df.duration)
                df.sub_id = pd.to_numeric(df.sub_id)
                df = df.groupby('sub_id').sum()

            for task in project.tasks:

                timeline = ProjectTimeLine(
                    project_id=project.id,
                    sub_id=task.id,
                    user=self.user.id,
                )
                if not df.empty and int(task.id) in df.index.astype(int):
                    timeline.duration = df.loc[int(task.id), 'duration']

                self.tasks_timers_dict[task.id] = CustomTimer(timeline, )

                self.tasks_timers_dict[task.id].attach(task.id)

                item = QListWidgetItem(sub_qlist)
                item.setData(Qt.ItemDataRole.UserRole, task)
                item.setText(task.name)
                sub_qlist.addItem(item)
                sub_qlist.setItemWidget(item, self.tasks_timers_dict[task.id])
                sub_qlist.setStyleSheet(consts.TASKS_LIST_WIDGET_STYLESHEET)

            self.tasks_qlist_dict[project.id] = sub_qlist

        pass

    def __start_timer(self, item):
        # Receive the Task
        task = item.data(Qt.ItemDataRole.UserRole)

        # if self.active_task is not None and self.active_project is not None:
        #     if self.active_project.id == task.project_id:
        #         self.duration = self.lbl_project_time_tracker.time

        # Make sure all other timers are paused before activating a new timer
        for sub_id in self.tasks_timers_dict:
            if self.tasks_timers_dict[sub_id].flag and task.id != sub_id:
                self.tasks_timers_dict[sub_id].pause()

        # self.lbl_project_time_tracker.reset(self.duration)
        # self.lbl_project_time_tracker.start()
        # Activate the Task TimeTracker in the titles grid
        self.lbl_task_time_tracker.reset(self.tasks_timers_dict[task.id].time)
        self.lbl_task_time_tracker.start()

        self.lbl_total_time_tracker.start()

        # Activate the actual timer
        self.tasks_timers_dict[task.id].start()
        self.tasks_timers_dict[task.id].show_time(mode='display')

        # Retrieve the project
        self.active_project = utils.id_filter(
            task.project_id,
            self.projects
        )[0]
        self.active_task = task

        # Fill the titles
        self.lbl_active_project.setText(self.active_project.name)
        self.lbl_active_task.setText(task.name)

    def __pause_timer(self, item):
        task = item.data(Qt.ItemDataRole.UserRole)
        self.tasks_timers_dict[task.id].pause()
        self.tasks_timers_dict[task.id].show_time(mode='display')
        self.lbl_task_time_tracker.pause()
        self.lbl_total_time_tracker.pause()
        # self.lbl_project_time_tracker.pause()

        pass

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        for sub_id in self.tasks_timers_dict:
            if self.tasks_timers_dict[sub_id].flag:
                self.tasks_timers_dict[sub_id].pause()

        if self.active_project is not None:
            utils.remember_me(
                self.active_project,
                consts.REMEMBER_LAST_ACTIVE_FILE_PATH
            )

        super().closeEvent(a0)

    def __fill_with_last_active_project(self):
        msg = QMessageBox()
        project = utils.get_me(consts.REMEMBER_LAST_ACTIVE_FILE_PATH)

        if project is None or not project.id:
            msg.setText('Failed to load project as nothing was saved.')
            msg.exec()
            return None

        if not utils.id_filter(project.id, self.projects):
            msg.setText('Failed to load project as it was removed from the database.')
            msg.exec()
            return None

        self.__show_project_ui(project)
