import os, re
from datetime import timedelta, datetime
from multiprocessing import Pipe, Process

from PyQt6 import QtGui
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtWidgets import QWidget, QListWidget, QGridLayout, \
    QLabel, QMenu, QMainWindow, QLayout, QListWidgetItem, \
    QAbstractItemView, QMessageBox, QLineEdit, QPushButton, QCheckBox, QVBoxLayout, QFrame, QHBoxLayout
from PyQt6.QtGui import QIcon, QAction

# Custom Modules
from common import consts, utils
from database.custom_models import DurationKeeper
from scripts.trackers import Periodic, ScreenshotsCapture, InternetStateTracker
from scripts.controllers import MainController, InputsObserver
from scripts.custom_views import QClickableLabel, TimeTracker, CustomTimer

from database.models import User, Task, Project, ProjectTimeLine, crete_user_from_api, create_projects_from_api, \
    create_tasks_from_api, create_and_insert_project_time_line

from active_window_watcher.main_window_watcher import create_active_window_watcher


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

        self.setWindowIcon(QIcon(
            consts.MAIN_ICON_PATH
        ))

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

        res = MainController.API_CONNECTION.post_forget_password_request(email=email)
        if res:
            msg.setText('You will receive an email with the details.')
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

        self.setWindowIcon(QIcon(
            consts.MAIN_ICON_PATH
        ))
        pass

    def check_password(self):

        msg = QMessageBox()
        email = self.lineEdit_username.text().lower()
        password = self.lineEdit_password.text()
        if email is None or not email:
            msg.setText('Please enter an email.')
            msg.exec()
            return

        if password is None or not password:
            msg.setText('Please enter a password.')
            msg.exec()
            return

        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not re.fullmatch(regex, email):
            msg.setText('Email must be in an email format.')
            msg.exec()
            return

        user = self.__load_user_data(email, password)

        if self.remember_me.isChecked():
            utils.remember_me({
                'email': user.email,
                'password': user.password,
            },
                consts.REMEMBER_ME_FILE_PATH
            )

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
        user = MainController.DB_CONNECTION.query(User).filter(User.email == email).first()
        if user:
            return user
        else:
            data = MainController.API_CONNECTION.post_login_request(email, password)
            if data:
                user = crete_user_from_api(MainController.DB_CONNECTION, data, password)
                return user
            else:
                msg.setText("Password might be incorrect. User is not found. APIs are down.")
                msg.exec()
                return False

    def __try_remember_me_login(self, ):
        msg = QMessageBox()
        data = utils.get_me(consts.REMEMBER_ME_FILE_PATH)

        if data:
            user = self.__load_user_data(
                email=data['email'],
                password=data['password'],
            )
        else:
            msg.setText("Could not load pre-saved user.")
            msg.exec()
            return

        utils.remember_me({
            'email': user.email,
            'password': user.password,
        }, consts.REMEMBER_ME_FILE_PATH)
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


def create_tasks_qlist():
    tasks_qlist = QListWidget()
    tasks_qlist.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    tasks_qlist.setSpacing(1)
    tasks_qlist.setStyleSheet(consts.TASKS_LIST_WIDGET_STYLESHEET)
    return tasks_qlist


class MainApp(QMainWindow):

    def __init__(self, user=None):
        super(MainApp, self).__init__()

        self.__init_ui()

        self.user = user
        self.floating_bar = None

        self.tasks_qlist_dict = {}  # KEY is user_id + project_id
        self.tasks_timers_dict = {}  # KEY is user_id + project_id + task_id
        self.projects = []
        self.projects_time_trackers = {}
        self.active_project = None
        self.active_task = None
        self.duration = timedelta(seconds=0)

        self.__init_data()
        self.__create_menu_bar()
        self.__init_layouts()
        self.__fill_projects_qlist()
        self.__fill_tasks_qlist_dict()

        if os.path.exists(consts.REMEMBER_LAST_ACTIVE_FILE_PATH):
            self.__fill_with_last_active_project()

        self.periodic_screenshots_capturer = None
        self.periodic_idle_capturer = None
        self.inputs_tracker = None
        self.window_activity_tracker = None
        self.window_watcher = None
        self.parent_conn = None
        self.child_conn = None
        self.periodic_load_upload_controller = None
        self.periodic_internet_tracker = None

        if self.user.sync_data:
            self.start_data_syncing()
        self.start_observers_and_schedulers()

    def start_data_syncing(self):
        from apis.sync import LoadUploadController
        load_upload_controller = LoadUploadController(
            session=MainController.DB_CONNECTION,
            requester=MainController.API_CONNECTION,
            user_id=self.user.id,
            token=self.user.token,
            commit=True,
        )

        self.periodic_load_upload_controller = Periodic(
            consts.DATA_LOAD_AND_UPLOAD_INTERVAL,
            load_upload_controller.load_and_upload,
        )

    def start_observers_and_schedulers(self):
        # Durations Uploader

        # ################################## #l
        # Must Stop Threads, No need to stop #
        # ################################## #
        screen_capturer = ScreenshotsCapture(
            user_id=self.user.id,
            directory=consts.OUTPUT_DIR,
            blur=self.user.blur_screen,
        )
        self.periodic_screenshots_capturer = Periodic(
            self.user.screenshot_interval * 60,
            screen_capturer.run
        )
        self.inputs_tracker = InputsObserver(auto_start=True)

        from idle_watcher.afk import AFKWatcher

        # Start Idle Watcher
        idle_capturer = AFKWatcher(
            user_id=self.user.id,
            timeout=self.user.inactive_interval * 60,
        )
        self.periodic_idle_capturer = Periodic(
            1,
            idle_capturer.heartbeat
        )

        self.window_watcher = create_active_window_watcher(
            user_id=self.user.id,
        )
        self.parent_conn, self.child_conn = Pipe()
        self.window_activity_tracker = Process(
            target=self.window_watcher.run,
            # args=(child_conn, user),
            daemon=True,
        )
        self.window_activity_tracker.start()

        tracker = InternetStateTracker(
            user_id=self.user.id
        )
        self.periodic_internet_tracker = Periodic(
            30,
            tracker.get_internet_state
        )
        self.periodic_internet_tracker.start()

    def __flush(self):
        for id in self.tasks_timers_dict:
            if self.tasks_timers_dict[id].flag:
                self.tasks_timers_dict[id].pause()

        if self.active_project is not None:
            utils.remember_me({
                'id': self.active_project.id,
                'name': self.active_project.name,
                'user_id': self.active_project.user_id,
            },
                consts.REMEMBER_LAST_ACTIVE_FILE_PATH
            )
        if self.periodic_screenshots_capturer is not None:
            self.periodic_screenshots_capturer.stop()

        if self.periodic_idle_capturer is not None:
            self.periodic_idle_capturer.stop()

        if self.inputs_tracker is not None:
            self.inputs_tracker.stop()

        if self.periodic_load_upload_controller is not None:
            self.periodic_load_upload_controller.stop()

        if self.periodic_internet_tracker is not None:
            self.periodic_internet_tracker.stop()

        if self.window_activity_tracker is not None:
            try:
                self.window_activity_tracker.kill()
                self.window_activity_tracker.terminate()
                self.window_activity_tracker.join()
                self.window_activity_tracker.close()
                self.parent_conn.close()
                self.child_conn.close()
            except Exception as e:
                print(e)

    def __create_menu_bar(self):
        menu_bar = self.menuBar()
        # Creating menus using a QMenu object
        file_menu = QMenu("&File", self)
        menu_bar.addMenu(file_menu)

        file_menu.addSeparator()
        self.logout_action = QAction("&Logout", self)
        self.logout_action.triggered.connect(self.__logout)
        file_menu.addAction(self.logout_action)

        self.exit_action = QAction("&Exit", self)
        self.exit_action.triggered.connect(self.closeEvent)
        file_menu.addAction(self.exit_action)

    def __logout(self):
        # self._force_stop_processes()
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
        self.setWindowIcon(QIcon(
            consts.MAIN_ICON_PATH
        ))

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

        self.lbl_current_user = QLabel(self.user.username.replace('.', ' ').title())
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

    def __fill_tasks_qlist_dict(self):
        for project in self.projects:
            tasks_qlist = create_tasks_qlist()
            data = self.load_total_durations_per_task_and_day(project.id)

            for task in project.tasks:
                # timeline = create_project_time_line(
                #     user_id=self.user.id,
                #     project_id=project.id,
                #     task_id=task.id,
                #     session=MainController.DB_CONNECTION
                # )
                timeline = DurationKeeper(
                    user_id=self.user.id,
                    project_id=project.id,
                    task_id=task.id,
                )

                if data and task.id in data.keys():
                    timeline.duration = data.get(task.id, timedelta(seconds=0))

                tasks_timers_dict_id = ''.join([str(self.user.id), str(project.id), str(task.id)])
                self.tasks_timers_dict[tasks_timers_dict_id] = CustomTimer(timeline, )
                self.tasks_timers_dict[tasks_timers_dict_id].attach(tasks_timers_dict_id)

                item = QListWidgetItem()
                item.setText(task.name)
                item.setData(Qt.ItemDataRole.UserRole, task)
                tasks_qlist.addItem(item)
                tasks_qlist.setItemWidget(item, self.tasks_timers_dict[tasks_timers_dict_id])

            tasks_qlist_dict_id = ''.join([str(self.user.id), str(project.id)])
            self.tasks_qlist_dict[tasks_qlist_dict_id] = tasks_qlist

    def __load_projects_related_data(self, ):
        msg = QMessageBox()
        projects = MainController.DB_CONNECTION.query(Project).filter(Project.user_id == self.user.id).all()

        if projects:
            self.projects = projects
        else:
            data = MainController.API_CONNECTION.get_projects_request(self.user.token)
            if data:
                projects = create_projects_from_api(MainController.DB_CONNECTION, data, self.user.id)
                self.projects = projects
            else:
                msg.setText(
                    "Could not load any project for this user."
                    "\nTheir might be no projects assigned to this user."
                )
                msg.exec()
                return False

    def __load_tasks_related_data(self):
        msg = QMessageBox()
        tasks = MainController.DB_CONNECTION.query(Task).filter(Task.user_id == self.user.id).all()
        if tasks:
            return tasks
        else:
            data = MainController.API_CONNECTION.get_tasks_request(self.user.token)
            if data:
                tasks = create_tasks_from_api(MainController.DB_CONNECTION, data, self.user.id)
                return tasks
            else:
                msg.setText(
                    "Could not load any tasks for this user."
                    "\nTheir might be no tasks assigned to this user."
                    "\nIt is recommended to check with your admins."
                )
                msg.exec()
                return False

    def __init_data(self):
        self.__load_projects_related_data()
        tasks = self.__load_tasks_related_data()

        # assign tasks to projects
        for i in range(len(self.projects)):
            self.projects[i].tasks = list(filter(lambda x: x.project_id == self.projects[i].id, tasks))

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

        self.load_total_spent_per_day()

    def load_total_spent_per_day(self):
        durations = MainController.DB_CONNECTION.query(ProjectTimeLine.duration).filter(
            ProjectTimeLine.user_id == self.user.id and
            ProjectTimeLine.day_format == datetime.today().strftime(consts.DAY_TIME_FORMAT)
        ).all()
        self.lbl_total_time_tracker.reset(sum([i.duration for i in durations], timedelta()))

    def __show_project_ui(self, item, ):
        if type(item) is not Project:
            project = item.data(Qt.ItemDataRole.UserRole)
        else:
            # self.active_project = item
            project = item
            self.lbl_active_project.setText(project.name)
            MainController.store_current_active_project_id(project.id)

        # self.load_spent_per_project_per_day(
        #   item = item type(item) is Project else project
        # )

        for id in self.tasks_qlist_dict.keys():
            self.tasks_qlist_dict[id].hide()

        tasks_qlist_dict_id = ''.join([str(self.user.id), str(project.id)])
        self.sub_projects_layout.addWidget(self.tasks_qlist_dict[tasks_qlist_dict_id])
        self.tasks_qlist_dict[tasks_qlist_dict_id].show()
        self.tasks_qlist_dict[tasks_qlist_dict_id].itemClicked.connect(self.__start_timer)
        self.tasks_qlist_dict[tasks_qlist_dict_id].itemChanged.connect(self.__pause_timer)
        # TODO: can we have a work around?
        self.tasks_qlist_dict[tasks_qlist_dict_id].itemDoubleClicked.connect(self.__pause_timer)

    def load_spent_per_project_per_day(self, item):  # Not Active
        durations = MainController.DB_CONNECTION.query(ProjectTimeLine.duration).filter(
            ProjectTimeLine.user_id == self.user.id and
            ProjectTimeLine.project_id == item.id and
            ProjectTimeLine.day_format == datetime.today().strftime(consts.DAY_TIME_FORMAT)
        ).all()
        self.duration = sum(durations, timedelta())
        # self.lbl_project_time_tracker.reset(
        #     self.duration
        # )

    def load_total_durations_per_task_and_day(self, project_id):
        data = MainController.DB_CONNECTION.query(
            ProjectTimeLine.task_id,
            ProjectTimeLine.duration,
        ).filter(
            ProjectTimeLine.user_id == self.user.id and
            ProjectTimeLine.project_id == project_id and
            ProjectTimeLine.day_format == datetime.today().strftime(consts.DAY_TIME_FORMAT)
        ).all()

        if data:
            return utils.group_by_and_accumulate_timedelta_list_of_tuples(data)
        else:
            print(
                f'Unable to load or find any durations for project {project_id} '
                f'tasks in {datetime.today().strftime(consts.DAY_TIME_FORMAT)}'
            )
            return {}

    def __start_timer(self, item):
        # Receive the Task
        task = item.data(Qt.ItemDataRole.UserRole)
        # if self.active_task is not None and self.active_project is not None:
        #     if self.active_project.id == task.project_id:
        #         self.duration = self.lbl_project_time_tracker.time

        tasks_timers_dict_id = ''.join([
            str(self.user.id),
            str(task.project_id),
            str(task.id)
        ])

        # Make sure all other timers are paused before activating a new timer
        for id in self.tasks_timers_dict:
            if self.tasks_timers_dict[id].flag and tasks_timers_dict_id != id:
                self.tasks_timers_dict[id].pause()

        # self.lbl_project_time_tracker.reset(self.duration)
        # self.lbl_project_time_tracker.start()

        # Activate the Task TimeTracker in the titles grid
        self.lbl_task_time_tracker.reset(self.tasks_timers_dict[tasks_timers_dict_id].time)
        self.lbl_task_time_tracker.start()
        self.lbl_total_time_tracker.start()

        # Activate the actual timer
        self.tasks_timers_dict[tasks_timers_dict_id].start()
        self.tasks_timers_dict[tasks_timers_dict_id].show_time(mode='display')

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
        tasks_timers_dict_id = ''.join([
            str(self.user.id),
            str(task.project_id),
            str(task.id)
        ])
        self.tasks_timers_dict[tasks_timers_dict_id].pause()
        self.tasks_timers_dict[tasks_timers_dict_id].show_time(mode='display')
        self.lbl_task_time_tracker.pause()
        self.lbl_total_time_tracker.pause()
        # self.lbl_project_time_tracker.pause()

        pass

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.__flush()
        super().closeEvent(a0)

    def __fill_with_last_active_project(self):
        msg = QMessageBox()
        data = utils.get_me(consts.REMEMBER_LAST_ACTIVE_FILE_PATH)

        if not data:
            msg.setText('Failed to load project as nothing was saved.')
            msg.exec()
            return None

        project = MainController.DB_CONNECTION.query(Project).filter(
            Project.id == data['id'] and
            Project.name == data['name'] and
            Project.user_id == data['user_id']
        ).first()
        print(project)

        if not project:
            msg.setText('Failed to load project as it was removed from the database.')
            msg.exec()
            return None

        self.__show_project_ui(project)

    def changeEvent(self, event):
        if event.type() == QEvent.Type.WindowStateChange:
            if event.oldState() and Qt.WindowState.WindowMinimized:
                self.show()
                self.floating_bar.hide()
                self.floating_bar.destroy()
                self.floating_bar.close()
            elif event.oldState() == Qt.WindowState.WindowNoState or self.windowState() == Qt.WindowState.WindowMaximized:

                if self.active_task:
                    project = self.active_project.name
                    task = self.active_task.name
                    tasks_timers_dict_id = ''.join([
                        str(self.user.id),
                        str(self.active_task.project_id),
                        str(self.active_task.id)
                    ])
                    time = self.tasks_timers_dict.get(tasks_timers_dict_id).time
                    flag = self.tasks_timers_dict.get(tasks_timers_dict_id).flag
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

    def greetings(self):
        # TODO: implement methodology to stop from the floating dialog
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
