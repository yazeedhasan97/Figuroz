import os

from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.types import Interval
from sqlalchemy.sql import func
from datetime import datetime, timedelta
import joblib

from common import consts

from abc import ABC, abstractmethod


class Model(ABC):

    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr[attr.rfind('__') + 2:], value

    def __str__(self):
        return f"{type(self).__name__}(" + ', '.join(
            [f"{attr[attr.rfind('__') + 1:]}={value}" for attr, value in self.__dict__.items()]
        ) + ")"

    def __repr__(self):
        return self.__str__()


# The base class which our objects will be defined on.
Base = declarative_base()


class MetaModelBase(type(Base), type(Model)):
    pass


# Our Project object, mapped to the 'Projects' table
class Project(Base, Model, metaclass=MetaModelBase):
    __tablename__ = 'Projects'

    # Every SQLAlchemy table should have a primary key named 'id'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    company_id = Column(Integer, nullable=False)
    project_access = Column(Integer, nullable=False, default=1)
    status = Column(Integer, nullable=False, default=1)
    project_groups = Column(String, nullable=True, default=None)
    project_members = Column(String, nullable=True, default=None)

    user_id = Column(Integer, ForeignKey('Users.id'), nullable=False, primary_key=True)
    application_user = relationship("User", backref=backref('Projects'))


class Task(Base, Model, metaclass=MetaModelBase):
    __tablename__ = 'Tasks'

    # Every SQLAlchemy table should have a primary key named 'id'
    id = Column(Integer, primary_key=True)
    # Since we have a 1:n relationship, we need to store a foreign key to the users table.
    project_id = Column(Integer, ForeignKey('Projects.id'), nullable=False, primary_key=True)
    # Defines the 1:n relationship between tasks and projects.
    # Also creates a backreference which is accessible from a User object.
    task = relationship("Project", backref=backref('Tasks'))

    # rest of the columns
    name = Column(String, nullable=False)
    status = Column(Integer, nullable=False, default=1)

    user_id = Column(Integer, ForeignKey('Users.id'), nullable=False, primary_key=True)
    application_user = relationship("User", backref=backref('Tasks'))


class ProjectTimeLine(Base, Model, metaclass=MetaModelBase):
    __tablename__ = 'ProjectTimeLines'

    # Every SQLAlchemy table should have a primary key named 'id'
    id = Column(String, primary_key=True)
    # Since we have a 1:n relationship, we need to store a foreign key to the users table.
    project_id = Column(Integer, ForeignKey('Projects.id'), nullable=False)
    timeline_project = relationship("Project", backref=backref('ProjectTimeLines'))

    task_id = Column(Integer, ForeignKey('Tasks.id'), nullable=False)
    timeline_task = relationship("Task", backref=backref('ProjectTimeLines'))

    user_id = Column(Integer, ForeignKey('Users.id'), nullable=False)
    timeline_user = relationship("User", backref=backref('ProjectTimeLines'))

    # rest of the columns
    start = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, unique=True)
    end = Column(DateTime(timezone=True), onupdate=func.now(), nullable=False, unique=True)
    duration = Column(Interval, nullable=False)
    status = Column(Integer, nullable=False, default=0)
    day_format = Column(String, nullable=False)
    sync = Column(Integer, nullable=False, default=0)


class User(Base, Model, metaclass=MetaModelBase):
    __tablename__ = 'Users'
    id = Column(Integer, primary_key=True)
    token = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    username = Column(String, nullable=False)

    company_id = Column(Integer, nullable=False)
    code = Column(String, nullable=False)
    status = Column(Integer, nullable=False, default=2)
    access_level = Column(Integer, nullable=False, default=2)
    profile_image = Column(String(200), )
    screenshot_interval = Column(Integer, nullable=False, default=5)
    can_edit_time = Column(Boolean, nullable=False, default=False)
    blur_screen = Column(Boolean, nullable=False, default=True)
    receive_daily_report = Column(Boolean, nullable=False, default=True)
    sync_data = Column(Integer, nullable=False, default=2)
    can_delete_screencast = Column(Boolean, nullable=False, default=False)
    owner_user = Column(Integer, nullable=False, default=2)
    inactive_interval = Column(Integer, nullable=False, default=3)

    group_members = Column(String, nullable=True, default=None)
    group_managers = Column(String, nullable=True, default=None)
    timezone = Column(String, nullable=True, default=None)
    ip_address = Column(String, nullable=True, default=None)
    current_app_version = Column(String, nullable=True, default=None)
    user_location = Column(String, nullable=True, default=None)
    internet_speed = Column(String, nullable=True, default=None)


class Window(Base, Model, metaclass=MetaModelBase):
    __tablename__ = 'Windows'

    # Every SQLAlchemy table should have a primary key named 'id'
    id = Column(String, primary_key=True)
    # Since we have a 1:n relationship, we need to store a foreign key to the users table.
    application_id = Column(String, ForeignKey('Applications.id'), nullable=False)
    window_application = relationship("Application", backref=backref('Windows'))

    title = Column(String, nullable=False)
    window_url = Column(String, nullable=False)
    start = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, unique=True)

    url = Column(String, nullable=True)
    domain_url = Column(String, nullable=True)
    sync = Column(Integer, nullable=False, default=0)


def create_and_insert_window(session, data):
    from common import consts
    current = datetime.now()
    try:
        window = Window(
            id=str(data['user_id']) + current.strftime(consts.ID_TIME_FORMATS),
            application_id=data['application_id'],
            title=data['title'],
            window_url=data['window_url'],
            start=current,
            sync=0,
            url=data['url'],
            domain_url=data['domain_url'],
        )
        session.add(window)

        session.commit()
        return window
    except Exception as e:
        print('Failed insert screenshot to the database. Some constraints are violated...')
        print(e)


class Application(Base, Model, metaclass=MetaModelBase):
    __tablename__ = 'Applications'

    # Every SQLAlchemy table should have a primary key named 'id'
    id = Column(String, primary_key=True)
    hash = Column(String, primary_key=True)  # user_id + name + path
    name = Column(String, nullable=False)  # different user open same application
    path = Column(String, nullable=False)  # different user open same application

    # rest of the columns
    version = Column(String, nullable=True)

    # Since we have a 1:n relationship, we need to store a foreign key to the users table.
    user_id = Column(Integer, ForeignKey('Users.id'), nullable=False)
    application_user = relationship("User", backref=backref('Applications'))

    description = Column(String, nullable=True)

    sync = Column(Integer, nullable=False, default=0)


def create_and_insert_application(session, data):
    from common import consts

    hashed = joblib.hash(str(data['user_id']) + data['name'] + data['path'])
    try:
        app = Application(
            id=str(data['user_id']) + datetime.now().strftime(consts.ID_TIME_FORMATS),
            user_id=data['user_id'],
            name=data['name'],
            path=data['path'],
            hash=hashed,
            sync=0,
            version=data['version'],
            description=data['description'],
        )
        session.add(app)

        session.commit()
        return app
    except Exception as e:
        print('Failed insert screenshot to the database. Some constraints are violated...')
        print(e)
        raise e


class Screenshot(Base, Model, metaclass=MetaModelBase):
    __tablename__ = 'Screenshots'

    # Every SQLAlchemy table should have a primary key named 'id'
    id = Column(String, primary_key=True)

    # Since we have a 1:n relationship, we need to store a foreign key to the users table.
    user_id = Column(Integer, ForeignKey('Users.id'), nullable=False)
    screenshot_user = relationship("User", backref=backref('Screenshots'))

    date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, unique=True)
    screenshot = Column(String, nullable=False, )

    # rest of the columns
    mouse_clicks = Column(Integer, nullable=False, default=0)
    mouse_move = Column(Integer, nullable=False, default=0)
    key_click = Column(Integer, nullable=False, default=0)
    sync = Column(Integer, nullable=False, default=0)


def create_and_insert_screenshot(session, data):
    from common import consts
    current = datetime.now()
    try:
        from scripts.controllers import MainController
        screen = Screenshot(
            id=str(data['user_id']) + current.strftime(consts.ID_TIME_FORMATS),
            user_id=data['user_id'],
            date=current,
            screenshot=data['img'],
            sync=0,
            mouse_move=data['mouse_move'],
            key_click=data['key_click'],
            mouse_clicks=data['mouse_clicks'],
        )
        session.add(screen)

        session.commit()
    except Exception as e:
        print('Failed insert screenshot to the database. Some constraints are violated...')
        print(e)


class UserAccountSetting(Base, Model, metaclass=MetaModelBase):
    # TODO: everytime the internet disconnect
    __tablename__ = 'UserAccountSettings'
    id = Column(String, primary_key=True)

    # Since we have a 1:n relationship, we need to store a foreign key to the users table.
    user_id = Column(Integer, ForeignKey('Users.id'), nullable=False)
    application_user = relationship("User", backref=backref('UserAccountSettings'))

    type = Column(Integer, nullable=False, )
    value = Column(String, nullable=False, )

    date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, unique=True)
    sync = Column(Integer, nullable=False, default=0)


def create_and_insert_user_account_settings(data, session):
    current = datetime.now()
    upload = 'Upload: {:.2f} Mb/s'.format(data['internet'][0] / 1024 / 1024)
    download = 'Download: {:.2f} Mb/s'.format(data['internet'][-1] / 1024 / 1024)
    user_account_settings_types = {
        1: data['ip_address'],
        2: data['geo_location'],
        3: str([upload, download]),
    }
    settings = []
    try:
        for key, value in user_account_settings_types.items():
            setting = UserAccountSetting(
                id=str(data['user_id']) + datetime.now().strftime(consts.ID_TIME_FORMATS),
                user_id=data['user_id'],
                date=current,
                type=key,
                value=value,
                sync=0,
            )
            session.add(setting)
            settings.append(setting)
        session.commit()
    except Exception as e:
        print('Failed insert screenshot to the database. Some constraints are violated...')
        print(e)
        # raise e

    return settings.copy()


class UserLog(Base, Model, metaclass=MetaModelBase):
    # TODO: everytime new window open
    #  This track the time of the window, the window table track the open itself
    __tablename__ = 'Logs'
    id = Column(String, primary_key=True)

    # Since we have a 1:n relationship, we need to store a foreign key to the users table.
    user_id = Column(Integer, ForeignKey('Users.id'), nullable=False)
    log_user = relationship("User", backref=backref('Logs'))

    # Since we have a 1:n relationship, we need to store a foreign key to the users table.
    window_id = Column(String, ForeignKey('Windows.id'), nullable=False)
    log_window = relationship("Window", backref=backref('Logs'))

    # Since we have a 1:n relationship, we need to store a foreign key to the users table.
    project_timeline_id = Column(String, ForeignKey('ProjectTimeLines.id'), nullable=False)
    log_project_timeline = relationship("ProjectTimeLine", backref=backref('Logs'))

    start = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, unique=True)
    end = Column(DateTime(timezone=True), onupdate=func.now(), nullable=False, unique=True)
    duration = Column(Integer, nullable=False, default=0)
    sync = Column(Integer, nullable=False, default=0)


def create_and_insert_user_log(data, session):
    current = datetime.now()
    try:
        idle = UserLog(
            id=str(data['user_id']) + datetime.now().strftime(consts.ID_TIME_FORMATS),
            user_id=data['user_id'],
            window_id=data['window_id'],
            project_timeline_id=data['project_timeline_id'],
            duration=0,
            start=current,
            end=current,
            sync=0,
        )
        session.add(idle)
        session.commit()
        return idle
    except Exception as e:
        print('Failed insert screenshot to the database. Some constraints are violated...')
        print(e)
        raise e


class Idle(Base, Model, metaclass=MetaModelBase):
    __tablename__ = 'Idles'

    # Every SQLAlchemy table should have a primary key named 'id'
    id = Column(String, primary_key=True)

    # Since we have a 1:n relationship, we need to store a foreign key to the users table.
    user_id = Column(Integer, ForeignKey('Users.id'), nullable=False)
    application_user = relationship("User", backref=backref('Idles'))

    # Since we have a 1:n relationship, we need to store a foreign key to the users table.
    application_id = Column(Integer, ForeignKey('Applications.id'), nullable=False)
    idle_application = relationship("Application", backref=backref('Idles'))

    # Since we have a 1:n relationship, we need to store a foreign key to the users table.
    task_id = Column(Integer, ForeignKey('Tasks.id'), nullable=False)
    idle_task = relationship("Task", backref=backref('Idles'))

    duration = Column(Integer, nullable=False, default=0)
    sync = Column(Integer, nullable=False, default=0)

    start = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, unique=True)
    end = Column(DateTime(timezone=True), onupdate=func.now(), nullable=False, unique=True)


class Test(Base, Model, metaclass=MetaModelBase):
    __tablename__ = 'Tests'
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, )
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False, )


def crete_user_from_api(session, data, password):
    user = User(
        token=data['token'], id=data['user']['id'], company_id=data['user']['companyId'], password=password,
        username=data['user']['username'], email=data['user']['emailAddress'], status=data['user']['status'],
        access_level=data['user']['accessLevel'], code=data['user']['code'], timezone=data['user']['timeZone'],
        screenshot_interval=data['user']['screenshotInterval'], receive_daily_report=data['user']['receiveDailyReport'],
        can_edit_time=data['user']['canEditTime'], blur_screen=data['user']['canEditTime'],
        ip_address=data['user']['ipAddress'], current_app_version=data['user']['currentAppVersion'],
        inactive_interval=data['user']['inactiveTime'], group_members=data['user']['groupMembers'],
        group_managers=data['user']['groupManagers'], can_delete_screencast=data['user']['canDeleteSceencast'],
        owner_user=data['user']['ownerUser'], user_location=data['user']['userLocation'],
        internet_speed=data['user']['internetSpeed'], sync_data=data['user']['syncData'],
        profile_image=data['user']['profileImage'],
    )
    try:
        session.add(user)
        session.commit()
    except Exception as e:
        print('Failed insert user to the database. Some constraints are violated...')
        print(e)

    return user


def create_projects_from_api(session, data, user_id):
    projects = []
    print(data)
    try:
        for raw in data:
            project = Project(
                id=raw['id'],
                name=raw['projectName'],
                company_id=raw['companyId'],
                project_access=raw['projectAccess'],
                status=raw['status'],
                project_groups=str(raw['projectGroups']),
                project_members=str(raw['projectMembers']),
                user_id=user_id,
            )
            session.add(project)
            projects.append(project)

        session.commit()
    except Exception as e:
        print('Failed insert user to the database. Some constraints are violated...')
        print(e)

    return projects.copy()


def create_tasks_from_api(session, data, user_id):
    tasks = []
    try:
        for raw in data:
            task = Task(
                id=raw['id'],
                project_id=raw['projectId'],
                name=raw['taskName'],
                status=raw['status'],
                user_id=user_id,
            )
            session.add(task)
            tasks.append(task)

        session.commit()
    except Exception as e:
        print('Failed insert user to the database. Some constraints are violated...')
        print(e)

    return tasks.copy()


def create_and_insert_project_time_line(user_id, project_id, task_id, session):
    current = datetime.now()
    try:
        timeline = ProjectTimeLine(
            id=str(user_id) + current.strftime(consts.ID_TIME_FORMATS),
            start=current,
            day_format=current.strftime(consts.DAY_TIME_FORMAT),
            project_id=project_id,
            task_id=task_id,
            duration=timedelta(seconds=0),
            user_id=user_id,
            sync=0,
            status=0,
            end=current,
        )
        session.add(timeline)
        session.commit()
        return timeline
    except Exception as e:
        print('Failed insert user to the database. Some constraints are violated...')
        print(e)


# Not in use
def update_project_time_line_duration(session, id, user_id, task_id, project_id, duration: timedelta):
    try:
        session.query(ProjectTimeLine).filter(
            ProjectTimeLine.user_id == user_id and
            ProjectTimeLine.id == id and
            ProjectTimeLine.task_id == task_id and
            ProjectTimeLine.project_id == project_id
        ).update({
            'duration': duration
        })

        session.commit()

    except Exception as e:
        print('Failed insert user to the database. Some constraints are violated...')
        print(e)


def create_and_insert_idle(data, session):
    current = datetime.now()
    try:
        idle = Idle(
            id=str(data['user_id']) + datetime.now().strftime(consts.ID_TIME_FORMATS),
            user_id=data['user_id'],
            application_id=data['application_id'],
            task_id=data['task_id'],
            duration=0,
            start=current,
            end=current,
            sync=0,
        )
        session.add(idle)
        session.commit()
        return idle
    except Exception as e:
        print('Failed insert screenshot to the database. Some constraints are violated...')
        print(e)
        raise e


def create_database_session(db_path, echo=True):
    # For this example we will use an in-memory sqlite DB.
    # Let's also configure it to echo everything it does to the screen.
    db_path = 'sqlite:///' + db_path + '?check_same_thread=False'
    engine = create_engine(db_path, echo=echo, )

    # Create all tables by issuing CREATE TABLE commands to the DB.
    if not os.path.exists(db_path):
        Base.metadata.create_all(engine)

    # Creates a new session to the database by using the engine we described.
    return sessionmaker(bind=engine)()

    # user_by_email = session.query(Task).all()
    # print(
    #     user_by_email
    # )
    # # Let's create a user and add two e-mail addresses to that user.
    # from datetime import datetime
    # task = Test(id=datetime.now().strftime('%Y%S'), name='yazeed', email='yazeed.97@hotmail.com', password='1234')

    # # Let's add the user and its addresses we've created to the DB and commit.
    # session.add(ed_user)
    # session.commit()
    #
    # # Now let's query the user that has the e-mail address ed@google.com
    # # SQLAlchemy will construct a JOIN query automatically.
    # user_by_email = session.query(User) \
    #     .filter(Address.email_address == 'ed@google.com') \
    #     .first()
    #
    # # This will cause an additional query by lazy loading from the DB.
    #
    # # To avoid querying again when getting all addresses of a user,
    # # we use the joinedload option. SQLAlchemy will load all results and hide
    # # the duplicate entries from us, so we can then get for
    # # the user's addressess without an additional query to the DB.
    # user_by_email = session.query(User) \
    #     .filter(Address.email_address == 'ed@google.com') \
    #     .options(joinedload(User.addresses)) \
    #     .first()


if __name__ == "__main__":
    # main()
    pass
