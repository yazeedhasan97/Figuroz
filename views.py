import os
import pickle
import sys
from datetime import timedelta, datetime

import pandas as pd
from PyQt6 import QtGui
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QListWidget, QHBoxLayout, QGridLayout, \
    QLabel, QMenu, QMainWindow, QLayout, QListWidgetItem, \
    QAbstractItemView, QMessageBox, QLineEdit, QPushButton, QCheckBox
from PyQt6.QtGui import QIcon, QAction

import db
import utils
import db_models

import models, consts
from tests import SQLs


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

    def __init_ui(self):
        self.setWindowTitle('Forget Password Form')
        height = 300
        width = 500
        self.resize(width, height)
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)

        self.setMinimumWidth(width)
        self.setMaximumWidth(width)

        pass

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
        super(LoginForm, self).__init__()
        self.__init_ui()

        self.forget_password_form = None
        self.main_screen = None

        layout = QGridLayout()

        label_name = QLabel('<font size="4"> Username </font>')
        self.lineEdit_username = QLineEdit()
        self.lineEdit_username.setPlaceholderText('Please enter your username')
        layout.addWidget(label_name, 0, 0)
        layout.addWidget(self.lineEdit_username, 0, 2, )

        label_password = QLabel('<font size="4"> Password </font>')
        self.lineEdit_password = QLineEdit()
        self.lineEdit_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.lineEdit_password.setPlaceholderText('Please enter your password')

        self.__show_pass_action = QAction(QIcon(consts.UNHIDDEN_EYE_ICON_PATH), 'Show password', self)
        self.__show_pass_action.setCheckable(True)
        self.__show_pass_action.toggled.connect(self.show_password)
        self.lineEdit_password.addAction(self.__show_pass_action, QLineEdit.ActionPosition.TrailingPosition)

        layout.addWidget(label_password, 1, 0)
        layout.addWidget(self.lineEdit_password, 1, 2, )

        self.remember_me = QCheckBox('Remember me')
        layout.addWidget(self.remember_me, 2, 0)

        label_forget_password = models.QClickableLabel('<font size="3"> Forget Password? </font>',
                                                       self.forget_password, )
        layout.addWidget(label_forget_password, 2, 2)

        button_login = QPushButton('Login')
        button_login.clicked.connect(self.check_password)
        layout.addWidget(button_login, 3, 0, 3, 3)
        layout.setRowMinimumHeight(2, 75)
        layout.setContentsMargins(65, 65, 65, 65)
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
        self.setWindowTitle('Login Form')
        height = 300
        width = 500
        self.resize(width, height)
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)

        self.setMinimumWidth(width)
        self.setMaximumWidth(width)

        pass

    def check_password(self):
        msg = QMessageBox()
        name = self.lineEdit_username.text()
        password = self.lineEdit_password.text()
        if name is None or not name:
            msg.setText('Please enter a username.')
            msg.exec()
            return

        if password is None or not password:
            msg.setText('Please enter a password.')
            msg.exec()
            return

        df = db.execute(SQLs.SELECT_ALL_USERS_WHERE_NAME_AND_PASSWORD.format(
            name=name,
            password=password
        ), conn_s=db.CONN)

        if df.shape[0] == 0:
            msg.setText("Sorry, this user is not registered in teh system.")
            msg.exec()
            return

        if password not in df['password'].to_numpy():
            msg.setText('Incorrect Password.')
            msg.exec()
            return

        user = db_models.User(
            company_id=df['company_id'].iloc[0],
            status=df['status'].iloc[0],
            password=df['password'].iloc[0],
            user_id=df['user_id'].iloc[0],
            logout=df['logout'].iloc[0],
            sync_id=df['sync_id'].iloc[0],
            token=df['token'].iloc[0],
            email_address=df['email_address'].iloc[0],
            access_level=df['access_level'].iloc[0],
            name=df['name'].iloc[0],
            start_work_at=pd.to_datetime(df['start_work_at']).iloc[0],
        )

        if self.remember_me.isChecked():
            utils.remember_me(user, consts.REMEMBER_ME_FILE_PATH)

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
        user = utils.get_me(consts.REMEMBER_ME_FILE_PATH)
        if user is None or not user.email_address:
            return None
        else:
            self.next_screen(user)
            return True
        pass

    def next_screen(self, user):

        if self.main_screen is None:
            self.main_screen = MainAppA(
                title='FigurozTimeTracker',
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
    # TODO: work to remove the double click behavior

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

        self.__fill_projects_qlist()
        self.__fill_tasks_qlist_dict()

        self.__fill_with_last_active_project()

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

        self.parent.show()
        self.hide()
        self.destroy()

    def __init_ui(self, title, left, top, height):
        self.setWindowTitle(title)
        self.setGeometry(left, top, int(height * 1.4), height)

        self.setMinimumHeight(height)
        self.setMaximumHeight(height)

        self.setMinimumWidth(int(height * 1.4))
        self.setMaximumWidth(int(height * 1.4))
        # self.setWindowIcon(QIcon('logo.png'))

    def __init_layouts(self):
        layout = QGridLayout()
        layout.sizeConstraint = QLayout.SizeConstraint.SetDefaultConstraint

        main_widget = QWidget()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

        # Define The Project Description Layout
        title_layout = QGridLayout()
        self.lbl_active_project = QLabel('Active Project: ')
        title_layout.addWidget(self.lbl_active_project, 0, 0)

        self.lbl_total_time = QLabel('Project Timer: ', )
        title_layout.addWidget(self.lbl_total_time, 0, 1)

        self.lbl_active_task = QLabel('Active Task: ')
        title_layout.addWidget(self.lbl_active_task, 1, 0)

        self.lbl_task_time = QLabel('Task Timer: ')
        title_layout.addWidget(self.lbl_task_time, 1, 1)

        self.lbl_project_time_tracker = models.TimeTracker()
        title_layout.addWidget(self.lbl_project_time_tracker, 0, 2)
        #
        self.lbl_task_time_tracker = models.TimeTracker()
        title_layout.addWidget(self.lbl_task_time_tracker, 1, 2)

        layout.addLayout(title_layout, 0, 1)

        # Define The Project Layout
        self.projects_layout = QHBoxLayout()
        layout.addLayout(self.projects_layout, 2, 0, )

        # Define The SubProjects Layout
        self.sub_projects_layout = QHBoxLayout()
        layout.addLayout(self.sub_projects_layout, 2, 1, )

    def __init_data(self):
        msg = QMessageBox()
        projects_df = db.execute(SQLs.SELECT_ALL_PROJECTS_WHERE_USER_AND_COMPANY.format(
            user=self.user.sync_id, company_id=self.user.company_id,
        ), conn_s=db.CONN)

        if projects_df.shape[0] == 0:
            msg.setText('This user has no active projects to show.')
            msg.exec()
            return

        subs_df = db.execute(SQLs.SELECT_ALL_TASKS_WHERE_PROJECTS_AND_USER.format(
            user=self.user.sync_id,
            project_id_tuple=tuple(projects_df['project_id'].values)
        ), conn_s=db.CONN)

        if subs_df.shape[0] == 0:
            msg.setText('This user has no active sub-projects to show.')
            msg.exec()
            return

        self.projects = [db_models.Project(
            project_id=a.project_id,
            name=a.name.title(),
            status=a.status,
            entry_id=a.entry_id,
            m_user=a.m_user,
            company_id=a.company_id,
        ) for a in projects_df.itertuples()]

        tasks = [db_models.Task(
            project_id=a.project_id,
            sub_id=a.sub_id,
            status=a.status,
            entry_id=a.entry_id,
            m_user=a.m_user,
            company_id=a.company_id,
            description=a.description.title(),
            is_select=a.is_select,
        ) for a in subs_df.itertuples()]

        del projects_df, subs_df

        # assign tasks to projects
        for i in range(len(self.projects)):
            self.projects[i].tasks = utils.pid_filter(
                pid=self.projects[i].project_id,
                lst=tasks,
            )

    def __fill_projects_qlist(self):
        self.projects_list_widget = QListWidget()
        self.projects_list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.projects_list_widget.setSpacing(10)
        self.projects_list_widget.setStyleSheet(consts.PROJECTS_LISTWIDGET_STYLESHEET)

        self.projects_layout.addWidget(
            self.projects_list_widget
        )

        for project in self.projects:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, project)
            item.setText(project.name)
            self.projects_list_widget.addItem(item)

        self.projects_list_widget.itemClicked.connect(self.__show_project_ui)

    def __show_project_ui(self, item, ):
        if type(item) is not db_models.Project:
            project = item.data(Qt.ItemDataRole.UserRole)
            print(item.text())
        else:
            # self.active_project = item
            project = item
            self.lbl_active_project.setText(
                utils.extract_before_from(self.lbl_active_project.text(), ': ') + project.name
            )

        # Collect Durations from the DB
        df = db.execute(SQLs.SELECT_DURATION_TIMELINES_WHERE_PROJECT_AND_USER_AND_DATE.format(
            user=self.user.sync_id,
            project_id=project.project_id,
            today=datetime.today().strftime('%Y%m%d')
        ), conn_s=db.CONN)
        self.duration = pd.to_timedelta(df.duration).sum()

        if type(item) is db_models.Project:  # if and only if reloaded from remember me
            self.lbl_project_time_tracker.reset(
                self.duration
            )

        for key in self.tasks_qlist_dict.keys():
            self.tasks_qlist_dict[key].hide()

        self.sub_projects_layout.addWidget(self.tasks_qlist_dict[project.project_id])
        self.tasks_qlist_dict[project.project_id].show()
        self.tasks_qlist_dict[project.project_id].itemClicked.connect(self.__start_timer)
        self.tasks_qlist_dict[project.project_id].itemChanged.connect(self.__pause_timer)
        self.tasks_qlist_dict[project.project_id].itemDoubleClicked.connect(self.__pause_timer)

    def __fill_tasks_qlist_dict(self):
        for project in self.projects:
            sub_qlist = QListWidget()
            sub_qlist.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            sub_qlist.setSpacing(1)

            df = db.execute(
                SQLs.SELECT_TASKID_AND_DURATION_AND_DURATION_TIMELINES_WHERE_PROJECT_AND_USER_AND_DATE.format(
                    user=self.user.sync_id,
                    project_id=project.project_id,
                    today=datetime.today().strftime('%Y%m%d')
                ), conn_s=db.CONN)

            if not df.empty:
                df.duration = pd.to_timedelta(df.duration)
                df.sub_id = pd.to_numeric(df.sub_id)
                df = df.groupby('sub_id').sum()

            for i, sub in enumerate(project.tasks):

                timeline = db_models.ProjectTimeLine(
                    project_id=project.project_id,
                    sub_id=sub.sub_id,
                    user=self.user.sync_id,
                )
                if not df.empty and int(sub.sub_id) in df.index.astype(int):
                    timeline.duration = df.loc[int(sub.sub_id), 'duration']

                self.tasks_timers_dict[sub.sub_id] = models.CustomTimer(
                    timeline,
                )

                self.tasks_timers_dict[sub.sub_id].attach(sub.sub_id)

                item = QListWidgetItem(sub_qlist)
                item.setData(Qt.ItemDataRole.UserRole, sub)
                item.setText(sub.description)
                sub_qlist.addItem(item)
                sub_qlist.setItemWidget(item, self.tasks_timers_dict[sub.sub_id])

            self.tasks_qlist_dict[project.project_id] = sub_qlist

        pass

    def __start_timer(self, item):
        # Receive the Task
        task = item.data(Qt.ItemDataRole.UserRole)

        if self.active_task is not None and self.active_project is not None:
            if self.active_project.project_id == task.project_id:
                self.duration = self.lbl_project_time_tracker.time

        # Make sure all other timers are paused before activating a new timer
        for sub_id in self.tasks_timers_dict:
            if self.tasks_timers_dict[sub_id].flag and task.sub_id != sub_id:
                self.tasks_timers_dict[sub_id].pause()

        self.lbl_project_time_tracker.reset(self.duration)
        self.lbl_project_time_tracker.start()

        # Activate the Task TimeTracker in the titles grid
        self.lbl_task_time_tracker.reset(self.tasks_timers_dict[task.sub_id].time)
        self.lbl_task_time_tracker.start()

        # Activate the actual timer
        self.tasks_timers_dict[task.sub_id].start()
        self.tasks_timers_dict[task.sub_id].show_time(mode='display')

        # Retrieve the project
        self.active_project = utils.pid_filter(
            task.project_id,
            self.projects
        )[0]
        self.active_task = task

        # Fill the titles
        self.lbl_active_project.setText(
            utils.extract_before_from(self.lbl_active_project.text(), ': ') + self.active_project.name
        )
        self.lbl_active_task.setText(
            utils.extract_before_from(self.lbl_active_task.text(), ': ') + task.description
        )

    def __pause_timer(self, item):
        task = item.data(Qt.ItemDataRole.UserRole)
        self.tasks_timers_dict[task.sub_id].pause()
        self.lbl_task_time_tracker.pause()
        self.lbl_project_time_tracker.pause()
        # self.duration = self.lbl_project_time_tracker.time
        # print('Duration in the Pause', self.duration)
        # print('Appeared Duration in Pause', self.duration)
        self.tasks_timers_dict[task.sub_id].show_time(mode='display')
        pass

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        for sub_id in self.tasks_timers_dict:
            if self.tasks_timers_dict[sub_id].flag:
                self.tasks_timers_dict[sub_id].pause()
        utils.remember_me(
            self.active_project,
            consts.REMEMBER_LAST_ACTIVE_FILE_PATH
        )

        super().closeEvent(a0)

    def __fill_with_last_active_project(self):
        msg = QMessageBox()
        project = utils.get_me(consts.REMEMBER_LAST_ACTIVE_FILE_PATH)

        if project is None or not project.project_id:
            msg.setText('Failed to load project as nothing was saved.')
            msg.exec()
            return None

        if not utils.pid_filter(project.project_id, self.projects):
            msg.setText('Failed to load project as it was removed from the database.')
            msg.exec()
            return None

        self.__show_project_ui(project)


if __name__ == '__main__':
    db.initiate_database(db.CONN)

    app = QApplication(sys.argv)
    form = LoginForm()

    if not os.path.exists(consts.REMEMBER_ME_FILE_PATH):
        form.show()

    db.CONN.close()
    sys.exit(app.exec())
