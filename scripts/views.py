import json
import os
import re
from datetime import timedelta, datetime
from multiprocessing import Process, Pipe
import pandas as pd
from PyQt6 import QtGui
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtWidgets import QWidget, QListWidget, QGridLayout, \
    QLabel, QMenu, QMainWindow, QLayout, QListWidgetItem, \
    QAbstractItemView, QMessageBox, QLineEdit, QPushButton, QCheckBox, QVBoxLayout, QStatusBar, QFrame, QHBoxLayout
from PyQt6.QtGui import QIcon, QAction

from database import db, SQLs
from common import consts, utils
from database.models import User, Task, Project, ProjectTimeLine
from scripts.controllers import MainController, ScreenShotDirectoryWatcher, InputsObserver, StoppableThread
from apis.sync import Sync
from scripts.custom_views import QClickableLabel, TimeTracker, CustomTimer
from scripts.trackers import Periodic


class ForgetPasswordForm(QWidget):
    """ This "window" is a QWidget. If it has no parent, it will appear as a free-floating window as we want.
    """

    def __init__(self, ):
        super(ForgetPasswordForm, self).__init__()
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
        height = consts.FORGET_PASSWORD_SCREEN_HEIGHT
        width = consts.FORGET_PASSWORD_WIDTH
        self.resize(width, height)
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)

        self.setMinimumWidth(width)
        self.setMaximumWidth(width)

        pass

    def check_password(self):
        msg = QMessageBox()
        email = self.lineEdit_username.text().lower()
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
        LoginForm(state='reverse').show()
        self.hide()
        self.destroy()
        self.close()
        pass


class LoginForm(QWidget):
    def __init__(self, state=None):
        super(LoginForm, self).__init__()
        self.__init_ui()
        self.screen = None
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

        if state is None:
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
        height = consts.LOGIN_SCREEN_HEIGHT
        width = consts.LOGIN_SCREEN_WIDTH
        self.resize(width, height)
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)

        self.setMinimumWidth(width)
        self.setMaximumWidth(width)

        pass

    def check_password(self):
        # TODO: Need APIs methodology to validate Password
        msg = QMessageBox()
        email = self.lineEdit_username.text().lower()
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
        self.screen = ForgetPasswordForm()
        self.screen.show()
        self.hide()
        self.destroy()
        self.close()

    def __load_user_data(self, email, password):
        msg = QMessageBox()
        user = Sync.send_login_request(email, password)
        print(user)

        if not user:
            user_df = db.execute(SQLs.SELECT_ALL_USERS_WHERE_EMAIL_AND_PASSWORD.format(
                email=email, password=password
            ), conn=MainController.DB_CONNECTION)

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
        self.screen = MainApp(
            user=user,
        )
        self.screen.show()

        self.hide()
        self.destroy()
        self.close()

        pass


class MainApp(QMainWindow):

    def __init__(self, user=None):
        super(MainApp, self).__init__()

        self.__init_ui()

        self.user = user
        self.floating_bar = None

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

        if os.path.exists(consts.REMEMBER_LAST_ACTIVE_FILE_PATH):
            self.__fill_with_last_active_project()

        # Durations Uploader
        if self.user.sync_data:
            # ################################## #
            # Must Stop Threads, No need to stop #
            # ################################## #
            self.periodic_screenshots_taker = Periodic(
                self.user.screenshot_interval * 60,
                lambda: utils.take_screenshot(
                    user_id=self.user.id,
                    blur=self.user.blur_screen,
                    directory=consts.OUTPUT_DIR,
                    format=consts.IMAGE_DATE_TIME_FORMATS,
                ))

            # ############################### #
            # Daemon threads, No need to stop #
            # ############################### #
            self.inputs_tracker = InputsObserver(auto_start=True)
            self.screenshots_watcher = ScreenShotDirectoryWatcher(consts.OUTPUT_DIR, auto_start=True)

            # TODO: this one needs further implementation
            self.idle_time_tracker = StoppableThread(
                target=self.init_idle_time_watcher,
                daemon=True
            )
            self.idle_time_tracker.start()

            self.init_window_activity_watcher()

        else:
            self.inputs_tracker = None
            self.periodic_screenshots_taker = None
            self.screenshots_watcher = None
            self.idle_time_tracker = None
            self.window_activity_tracker, self.parent_conn, self.child_conn = None, None, None

    def init_idle_time_watcher(self):
        from common.logs import setup_logging
        from idle_watcher.afk import AFKWatcher
        from idle_watcher.config import parse_args

        args = parse_args()

        # Set up logging
        setup_logging(
            "aw-watcher-afk",
            testing=args.testing,
            verbose=args.verbose,
            log_stderr=True,
            log_file=True,
        )

        # Start watcher
        watcher = AFKWatcher(args, self.user, testing=args.testing)
        watcher.run()
        pass

    def init_window_activity_watcher(self):
        from active_window_watcher.main_window_watcher import main

        self.parent_conn, self.child_conn = Pipe()
        self.window_activity_tracker = Process(target=main, args=(self.child_conn, self.user), daemon=True)
        self.window_activity_tracker.start()

    def __flush(self):
        for sub_id in self.tasks_timers_dict:
            if self.tasks_timers_dict[sub_id].flag:
                self.tasks_timers_dict[sub_id].pause()

        if self.active_project is not None:
            utils.remember_me(
                self.active_project,
                consts.REMEMBER_LAST_ACTIVE_FILE_PATH
            )
        if self.periodic_screenshots_taker is not None:
            self.periodic_screenshots_taker.stop()

        # if self.periodic_duration_sync is not None:
        #     self.periodic_duration_sync.stop()

        # if self.periodic_screenshot_sync is not None:
        #     self.periodic_screenshot_sync.stop()

        self.inputs_tracker = None
        self.periodic_screenshots_taker = None
        self.screenshots_watcher = None
        self.idle_time_tracker = None
        self.window_activity_tracker = None
        # TODO: we need to clear all tables if the user sign-out

    def _force_stop_processes(self):
        try:
            if self.window_activity_tracker is not None:
                self.window_activity_tracker.terminate()
        except Exception as e:
            print('Active window watcher stopped')

        # TODO: this one causing issues on force_stop
        if self.idle_time_tracker is not None:
            self.idle_time_tracker.stop()

        if self.screenshots_watcher is not None:
            self.screenshots_watcher.stop()

        # TODO: this one causing issues on force_stop
        # if self.inputs_tracker is not None:
        #     self.inputs_tracker.stop()

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
        self.exit_action.triggered.connect(self.closeEvent)
        file_menu.addAction(self.exit_action)

    def __logout(self):
        self._force_stop_processes()
        self.__flush()

        if os.path.exists(consts.REMEMBER_ME_FILE_PATH):
            os.remove(consts.REMEMBER_ME_FILE_PATH)

        if os.path.exists(consts.REMEMBER_LAST_ACTIVE_FILE_PATH):
            os.remove(consts.REMEMBER_LAST_ACTIVE_FILE_PATH)

        LoginForm(state='reverse').show()
        self.hide()
        self.destroy()
        self.close()

    def __init_ui(self, ):
        self.setWindowTitle(consts.APP_NAME)
        width = int(consts.MAIN_SCREEN_HEIGHT * 1.61)
        self.setGeometry(
            consts.MAIN_SCREEN_LEFT_CORNER_START,
            consts.MAIN_SCREEN_TOP_CORNER_START,
            width,
            consts.MAIN_SCREEN_HEIGHT,
        )

        self.setMinimumHeight(consts.MAIN_SCREEN_HEIGHT)
        self.setMaximumHeight(consts.MAIN_SCREEN_HEIGHT)

        self.setMinimumWidth(width)
        self.setMaximumWidth(width)
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

        self.lbl_current_user = QLabel(self.user.username)
        self.lbl_current_user.setStyleSheet(consts.GENERAL_QLabel_STYLESHEET)
        title_layout.addWidget(self.lbl_current_user, 2, 0)

        self.lbl_worked_today = QLabel('Worked Today: ')
        title_layout.addWidget(self.lbl_worked_today, 2, 2)

        # self.lbl_project_time_tracker = models.TimeTracker(icon_flag=False)
        # title_layout.addWidget(self.lbl_project_time_tracker, 0, 2)

        self.lbl_task_time_tracker = TimeTracker(icon_flag=False)
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
            ), conn=MainController.DB_CONNECTION)

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
            ), conn=MainController.DB_CONNECTION)

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
            today=datetime.today().strftime(consts.DAY_TIME_FORMAT)
        ), conn=MainController.DB_CONNECTION)
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
            today=datetime.today().strftime(consts.DAY_TIME_FORMAT)
        ), conn=MainController.DB_CONNECTION)
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
                    today=datetime.today().strftime(consts.DAY_TIME_FORMAT)
                ), conn=MainController.DB_CONNECTION)

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

        # TODO: Another methodology to track this ?
        ####################################################################
        MainController.CURRENT_ACTIVE_PROJECT_ID = task.project_id
        MainController.CURRENT_ACTIVE_TASK_ID = task.id
        ####################################################################

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
        self.__flush()
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

    def changeEvent(self, event):
        if event.type() == QEvent.Type.WindowStateChange:
            if event.oldState() and Qt.WindowState.WindowMinimized:
                print("WindowMaximized")
                self.show()
                self.floating_bar.hide()
                self.floating_bar.destroy()
                self.floating_bar.close()
            elif event.oldState() == Qt.WindowState.WindowNoState or self.windowState() == Qt.WindowState.WindowMaximized:
                print(self.active_project)
                print(self.active_task)

                if self.active_task:
                    project = self.active_project.name
                    task = self.active_task.name
                    time = self.tasks_timers_dict.get(self.active_task.id).time
                    flag = self.tasks_timers_dict.get(self.active_task.id).flag
                else:
                    project = None
                    task = None
                    time = timedelta(seconds=0)
                    flag = False

                self.floating_bar = FloatingDialogBar(
                    project=project,
                    task=task,
                    time=time,
                    flag=flag,
                )
                self.floating_bar.show()


class FloatingDialogBar(QWidget):

    def __init__(self, parent=None, project: str = None, task: str = None, time=timedelta(seconds=0), flag=False):
        super(FloatingDialogBar, self).__init__(parent)
        self.offset = None

        self.project = project if project else 'N/A'
        self.task = task if task else 'N/A'

        self.timer = TimeTracker(icon_flag=False)
        self.timer.reset(time)
        if flag:
            self.timer.start()

        self.__init_ui()
        self.__init_layouts()

    def greetings(self):  # TODO: implement methodology to stop from the floating dialog
        if self.button.text() == 'Start':
            self.button.setText('Pause')
            self.frame.adjustSize()
            self.adjustSize()
        else:
            self.button.setText('Start')
            self.frame.adjustSize()
            self.frame.adjustSize()
            self.adjustSize()
        pass

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.offset = event.pos()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.pos() - self.offset)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.offset = None
        super().mouseReleaseEvent(event)

    def __init_ui(self):
        self.setWindowFlags(
            self.windowFlags() |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        available_width = MainController.CURRENT_COMPUTER_SCREEN.availableSize().width()
        available_height = MainController.CURRENT_COMPUTER_SCREEN.availableSize().height()

        left = available_width - int(available_width * (1 - consts.FLOATING_BAR_LEFT_CORNER_START))
        top = available_height - int(available_height * (1 - consts.FLOATING_BAR_TOP_CORNER_START))
        self.width = available_width - int(available_width * (1 - consts.FLOATING_BAR_WIDTH_SUBTRACT_RATIO))
        self.setGeometry(
            left,
            top,
            self.width,
            consts.FLOATING_BAR_HEIGHT,
        )
        self.setMaximumWidth(self.width)
        self.setMinimumWidth(self.width)
        self.setMinimumHeight(consts.FLOATING_BAR_HEIGHT)
        self.setMaximumHeight(consts.FLOATING_BAR_HEIGHT)
        pass

    def __init_layouts(self):
        self.frame = QFrame(self)
        self.frame.setStyleSheet(consts.FLOATING_BAR_STYLESHEET)
        # Create widgets
        layout = QHBoxLayout()

        self.lbl_project = QLabel(self.project)
        self.lbl_project.setStyleSheet(consts.FLOATING_BAR_QLabel_STYLESHEET)
        layout.addWidget(self.lbl_project)

        self.lbl_task = QLabel(self.task)
        self.lbl_task.setStyleSheet(consts.FLOATING_BAR_QLabel_STYLESHEET)
        layout.addWidget(self.lbl_task)

        # self.lbl_timer = QLabel('Timer')
        # self.lbl_timer.setStyleSheet(consts.FLOATING_BAR_QLabel_STYLESHEET)
        layout.addWidget(self.timer)

        self.button = QPushButton("Start")
        # self.button.setStyleSheet(consts.FLOATING_BAR_QPushButton_STYLESHEET)
        # self.button.clicked.connect(self.greetings)
        # layout.addWidget(self.button)

        layout.setContentsMargins(0, 0, 0, 0)
        self.frame.setLayout(layout)

        self.frame.setMaximumWidth(self.width)
        self.frame.setMinimumWidth(self.width)

        self.frame.setMinimumHeight(consts.FLOATING_BAR_HEIGHT)
        self.frame.setMaximumHeight(consts.FLOATING_BAR_HEIGHT)

        pass
