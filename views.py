import os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QListWidget, QHBoxLayout, QPushButton, QGridLayout, \
    QLabel, QMenu, QMainWindow, QLayout, QListWidgetItem, \
    QAbstractItemView, QLineEdit, QMessageBox, QCheckBox
from PyQt6.QtGui import QIcon, QAction

import db
import models

import os.path
import pickle
import sys

import pandas as pd

import db_models
import utils
from db import create_db_connection
import consts


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

        conn = create_db_connection(host_config='local', config_path='env')
        df = conn.select(f"select * from Uzers where Name = '{name}' and Password = '{password}'")
        conn.close()

        if df.shape[0] == 0:
            msg.setText("Sorry, this user is not registered in teh system.")
            msg.exec()
            return

        if password not in df['Password'].to_numpy():
            msg.setText('Incorrect Password.')
            msg.exec()
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
        if os.path.exists(consts.REMEMBER_ME_FILE_PATH):
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
        with open(consts.REMEMBER_ME_FILE_PATH, 'bw') as file:
            pickle.dump(user, file)

    def __getMe(self):
        with open(consts.REMEMBER_ME_FILE_PATH, 'rb') as file:
            user = pickle.load(file)
        return user

    def next_screen(self, user):

        if self.main_screen is None:
            self.main_screen = MainApp(
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


class MainApp(QMainWindow):

    def __init__(self, title, left, top, height, parent=None, user=None):
        super(MainApp, self).__init__(parent)
        self.__init_ui(title, left, top, height)

        self.user = user
        self.parent = parent

        self._ = None  # dummy var for internal use
        self.tasks_qlist_dict = {}  # dummy var for internal use
        # self.active_projects = {}
        # self.active_sub_projects = {}
        self.projects = []
        # self.tasks = []

        self.__init_data()

        self.__create_menu_bar()

        self.__init_layouts()

        self.__fill_projects_qlist()
        self.__fill_tasks_qlist_dict()

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
        self.lbl_pr_name = QLabel('Project: ')
        title_layout.addWidget(self.lbl_pr_name, 0, 0)

        self.lbl_pr_state = QLabel('State: ')
        title_layout.addWidget(self.lbl_pr_state, 1, 0)

        self.lbl_pr_total_time = QLabel('Total Time: ', )
        title_layout.addWidget(self.lbl_pr_total_time, 0, 1)

        self.lbl_pr_active_task = QLabel('Current Active Task: ')
        title_layout.addWidget(self.lbl_pr_active_task, 1, 1)

        layout.addLayout(title_layout, 0, 1)

        # Define The Project Layout
        self.projects_layout = QHBoxLayout()
        layout.addLayout(self.projects_layout, 2, 0, )

        # Define The SubProjects Layout
        self.sub_projects_layout = QHBoxLayout()
        layout.addLayout(self.sub_projects_layout, 2, 1, )

    def __init_data(self):
        msg = QMessageBox()
        projects_df = db.load_data(
            f"select * from Project "
            f"where m_user = '{self.user.syncid}' and CompanyID = '{self.user.company_id}' "
            f"and Status = '1' "
        )

        if projects_df.shape[0] == 0:
            msg.setText('This user has no active projects to show.')
            msg.exec()
            return

        subs_df = db.load_data(
            f"select * from subproject "
            f"where ProjectID in {tuple(projects_df['ProjectID'].values)} and m_user = '{self.user.syncid}' "
            f"and Status = '1' "
        )

        if subs_df.shape[0] == 0:
            msg.setText('This user has no active sub-projects to show.')
            msg.exec()
            return

        self.projects = [db_models.Project(
            project_id=a.ProjectID,
            name=a.Name.title(),
            status=a.Status,
            entry_id=a.EntryID,
            m_user=a.m_user,
            company_id=a.CompanyID,

        ) for a in projects_df.itertuples()]

        tasks = [db_models.Task(
            project_id=a.ProjectID,
            sub_id=a.subID,
            status=a.Status,
            entry_id=a.EntryID,
            m_user=a.m_user,
            company_id=a.CompanyID,
            description=a.description.title(),
            is_select=a.isselect,
        ) for a in subs_df.itertuples()]

        del projects_df, subs_df

        for i in range(len(self.projects)):
            self.projects[i].tasks = utils.pid_filter(
                pid=self.projects[i].project_id,
                lst=tasks,
            )

    def __fill_tasks_qlist_dict(self):
        for project in self.projects:
            sub_qlist = QListWidget()
            sub_qlist.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            sub_qlist.setSpacing(1)

            for i, sub in enumerate(project.tasks):
                # TODO: try the inverse method, where the timers are in a dict here {sub_id -> timer}
                #  and
                sub.timer = sub_qlist
                item = QListWidgetItem(sub_qlist)
                item.setData(Qt.ItemDataRole.UserRole, tuple([project, i]))
                item.setText(sub.description)
                sub_qlist.addItem(item)
                sub_qlist.setItemWidget(item, sub.timer)

            self.tasks_qlist_dict[project.project_id] = sub_qlist
        pass

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
        project = item.data(Qt.ItemDataRole.UserRole)

        self.lbl_pr_name.setText(utils.extract_before_from(self.lbl_pr_name.text(), ': ') + project.name)

        self.lbl_pr_state.setText(utils.extract_before_from(self.lbl_pr_state.text(), ': ') + project.status)

        for key in self.tasks_qlist_dict.keys():
            self.tasks_qlist_dict[key].hide()

        self.sub_projects_layout.addWidget(self.tasks_qlist_dict[project.project_id])
        self.tasks_qlist_dict[project.project_id].show()

        # self.tasks_qlist_dict[project.project_id].itemClicked.connect(self.__start_timer)
        self.tasks_qlist_dict[project.project_id].itemClicked.connect(self.__start_timer)
        self.tasks_qlist_dict[project.project_id].itemChanged.connect(self.__pause_timer)
        self.tasks_qlist_dict[project.project_id].itemDoubleClicked.connect(self.__pause_timer)

    def __start_timer(self, item):
        project, task_idx = item.data(Qt.ItemDataRole.UserRole)
        self.lbl_pr_active_task.setText(
            utils.extract_before_from(self.lbl_pr_active_task.text(), ': ') + project.tasks[task_idx].description
        )
        # TODO: activate this lbl
        # title_total_time_pr = self.lbl_pr_total_time.text()[:self.lbl_pr_total_time.text().find(': ') + 2]
        # self.lbl_pr_total_time.setText(self.active_sub_projects[temp.sub_id].timer.label)

        for pro in self.projects:
            for tsk in pro.tasks:
                if tsk.timer.flag:
                    tsk.timer.pause()

        project.tasks[task_idx].timer.start()
        project.tasks[task_idx].timer.show_time(mode='display')
        pass

    def __pause_timer(self, item):
        project, task_idx = item.data(Qt.ItemDataRole.UserRole)
        project.tasks[task_idx].timer.pause()
        project.tasks[task_idx].timer.show_time(mode='display')
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)

    form = LoginForm()
    if not os.path.exists(consts.REMEMBER_ME_FILE_PATH):
        form.show()

    # sys.exit(app.exec())
    sys.exit(app.exec())
