from abc import ABC, abstractmethod
from datetime import datetime, date

import models


class Model(ABC):
    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr[attr.rfind('__') + 2:], value

    def __str__(self):
        return f"{type(self).__name__}(" + ', '.join(
            [f"{attr[attr.rfind('__') + 2:]}={value}" for attr, value in self.__dict__.items()]
        ) + ")"

    def __repr__(self):
        return self.__str__()

    pass


class Application(Model):
    def __init__(
            self, app_id: str, name: str, file_name: str, version: str, description: str, company: str, sync: int,
            user_id: int, entry_id: str, project_id: str, user: str, win_name: str, ico: str
    ) -> None:
        super(Application, self).__init__()
        self.__app_id = app_id
        self.__name = name
        self.__file_name = file_name
        self.__version = version
        self.__description = description
        self.__company = company
        self.__sync = sync
        self.__user_id = user_id
        self.__entry_id = entry_id
        self.__project_id = project_id
        self.__user = user
        self.__win_name = win_name
        self.__ico = ico

    def __get_app_id(self):
        return self.__app_id

    def __set_app_id(self, app_id):
        self.__app_id = app_id

    app_id = property(
        fget=__get_app_id,
        fset=__set_app_id,
        doc='None.',
    )

    def __get_ico(self):
        return self.__ico

    def __set_ico(self, ico):
        self.__ico = ico

    ico = property(
        fget=__get_ico,
        fset=__set_ico,
        doc='None.',
    )

    def __get_win_name(self):
        return self.__win_name

    def __set_win_name(self, win_name):
        self.__win_name = win_name

    win_name = property(
        fget=__get_win_name,
        fset=__set_win_name,
        doc='None.',
    )

    def __get_user(self):
        return self.__user

    def __set_user(self, user):
        self.__user = user

    user = property(
        fget=__get_user,
        fset=__set_user,
        doc='None.',
    )

    def __get_project_id(self):
        return self.__project_id

    def __set_project_id(self, project_id):
        self.__project_id = project_id

    project_id = property(
        fget=__get_project_id,
        fset=__set_project_id,
        doc='None.',
    )

    def __get_entry_id(self):
        return self.__entry_id

    def __set_entry_id(self, entry_id):
        self.__entry_id = entry_id

    entry_id = property(
        fget=__get_entry_id,
        fset=__set_entry_id,
        doc='None.',
    )

    def __get_user_id(self):
        return self.__user_id

    def __set_user_id(self, user_id):
        self.__user_id = user_id

    user_id = property(
        fget=__get_user_id,
        fset=__set_user_id,
        doc='None.',
    )

    def __get_sync(self):
        return self.__sync

    def __set_sync(self, sync):
        self.__sync = sync

    sync = property(
        fget=__get_sync,
        fset=__set_sync,
        doc='None.',
    )

    def __get_company(self):
        return self.__company

    def __set_company(self, company):
        self.__company = company

    company = property(
        fget=__get_company,
        fset=__set_company,
        doc='The owner company of the application.',
    )

    def __get_description(self):
        return self.__description

    def __set_description(self, description):
        self.__description = description

    description = property(
        fget=__get_description,
        fset=__set_description,
        doc='Simple description over the application.',
    )

    def __get_version(self):
        return self.__version

    def __set_version(self, version):
        self.__version = version

    version = property(
        fget=__get_version,
        fset=__set_version,
        doc='Application version on the local device.',
    )

    def __get_file_name(self):
        return self.__file_name

    def __set_file_name(self, file_name):
        self.__file_name = file_name

    file_name = property(
        fget=__get_file_name,
        fset=__set_file_name,
        doc='Application absolute path to the execution file.',
    )

    def __get_name(self):
        return self.__name

    def __set_name(self, name):
        self.__name = name

    name = property(
        fget=__get_name,
        fset=__set_name,
        doc='Application name.',
    )


class Task(Model):
    def __init__(self, project_id: str, sub_id: str, company_id: str, status: str, is_select: str, entry_id: str,
                 m_user: str, description: str) -> None:
        super(Task, self).__init__()
        self.__project_id = project_id
        self.__sub_id = sub_id
        self.__status = status
        self.__is_select = is_select
        self.__entry_id = entry_id
        self.__m_user = m_user
        self.__company_id = company_id
        self.__description = description
        self.__timer = None

    def __get_timer(self):
        return self.__timer

    def __set_timer(self, parent):
        self.__timer = models.CustomTimer(parent=parent)

    timer = property(
        fget=__get_timer,
        fset=__set_timer,
        doc='None.',
    )

    def __get_is_select(self):
        return self.__is_select

    def __set_is_select(self, is_select):
        self.__is_select = is_select

    is_select = property(
        fget=__get_is_select,
        fset=__set_is_select,
        doc='None.',
    )

    def __get_project_id(self):
        return self.__project_id

    def __set_project_id(self, project_id):
        self.__project_id = project_id

    project_id = property(
        fget=__get_project_id,
        fset=__set_project_id,
        doc='None.',
    )

    def __get_description(self):
        return self.__description

    def __set_description(self, description):
        self.__description = description

    description = property(
        fget=__get_description,
        fset=__set_description,
        doc='None.',
    )

    def __get_sub_id(self):
        return self.__sub_id

    def __set_sub_id(self, sub_id):
        self.__sub_id = sub_id

    sub_id = property(
        fget=__get_sub_id,
        fset=__set_sub_id,
        doc='None.',
    )

    def __get_company_id(self):
        return self.__company_id

    def __set_company_id(self, company_id):
        self.__company_id = company_id

    company_id = property(
        fget=__get_company_id,
        fset=__set_company_id,
        doc='None.',
    )

    def __get_m_user(self):
        return self.__m_user

    def __set_m_user(self, m_user):
        self.__m_user = m_user

    m_user = property(
        fget=__get_m_user,
        fset=__set_m_user,
        doc='None.',
    )

    def __get_status(self):
        return self.__status

    def __set_status(self, status):
        self.__status = status

    status = property(
        fget=__get_status,
        fset=__set_status,
        doc='None.',
    )

    def __get_entry_id(self):
        return self.__entry_id

    def __set_entry_id(self, entry_id):
        self.__entry_id = entry_id

    entry_id = property(
        fget=__get_entry_id,
        fset=__set_entry_id,
        doc='None.',
    )


class Project(Model):
    def __init__(self, project_id: str, name: str, status: str, entry_id: str, m_user: str, company_id: str,
                 tasks: list = None) -> None:
        super(Project, self).__init__()
        self.__project_id = project_id
        self.__name = name
        self.__status = status
        self.__entry_id = entry_id
        self.__m_user = m_user
        self.__company_id = company_id
        if tasks is not None:
            self.__tasks = tasks.copy()
        else:
            self.__tasks = []

    def __get_project_id(self):
        return self.__project_id

    def __set_project_id(self, project_id):
        self.__project_id = project_id

    project_id = property(
        fget=__get_project_id,
        fset=__set_project_id,
        doc='None.',
    )

    def __get_company_id(self):
        return self.__company_id

    def __set_company_id(self, company_id):
        self.__company_id = company_id

    company_id = property(
        fget=__get_company_id,
        fset=__set_company_id,
        doc='None.',
    )

    def __get_m_user(self):
        return self.__m_user

    def __set_m_user(self, m_user):
        self.__m_user = m_user

    m_user = property(
        fget=__get_m_user,
        fset=__set_m_user,
        doc='None.',
    )

    def __get_status(self):
        return self.__status

    def __set_status(self, status):
        self.__status = status

    status = property(
        fget=__get_status,
        fset=__set_status,
        doc='None.',
    )

    def __get_entry_id(self):
        return self.__entry_id

    def __set_entry_id(self, entry_id):
        self.__entry_id = entry_id

    entry_id = property(
        fget=__get_entry_id,
        fset=__set_entry_id,
        doc='None.',
    )

    def __get_name(self):
        return self.__name

    def __set_name(self, name):
        self.__name = name

    name = property(
        fget=__get_name,
        fset=__set_name,
        doc='Application name.',
    )

    def __get_tasks(self):
        return self.__tasks.copy()

    def __set_tasks(self, tasks: list[Task]):
        self.__tasks = tasks.copy()

    def add_sub_project(self, task: Task):
        self.tasks += [task]

    tasks = property(
        fget=__get_tasks,
        fset=__set_tasks,
        doc='Application name.',
    )


class ProjectDuration(Model):
    def __init__(self, project_id: str, sub_id: str, entry_id: str, day: date, text: str, duration: str, user_id: str,
                 sync: str, day_format: str, ) -> None:
        super(ProjectDuration, self).__init__()
        self.__project_id = project_id
        self.__sub_id = sub_id
        self.__entry_id = entry_id
        self.__day = day
        self.__text = text
        self.__duration = duration
        self.__user_id = user_id
        self.__sync = sync
        self.__day_format = day_format

    def __get_day_format(self):
        return self.__day_format

    def __set_day_format(self, day_format):
        self.__day_format = day_format

    day_format = property(
        fget=__get_day_format,
        fset=__set_day_format,
        doc='None.',
    )

    def __get_sync(self):
        return self.__sync

    def __set_sync(self, sync):
        self.__sync = sync

    sync = property(
        fget=__get_sync,
        fset=__set_sync,
        doc='None.',
    )

    def __get_user_id(self):
        return self.__user_id

    def __set_user_id(self, user_id):
        self.__user_id = user_id

    user_id = property(
        fget=__get_user_id,
        fset=__set_user_id,
        doc='None.',
    )

    def __get_duration(self):
        return self.__duration

    def __set_duration(self, duration):
        self.__duration = duration

    duration = property(
        fget=__get_duration,
        fset=__set_duration,
        doc='None.',
    )

    def __get_text(self):
        return self.__text

    def __set_text(self, text):
        self.__text = text

    text = property(
        fget=__get_text,
        fset=__set_text,
        doc='None.',
    )

    def __get_day(self):
        return self.__day

    def __set_day(self, day):
        self.__day = day

    day = property(
        fget=__get_day,
        fset=__set_day,
        doc='None.',
    )

    def __get_entry_id(self):
        return self.__entry_id

    def __set_entry_id(self, entry_id):
        self.__entry_id = entry_id

    entry_id = property(
        fget=__get_entry_id,
        fset=__set_entry_id,
        doc='None.',
    )

    def __get_sub_id(self):
        return self.__sub_id

    def __set_sub_id(self, sub_id):
        self.__sub_id = sub_id

    sub_id = property(
        fget=__get_sub_id,
        fset=__set_sub_id,
        doc='None.',
    )

    def __get_project_id(self):
        return self.__project_id

    def __set_project_id(self, project_id):
        self.__project_id = project_id

    project_id = property(
        fget=__get_project_id,
        fset=__set_project_id,
        doc='None.',
    )


class ProjectTimeLine(Model):
    def __init__(self, project_id: str, current_project_line_id: str, sub_id: str, start_time: str, time_end: str,
                 user: str, entry_id: str, duration: str, date_ended: datetime, sync: str, day_format: str, ) -> None:
        super().__init__()
        self.__project_id = project_id
        self.__sub_id = sub_id
        self.__entry_id = entry_id
        self.__current_project_line_id = current_project_line_id
        self.__start_time = start_time
        self.__duration = duration
        self.__time_end = time_end
        self.__sync = sync
        self.__user = user
        self.__date_ended = date_ended
        self.__day_format = day_format

    def __get_date_ended(self):
        return self.__date_ended

    def __set_date_ended(self, date_ended):
        self.__date_ended = date_ended

    date_ended = property(
        fget=__get_date_ended,
        fset=__set_date_ended,
        doc='None.',
    )

    def __get_user(self):
        return self.__user

    def __set_user(self, user):
        self.__user = user

    user = property(
        fget=__get_user,
        fset=__set_user,
        doc='None.',
    )

    def __get_time_end(self):
        return self.__time_end

    def __set_time_end(self, time_end):
        self.__time_end = time_end

    time_end = property(
        fget=__get_time_end,
        fset=__set_time_end,
        doc='None.',
    )

    def __get_start_time(self):
        return self.__start_time

    def __set_start_time(self, start_time):
        self.__start_time = start_time

    start_time = property(
        fget=__get_start_time,
        fset=__set_start_time,
        doc='None.',
    )

    def __get_current_project_line_id(self):
        return self.__current_project_line_id

    def __set_current_project_line_id(self, current_project_line_id):
        self.__current_project_line_id = current_project_line_id

    current_project_line_id = property(
        fget=__get_current_project_line_id,
        fset=__set_current_project_line_id,
        doc='None.',
    )

    def __get_day_format(self):
        return self.__day_format

    def __set_day_format(self, day_format):
        self.__day_format = day_format

    day_format = property(
        fget=__get_day_format,
        fset=__set_day_format,
        doc='None.',
    )

    def __get_sync(self):
        return self.__sync

    def __set_sync(self, sync):
        self.__sync = sync

    sync = property(
        fget=__get_sync,
        fset=__set_sync,
        doc='None.',
    )

    def __get_duration(self):
        return self.__duration

    def __set_duration(self, duration):
        self.__duration = duration

    duration = property(
        fget=__get_duration,
        fset=__set_duration,
        doc='None.',
    )

    def __get_entry_id(self):
        return self.__entry_id

    def __set_entry_id(self, entry_id):
        self.__entry_id = entry_id

    entry_id = property(
        fget=__get_entry_id,
        fset=__set_entry_id,
        doc='None.',
    )

    def __get_sub_id(self):
        return self.__sub_id

    def __set_sub_id(self, sub_id):
        self.__sub_id = sub_id

    sub_id = property(
        fget=__get_sub_id,
        fset=__set_sub_id,
        doc='None.',
    )

    def __get_project_id(self):
        return self.__project_id

    def __set_project_id(self, project_id):
        self.__project_id = project_id

    project_id = property(
        fget=__get_project_id,
        fset=__set_project_id,
        doc='None.',
    )


class User(Model):
    def __init__(self, user_id: str, syncid: str, token: str, company_id: str, email_address: str, password: str,
                 status: str, logout: str, access_level: str, start_work_at: datetime, name: str, ) -> None:
        super(User, self).__init__()
        self.__user_id = user_id
        self.__syncid = syncid
        self.__token = token
        self.__company_id = company_id
        self.__email_address = email_address
        self.__password = password
        self.__status = status
        self.__logout = logout
        self.__access_level = access_level
        self.__start_work_at = start_work_at
        self.__name = name

    def __get_start_work_at(self):
        return self.__start_work_at

    def __set_start_work_at(self, start_work_at):
        self.__start_work_at = start_work_at

    start_work_at = property(
        fget=__get_start_work_at,
        fset=__set_start_work_at,
        doc='None.',
    )

    def __get_access_level(self):
        return self.__access_level

    def __set_access_level(self, access_level):
        self.__access_level = access_level

    access_level = property(
        fget=__get_access_level,
        fset=__set_access_level,
        doc='None.',
    )

    def __get_logout(self):
        return self.__logout

    def __set_logout(self, logout):
        self.__logout = logout

    logout = property(
        fget=__get_logout,
        fset=__set_logout,
        doc='None.',
    )

    def __get_status(self):
        return self.__status

    def __set_status(self, status):
        self.__status = status

    status = property(
        fget=__get_status,
        fset=__set_status,
        doc='None.',
    )

    def __get_password(self):
        return self.__password

    def __set_password(self, password):
        self.__password = password

    password = property(
        fget=__get_password,
        fset=__set_password,
        doc='None.',
    )

    def __get_email_address(self):
        return self.__email_address

    def __set_email_address(self, email_address):
        self.__email_address = email_address

    email_address = property(
        fget=__get_email_address,
        fset=__set_email_address,
        doc='None.',
    )

    def __get_company_id(self):
        return self.__company_id

    def __set_company_id(self, company_id):
        self.__company_id = company_id

    company_id = property(
        fget=__get_company_id,
        fset=__set_company_id,
        doc='None.',
    )

    def __get_token(self):
        return self.__token

    def __set_token(self, token):
        self.__token = token

    token = property(
        fget=__get_token,
        fset=__set_token,
        doc='None.',
    )

    def __get_syncid(self):
        return self.__syncid

    def __set_syncid(self, syncid):
        self.__syncid = syncid

    syncid = property(
        fget=__get_syncid,
        fset=__set_syncid,
        doc='None.',
    )

    def __get_user_id(self):
        return self.__user_id

    def __set_user_id(self, user_id):
        self.__user_id = user_id

    user_id = property(
        fget=__get_user_id,
        fset=__set_user_id,
        doc='None.',
    )

    def __get_name(self):
        return self.__name

    def __set_name(self, name):
        self.__name = name

    name = property(
        fget=__get_name,
        fset=__set_name,
        doc='Application name.',
    )


class Window(Model):
    def __init__(self, window_id: str, app_id: str, entry_id: str, project_id: str, sync: str, m_time: str,
                 user: str, time_line_id: str, app_name: str, master_col: str, title: str, m_url: str, ) -> None:
        super().__init__()
        self.__window_id = window_id
        self.__app_id = app_id
        self.__entry_id = entry_id
        self.__project_id = project_id
        self.__sync = sync
        self.__m_time = m_time
        self.__user = user
        self.__time_line_id = time_line_id
        self.__app_name = app_name
        self.__master_col = master_col
        self.__title = title
        self.__m_url = m_url

    def __get_m_url(self):
        return self.__m_url

    def __set_m_url(self, m_url):
        self.__m_url = m_url

    m_url = property(
        fget=__get_m_url,
        fset=__set_m_url,
        doc='None.',
    )

    def __get_master_col(self):
        return self.__master_col

    def __set_master_col(self, master_col):
        self.__master_col = master_col

    master_col = property(
        fget=__get_master_col,
        fset=__set_master_col,
        doc='None.',
    )

    def __get_app_name(self):
        return self.__app_name

    def __set_app_name(self, app_name):
        self.__app_name = app_name

    app_name = property(
        fget=__get_app_name,
        fset=__set_app_name,
        doc='None.',
    )

    def __get_time_line_id(self):
        return self.__time_line_id

    def __set_time_line_id(self, time_line_id):
        self.__time_line_id = time_line_id

    time_line_id = property(
        fget=__get_time_line_id,
        fset=__set_time_line_id,
        doc='None.',
    )

    def __get_user(self):
        return self.__user

    def __set_user(self, user):
        self.__user = user

    user = property(
        fget=__get_user,
        fset=__set_user,
        doc='None.',
    )

    def __get_m_time(self):
        return self.__m_time

    def __set_m_time(self, m_time):
        self.__m_time = m_time

    m_time = property(
        fget=__get_m_time,
        fset=__set_m_time,
        doc='None.',
    )

    def __get_sync(self):
        return self.__sync

    def __set_sync(self, sync):
        self.__sync = sync

    sync = property(
        fget=__get_sync,
        fset=__set_sync,
        doc='None.',
    )

    def __get_project_id(self):
        return self.__project_id

    def __set_project_id(self, project_id):
        self.__project_id = project_id

    project_id = property(
        fget=__get_project_id,
        fset=__set_project_id,
        doc='None.',
    )

    def __get_entry_id(self):
        return self.__entry_id

    def __set_entry_id(self, entry_id):
        self.__entry_id = entry_id

    entry_id = property(
        fget=__get_entry_id,
        fset=__set_entry_id,
        doc='None.',
    )

    def __get_app_id(self):
        return self.__app_id

    def __set_app_id(self, app_id):
        self.__app_id = app_id

    app_id = property(
        fget=__get_app_id,
        fset=__set_app_id,
        doc='None.',
    )

    def __get_window_id(self):
        return self.__window_id

    def __set_window_id(self, window_id):
        self.__window_id = window_id

    window_id = property(
        fget=__get_window_id,
        fset=__set_window_id,
        doc='None.',
    )

    def __get_title(self):
        return self.__title

    def __set_title(self, title):
        self.__title = title

    title = property(
        fget=__get_title,
        fset=__set_title,
        doc='Application name.',
    )


if __name__ == "__main__":
    # p = Task(
    #     project_id='', sub_id="", entry_id="", company_id="", description="", m_user='', status='',
    # )
    # print(dict(p))
    # print(p)

    pass
