from __future__ import annotations

from datetime import datetime, timedelta, time, timezone

from database.common import DataModel
from database import db, SQLs
from common import consts, utils


class Task(DataModel):

    def register(self, conn):
        pass

    def __init__(self, project_id: int, id: int, status: int, name: str, ) -> None:
        super(Task, self).__init__()
        self.__id = id
        self.__project_id = project_id
        self.__name = name
        self.__status = status

    def __get_project_id(self):
        return self.__project_id

    def __set_project_id(self, project_id):
        self.__project_id = project_id

    project_id = property(
        fget=__get_project_id,
        fset=__set_project_id,
        doc='None.',
    )

    def __get_name(self):
        return self.__name

    def __set_name(self, name):
        self.__name = name

    name = property(
        fget=__get_name,
        fset=__set_name,
        doc='None.',
    )

    def __get_id(self):
        return self.__id

    def __set_id(self, id):
        self.__id = id

    id = property(
        fget=__get_id,
        fset=__set_id,
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


class Project(DataModel):
    def register(self, conn):
        pass

    def __init__(self, id: int, name: str, company_id: int, project_access: int = 1, status: int = 1,
                 tasks: list = None, project_groups: list = None, project_members: list = None) -> None:
        super(Project, self).__init__()
        self.__id = id
        self.__name = name
        self.__status = status
        self.__company_id = company_id
        self.__project_access = project_access

        if tasks is not None:
            self.__tasks = tasks.copy()
        else:
            self.__tasks = []

        if project_members is not None:
            self.__project_members = project_members.copy()
        else:
            self.__project_members = []

        if project_groups is not None:
            self.__project_groups = project_groups.copy()
        else:
            self.__project_groups = []

    def __get_project_groups(self):
        return self.__project_groups.copy()

    def __set_project_groups(self, project_groups: list):
        self.__project_groups = project_groups.copy()

    project_groups = property(
        fget=__get_project_groups,
        fset=__set_project_groups,
        doc='Application name.',
    )

    def __get_project_members(self):
        return self.__project_members.copy()

    def __set_project_members(self, project_members: list):
        self.__project_members = project_members.copy()

    project_members = property(
        fget=__get_project_members,
        fset=__set_project_members,
        doc='Application name.',
    )

    def __get_project_access(self):
        return self.__project_access

    def __set_project_access(self, project_access):
        self.__project_access = project_access

    project_access = property(
        fget=__get_project_access,
        fset=__set_project_access,
        doc='None.',
    )

    def __get_id(self):
        return self.__id

    def __set_id(self, id):
        self.__id = id

    id = property(
        fget=__get_id,
        fset=__set_id,
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

    def __get_status(self):
        return self.__status

    def __set_status(self, status):
        self.__status = status

    status = property(
        fget=__get_status,
        fset=__set_status,
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

    tasks = property(
        fget=__get_tasks,
        fset=__set_tasks,
        doc='Application name.',
    )

    def add_sub_project(self, task: Task):
        self.tasks += [task]


# TODO: needs to be re-implemented
class ProjectTimeLine(DataModel):
    def __init__(self,
                 project_id: int,
                 sub_id: int,
                 user: int,
                 sync: int = 0,
                 duration: timedelta = timedelta(seconds=0),
                 time_start: time = datetime.now().time(),
                 day_format: str = datetime.now().date().strftime(consts.DAY_TIME_FORMAT),
                 time_end: time = None,
                 current_project_line_id: str = None,
                 date_ended: datetime = datetime.now(),
                 entry_id: str = None,
                 ) -> None:
        super().__init__()
        self.__project_id = project_id
        self.__sub_id = sub_id

        self.__time_start = time_start
        self.__duration = duration
        self.__time_end = time_end
        self.__sync = sync
        self.__user = user
        self.__date_ended = date_ended
        self.__day_format = day_format

        row_format = str(self.__user) + datetime.now().strftime(consts.ID_TIME_FORMATS)
        if entry_id is None or current_project_line_id is None:
            self.__entry_id = row_format
            self.__current_project_line_id = row_format
        else:
            self.__entry_id = entry_id
            self.__current_project_line_id = current_project_line_id

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

    def __get_time_start(self):
        return self.__time_start

    def __set_time_start(self, start_time: time = datetime.now().time()):
        self.__time_start = start_time

    time_start = property(
        fget=__get_time_start,
        fset=__set_time_start,
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

    def __get_duration(self) -> timedelta:
        return self.__duration

    def __set_duration(self, duration) -> None:
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

    def register(self, conn):
        sql = SQLs.INSERT_NEW_ROW_INTO_PROJECT_TIMELINE.format(
            project_id=self.project_id,
            current_project_line_id=self.current_project_line_id,
            sub_id=self.sub_id,
            time_start=str(self.time_start)[:-7],
            time_end='' if not self.time_end else self.time_end,
            user=self.user,
            entry_id=self.entry_id,
            duration=str(self.duration)[:-7],
            date_ended=str(self.date_ended)[:-7],
            sync=self.sync,
            day_format=self.day_format,

        )
        return db.execute(sql, conn=conn)


class User(DataModel):
    def register(self, conn):
        pass

    def __init__(
            self, id: int, token: str, refresh_token: str, company_id: int, email_address: str, password: str,
            status: int, access_level: int, username: str, code: str, profile_image: str = None,
            screenshot_interval: float = 4.5, can_edit_time: bool = False, blur_screen: bool = True,
            receive_daily_report: bool = True, sync_data: int = 2, can_delete_screencast: bool = False,
            owner_user: int = 2, inactive_time: int = 2, group_members: list = None, group_managers: list = None,
    ) -> None:
        super(User, self).__init__()
        # Required
        self.__id = id
        self.__token = token
        self.__refresh_token = refresh_token
        self.__company_id = company_id
        self.__email_address = email_address
        self.__password = password
        self.__status = status
        self.__access_level = access_level
        self.__username = username
        self.__code = code
        self.__profile_image = profile_image

        # Optional
        self.__screenshot_interval = screenshot_interval
        self.__can_edit_time = can_edit_time
        self.__blur_screen = blur_screen
        self.__receive_daily_report = receive_daily_report
        self.__sync_data = sync_data
        self.__can_delete_screencast = can_delete_screencast
        self.__owner_user = owner_user
        self.__inactive_time = inactive_time
        if group_members is None:
            self.__group_members = []
        else:
            self.__group_members = group_members.copy()

        if group_managers is None:
            self.__group_managers = []
        else:
            self.__group_managers = group_managers.copy()

        # Figure it out
        self.__timezone = datetime.now(timezone.utc).astimezone().tzinfo
        self._ip_address = '127.0.0.1'  # socket.gethostbyname(socket.gethostname())
        self.__current_app_version = consts.APP_VERSION  # TODO: pip install pywin32
        self.__user_location = utils.get_user_location()
        self.__internet_speed = 0.0  # TODO: pip install speedtest-cli --> utils.calculate_internet_speed()

    def __get_internet_speed(self):
        return self.__internet_speed

    def __set_internet_speed(self, internet_speed):
        self.__internet_speed = internet_speed

    internet_speed = property(
        fget=__get_internet_speed,
        fset=__set_internet_speed,
        doc='None.',
    )

    def __get_user_location(self):
        return self.__user_location

    def __set_user_location(self, user_location):
        self.__user_location = user_location

    user_location = property(
        fget=__get_user_location,
        fset=__set_user_location,
        doc='None.',
    )

    def __get_current_app_version(self):
        return self.__current_app_version

    def __set_current_app_version(self, current_app_version):
        self.__current_app_version = current_app_version

    current_app_version = property(
        fget=__get_current_app_version,
        fset=__set_current_app_version,
        doc='None.',
    )

    def __get_ip_address(self):
        return self.__ip_address

    def __set_ip_address(self, ip_address):
        self.__ip_address = ip_address

    ip_address = property(
        fget=__get_ip_address,
        fset=__set_ip_address,
        doc='None.',
    )

    def __get_timezone(self):
        return self.__timezone

    def __set_timezone(self, timezone):
        self.__timezone = timezone

    timezone = property(
        fget=__get_timezone,
        fset=__set_timezone,
        doc='None.',
    )

    def __get_group_managers(self):
        return self.__group_managers.copy()

    def __set_group_managers(self, group_managers: list):
        self.__group_managers = group_managers.copy()

    group_managers = property(
        fget=__get_group_managers,
        fset=__set_group_managers,
        doc='Application name.',
    )

    def __get_group_members(self):
        return self.__group_members.copy()

    def __set_group_members(self, group_members: list):
        self.__group_members = group_members.copy()

    group_members = property(
        fget=__get_group_members,
        fset=__set_group_members,
        doc='Application name.',
    )

    def __get_inactive_time(self):
        return self.__inactive_time

    def __set_inactive_time(self, inactive_time):
        self.__inactive_time = inactive_time

    inactive_time = property(
        fget=__get_inactive_time,
        fset=__set_inactive_time,
        doc='None.',
    )

    def __get_owner_user(self):
        return self.__owner_user

    def __set_owner_user(self, owner_user):
        self.__owner_user = owner_user

    owner_user = property(
        fget=__get_owner_user,
        fset=__set_owner_user,
        doc='None.',
    )

    def __get_can_delete_screencast(self):
        return self.__can_delete_screencast

    def __set_can_delete_screencast(self, can_delete_screencast):
        self.__can_delete_screencast = can_delete_screencast

    can_delete_screencast = property(
        fget=__get_can_delete_screencast,
        fset=__set_can_delete_screencast,
        doc='None.',
    )

    def __get_sync_data(self):
        return self.__sync_data

    def __set_sync_data(self, sync_data):
        self.__sync_data = sync_data

    sync_data = property(
        fget=__get_sync_data,
        fset=__set_sync_data,
        doc='None.',
    )

    def __get_receive_daily_report(self):
        return self.__receive_daily_report

    def __set_receive_daily_report(self, receive_daily_report):
        self.__receive_daily_report = receive_daily_report

    receive_daily_report = property(
        fget=__get_receive_daily_report,
        fset=__set_receive_daily_report,
        doc='None.',
    )

    def __get_blur_screen(self):
        return self.__blur_screen

    def __set_blur_screen(self, blur_screen):
        self.__blur_screen = blur_screen

    blur_screen = property(
        fget=__get_blur_screen,
        fset=__set_blur_screen,
        doc='None.',
    )

    def __get_can_edit_time(self):
        return self.__can_edit_time

    def __set_can_edit_time(self, can_edit_time):
        self.__can_edit_time = can_edit_time

    can_edit_time = property(
        fget=__get_can_edit_time,
        fset=__set_can_edit_time,
        doc='None.',
    )

    def __get_screenshot_interval(self):
        return self.__screenshot_interval

    def __set_screenshot_interval(self, screenshot_interval):
        self.__screenshot_interval = screenshot_interval

    screenshot_interval = property(
        fget=__get_screenshot_interval,
        fset=__set_screenshot_interval,
        doc='None.',
    )

    def __get_profile_image(self):
        return self.__profile_image

    def __set_profile_image(self, profile_image):
        self.__profile_image = profile_image

    profile_image = property(
        fget=__get_profile_image,
        fset=__set_profile_image,
        doc='None.',
    )

    def __get_refresh_token(self):
        return self.__refresh_token

    def __set_refresh_token(self, refresh_token):
        self.__refresh_token = refresh_token

    refresh_token = property(
        fget=__get_refresh_token,
        fset=__set_refresh_token,
        doc='None.',
    )

    def __get_code(self):
        return self.__code

    def __set_code(self, code):
        self.__code = code

    code = property(
        fget=__get_code,
        fset=__set_code,
        doc='None.',
    )

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

    def __get_id(self):
        return self.__id

    def __set_id(self, user_id):
        self.__id = user_id

    id = property(
        fget=__get_id,
        fset=__set_id,
        doc='None.',
    )

    def __get_username(self):
        return self.__username

    def __set_username(self, username):
        self.__username = username

    username = property(
        fget=__get_username,
        fset=__set_username,
        doc='Application name.',
    )


class Window(DataModel):
    def __init__(self, id: str, application_id: str, title: str, window_url: str, start_date: datetime, url: str,
                 domain_url: str = '', sync: int = 0, ) -> None:
        super().__init__()
        self.__id = id
        self.__application_id = application_id
        self.__title = title
        self.__window_url = window_url
        self.__start_date = start_date
        self.__url = url
        self.__domain_url = domain_url
        self.__sync = sync

    def __get_window_url(self):
        return self.__window_url

    def __set_window_url(self, window_url):
        self.__window_url = window_url

    window_url = property(
        fget=__get_window_url,
        fset=__set_window_url,
        doc='None.',
    )

    def __get_start_date(self):
        return self.__start_date

    def __set_start_date(self, start_date):
        self.__start_date = start_date

    start_date = property(
        fget=__get_start_date,
        fset=__set_start_date,
        doc='None.',
    )

    def __get_url(self):
        return self.__url

    def __set_url(self, url):
        self.__url = url

    url = property(
        fget=__get_url,
        fset=__set_url,
        doc='None.',
    )

    def __get_domain_url(self):
        return self.__domain_url

    def __set_domain_url(self, domain_url):
        self.__domain_url = domain_url

    domain_url = property(
        fget=__get_domain_url,
        fset=__set_domain_url,
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

    def __get_application_id(self):
        return self.__application_id

    def __set_application_id(self, application_id):
        self.__application_id = application_id

    application_id = property(
        fget=__get_application_id,
        fset=__set_application_id,
        doc='None.',
    )

    def __get_id(self):
        return self.__id

    def __set_id(self, id):
        self.__window_id = id

    id = property(
        fget=__get_id,
        fset=__set_id,
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

    def register(self, conn):
        sql = SQLs.INSERT_NEW_ROW_INTO_WINDOWS.format(
            id=self.id,
            application_id=self.application_id,
            title=self.title,
            window_url=self.window_url,
            start_date=str(self.start_date),
            url=self.url,
            domain_url=self.domain_url,
            sync=self.sync,
        )
        return db.execute(sql, conn=conn)


class Application(DataModel):
    def __init__(
            self, id: str, user: int, name: str, path: str, version: str, description: str, sync: int = 0,
    ) -> None:
        super(Application, self).__init__()
        self.__id = id
        self.__user = user
        self.__name = name
        self.__path = path
        self.__version = version
        self.__description = description
        self.__sync = sync

    def __get_id(self):
        return self.__id

    def __set_id(self, id):
        self.__id = id

    id = property(
        fget=__get_id,
        fset=__set_id,
        doc='None.',
    )

    def __get_path(self):
        return self.__path

    def __set_path(self, path):
        self.__path = path

    path = property(
        fget=__get_path,
        fset=__set_path,
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

    def __get_sync(self):
        return self.__sync

    def __set_sync(self, sync):
        self.__sync = sync

    sync = property(
        fget=__get_sync,
        fset=__set_sync,
        doc='None.',
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

    def __get_name(self):
        return self.__name

    def __set_name(self, name):
        self.__name = name

    name = property(
        fget=__get_name,
        fset=__set_name,
        doc='Application name.',
    )

    def register(self, conn):
        sql = SQLs.INSERT_NEW_ROW_INTO_APPLICATIONS.format(
            id=self.id,
            user=self.user,
            name=self.name,
            path=self.path,
            version=self.version,
            description=self.description,
            sync=self.sync,
        )
        return db.execute(sql, conn=conn)


class Settings(DataModel):

    @classmethod
    def load_settings(cls, conn):
        settings = [Settings(
            user_id=a.id,
            run_at_startup=a.run_at_startup,
            mini_timer=a.mini_timer,
            take_screenshots=a.take_screenshots,
            light_theme=a.light_theme,
            is_master_password_set=a.is_master_password_set,
            delete_old_logs=a.delete_old_logs,
            first_run=a.first_run,
            tracking_enabled=a.tracking_enabled,
            timezone=a.timezone,
            timer_interval=a.timer_interval,
            old_log_delete_days=a.old_log_delete_days,
            window_open=a.window_open,
            can_edit_time=a.can_edit_time,
            blur_screen=a.blur_screen,
            receive_daily_report=a.receive_daily_report,
            ip_address=a.ip_address,
            ip_address_backup=a.ip_address_backup,
            current_app_version=a.current_app_version,
            enable_idle=a.enable_idle,
            idle_timer=a.idle_timer,
            project_sel=a.project_sel,
            sup_project=a.sup_project,
            start_week=a.start_week,
            default_screenshot_save_path=a.default_screenshot_save_path,
        ) for a in conn.select(query=SQLs.SELECT_ALL_SETTINGS).itertuples()][-1]

        return settings

    def __init__(
            self, user_id: int, run_at_startup: bool, mini_timer: bool, take_screenshots: bool, light_theme: bool,
            is_master_password_set: bool, delete_old_logs: bool, first_run: bool, tracking_enabled: bool,
            timezone: bool, timer_interval: int, old_log_delete_days: int, window_open: bool, can_edit_time: bool,
            blur_screen: bool, receive_daily_report: bool, ip_address: bool, ip_address_backup: bool,
            current_app_version: bool, enable_idle: bool, idle_timer: int, project_sel: int, sup_project: int,
            start_week: str, default_screenshot_save_path: str,
    ) -> None:
        super(Settings, self).__init__()
        self.__user_id = user_id
        self.__run_at_startup = run_at_startup
        self.__mini_timer = mini_timer
        self.__take_screenshots = take_screenshots
        self.__is_master_password_set = is_master_password_set
        self.__delete_old_logs = delete_old_logs
        self.__light_theme = light_theme
        self.__first_run = first_run
        self.__tracking_enabled = tracking_enabled
        self.__timer_interval = timer_interval
        self.__old_log_delete_days = old_log_delete_days
        self.__window_open = window_open
        self.__can_edit_time = can_edit_time
        self.__blur_screen = blur_screen
        self.__timezone = timezone
        self.__receive_daily_report = receive_daily_report
        self.__ip_address = ip_address
        self.__ip_address_backup = ip_address_backup
        self.__current_app_version = current_app_version
        self.__enable_idle = enable_idle
        self.__idle_timer = idle_timer
        self.__project_sel = project_sel
        self.__sup_project = sup_project
        self.__start_week = start_week
        self.__default_screenshot_save_path = default_screenshot_save_path

    def __get_default_screenshot_save_path(self):
        return self.__default_screenshot_save_path

    def __set_default_screenshot_save_path(self, default_screenshot_save_path):
        self.__default_screenshot_save_path = default_screenshot_save_path

    default_screenshot_save_path = property(
        fget=__get_default_screenshot_save_path,
        fset=__set_default_screenshot_save_path,
        doc='None.',
    )

    def __get_start_week(self):
        return self.__start_week

    def __set_start_week(self, start_week):
        self.__start_week = start_week

    start_week = property(
        fget=__get_start_week,
        fset=__set_start_week,
        doc='None.',
    )

    def __get_sup_project(self):
        return self.__sup_project

    def __set_sup_project(self, sup_project):
        self.__sup_project = sup_project

    sup_project = property(
        fget=__get_sup_project,
        fset=__set_sup_project,
        doc='None.',
    )

    def __get_project_sel(self):
        return self.__project_sel

    def __set_project_sel(self, project_sel):
        self.__project_sel = project_sel

    project_sel = property(
        fget=__get_project_sel,
        fset=__set_project_sel,
        doc='None.',
    )

    def __get_idle_timer(self):
        return self.__idle_timer

    def __set_idle_timer(self, idle_timer):
        self.__idle_timer = idle_timer

    idle_timer = property(
        fget=__get_idle_timer,
        fset=__set_idle_timer,
        doc='None.',
    )

    def __get_enable_idle(self):
        return self.__enable_idle

    def __set_enable_idle(self, enable_idle):
        self.__enable_idle = enable_idle

    enable_idle = property(
        fget=__get_enable_idle,
        fset=__set_enable_idle,
        doc='None.',
    )

    def __get_current_app_version(self):
        return self.__current_app_version

    def __set_current_app_version(self, current_app_version):
        self.__current_app_version = current_app_version

    current_app_version = property(
        fget=__get_current_app_version,
        fset=__set_current_app_version,
        doc='None.',
    )

    def __get_ip_address_backup(self):
        return self.__ip_address_backup

    def __set_ip_address_backup(self, ip_address_backup):
        self.__ip_address_backup = ip_address_backup

    ip_address_backup = property(
        fget=__get_ip_address_backup,
        fset=__set_ip_address_backup,
        doc='None.',
    )

    def __get_ip_address(self):
        return self.__ip_address

    def __set_ip_address(self, ip_address):
        self.__ip_address = ip_address

    ip_address = property(
        fget=__get_ip_address,
        fset=__set_ip_address,
        doc='None.',
    )

    def __get_receive_daily_report(self):
        return self.__receive_daily_report

    def __set_receive_daily_report(self, receive_daily_report):
        self.__receive_daily_report = receive_daily_report

    receive_daily_report = property(
        fget=__get_receive_daily_report,
        fset=__set_receive_daily_report,
        doc='None.',
    )

    def __get_timezone(self):
        return self.__timezone

    def __set_timezone(self, timezone):
        self.__timezone = timezone

    timezone = property(
        fget=__get_timezone,
        fset=__set_timezone,
        doc='None.',
    )

    def __get_blur_screen(self):
        return self.__blur_screen

    def __set_blur_screen(self, blur_screen):
        self.__blur_screen = blur_screen

    blur_screen = property(
        fget=__get_blur_screen,
        fset=__set_blur_screen,
        doc='None.',
    )

    def __get_can_edit_time(self):
        return self.__can_edit_time

    def __set_can_edit_time(self, can_edit_time):
        self.__can_edit_time = can_edit_time

    can_edit_time = property(
        fget=__get_can_edit_time,
        fset=__set_can_edit_time,
        doc='None.',
    )

    def __get_window_open(self):
        return self.__window_open

    def __set_window_open(self, window_open):
        self.__window_open = window_open

    window_open = property(
        fget=__get_window_open,
        fset=__set_window_open,
        doc='None.',
    )

    def __get_old_log_delete_days(self):
        return self.__old_log_delete_days

    def __set_old_log_delete_days(self, old_log_delete_days):
        self.__old_log_delete_days = old_log_delete_days

    old_log_delete_days = property(
        fget=__get_old_log_delete_days,
        fset=__set_old_log_delete_days,
        doc='None.',
    )

    def __get_timer_interval(self):
        return self.__timer_interval

    def __set_timer_interval(self, timer_interval):
        self.__timer_interval = timer_interval

    timer_interval = property(
        fget=__get_timer_interval,
        fset=__set_timer_interval,
        doc='None.',
    )

    def __get_tracking_enabled(self):
        return self.__tracking_enabled

    def __set_tracking_enabled(self, tracking_enabled):
        self.__tracking_enabled = tracking_enabled

    tracking_enabled = property(
        fget=__get_tracking_enabled,
        fset=__set_tracking_enabled,
        doc='None.',
    )

    def __get_first_run(self):
        return self.__first_run

    def __set_first_run(self, first_run):
        self.__first_run = first_run

    first_run = property(
        fget=__get_first_run,
        fset=__set_first_run,
        doc='None.',
    )

    def __get_light_theme(self):
        return self.__light_theme

    def __set_light_theme(self, light_theme):
        self.__light_theme = light_theme

    light_theme = property(
        fget=__get_light_theme,
        fset=__set_light_theme,
        doc='None.',
    )

    def __get_delete_old_logs(self):
        return self.__delete_old_logs

    def __set_delete_old_logs(self, delete_old_logs):
        self.__delete_old_logs = delete_old_logs

    delete_old_logs = property(
        fget=__get_delete_old_logs,
        fset=__set_delete_old_logs,
        doc='None.',
    )

    def __get_is_master_password_set(self):
        return self.__is_master_password_set

    def __set_is_master_password_set(self, is_master_password_set):
        self.__is_master_password_set = is_master_password_set

    is_master_password_set = property(
        fget=__get_is_master_password_set,
        fset=__set_is_master_password_set,
        doc='None.',
    )

    def __get_take_screenshots(self):
        return self.__take_screenshots

    def __set_take_screenshots(self, take_screenshots):
        self.__take_screenshots = take_screenshots

    take_screenshots = property(
        fget=__get_take_screenshots,
        fset=__set_take_screenshots,
        doc='None.',
    )

    def __get_mini_timer(self):
        return self.__mini_timer

    def __set_mini_timer(self, mini_timer):
        self.__mini_timer = mini_timer

    mini_timer = property(
        fget=__get_mini_timer,
        fset=__set_mini_timer,
        doc='None.',
    )

    def __get_run_at_startup(self):
        return self.__run_at_startup

    def __set_run_at_startup(self, run_at_startup):
        self.__run_at_startup = run_at_startup

    run_at_startup = property(
        fget=__get_run_at_startup,
        fset=__set_run_at_startup,
        doc='None.',
    )

    def __get_user_id(self):
        return self.__user_id

    def __set_user_id(self, user_id):
        self.__app_id = user_id

    user_id = property(
        fget=__get_user_id,
        fset=__set_user_id,
        doc='None.',
    )


class Screenshot(DataModel):
    def register(self, conn):
        pass

    def __init__(
            self, id: str, user: int, date: datetime, screenshot: str, mouse_move: int, key_click: int,
            mouse_clicks: int, sync: int = 0,
    ) -> None:
        super(Screenshot, self).__init__()
        self.__date = date
        self.__mouse_clicks = mouse_clicks
        self.__id = id
        self.__mouse_move = mouse_move
        self.__sync = sync
        self.__key_click = key_click
        self.__screenshot = screenshot
        self.__user = user

    def __get_mouse_clicks(self):
        return self.__mouse_clicks

    def __set_mouse_clicks(self, mouse_clicks):
        self.__mouse_clicks = mouse_clicks

    mouse_clicks = property(
        fget=__get_mouse_clicks,
        fset=__set_mouse_clicks,
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

    def __get_user(self):
        return self.__user

    def __set_user(self, user):
        self.__user = user

    user = property(
        fget=__get_user,
        fset=__set_user,
        doc='None.',
    )

    def __get_screenshot(self):
        return self.__screenshot

    def __set_screenshot(self, screenshot):
        self.__screenshot = screenshot

    screenshot = property(
        fget=__get_screenshot,
        fset=__set_screenshot,
        doc='None.',
    )

    def __get_key_click(self):
        return self.__key_click

    def __set_key_click(self, key_click):
        self.__key_click = key_click

    key_click = property(
        fget=__get_key_click,
        fset=__set_key_click,
        doc='None.',
    )

    def __get_mouse_move(self):
        return self.__mouse_move

    def __set_mouse_move(self, mouse_move):
        self.__mouse_move = mouse_move

    mouse_move = property(
        fget=__get_mouse_move,
        fset=__set_mouse_move,
        doc='None.',
    )

    def __get_id(self):
        return self.__id

    def __set_id(self, id):
        self.__id = id

    id = property(
        fget=__get_id,
        fset=__set_id,
        doc='None.',
    )

    def __get_date(self):
        return self.__date

    def __set_date(self, date):
        self.__date = date

    date = property(
        fget=__get_date,
        fset=__set_date,
        doc='None.',
    )

    # def insert_to_db(self, , ):
    #     self.date = datetime.now()
    #     self.__id = str(user.id) + self.date.strftime('%d%m%Y%H%M%S%f')[:-3]
    #     self.__mouse_clicks = mouse_clicks
    #     self.__mouse_move = mouse_move
    #     self.__sync = 0
    #     self.__key_click = key_click
    #     self.__screenshot = screenshot
    #     self.__user = user.id


class Idle(DataModel):
    def __init__(
            self, id: str, application_id: str, task_id: int, duration: int = 0, end: datetime = None,
            start: datetime = datetime.now(), sync: int = 0,
    ) -> None:
        super(Idle, self).__init__()
        self.__id = id
        self.__application_id = application_id
        self.__task_id = task_id
        self.__duration = duration
        self.__sync = sync
        self.__start = start
        self.__end = end

    def __get_start(self):
        return self.__start

    def __set_start(self, start):
        self.__start = start

    start = property(
        fget=__get_start,
        fset=__set_start,
        doc='None.',
    )

    def __get_end(self):
        return self.__end

    def __set_end(self, end):
        self.__end = end

    def stopped(self):
        self.end = datetime.now()
        self.duration = (self.end - self.start).total_seconds()

    end = property(
        fget=__get_end,
        fset=__set_end,
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

    def __get_task_id(self):
        return self.__task_id

    def __set_task_id(self, task_id):
        self.__task_id = task_id

    task_id = property(
        fget=__get_task_id,
        fset=__set_task_id,
        doc='None.',
    )

    def __get_application_id(self):
        return self.__application_id

    def __set_application_id(self, application_id):
        self.__application_id = application_id

    application_id = property(
        fget=__get_application_id,
        fset=__set_application_id,
        doc='None.',
    )

    def __get_id(self):
        return self.__id

    def __set_id(self, id):
        self.__id = id

    id = property(
        fget=__get_id,
        fset=__set_id,
        doc='None.',
    )

    def register(self, conn):
        sql = SQLs.INSERT_NEW_ROW_INTO_IDLE.format(
            id=self.id,
            project_id=self.application_id,
            task_id=self.task_id,
            duration=self.duration,
            end=str(self.end),
            start=str(self.start),
            sync=self.sync,
        )
        return db.execute(sql, conn=conn)


if __name__ == "__main__":
    pass
