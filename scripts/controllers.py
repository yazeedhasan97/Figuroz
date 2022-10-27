from __future__ import annotations
import time
from abc import ABC, abstractmethod
from datetime import datetime

from scripts import db_models

from threading import Timer, Lock


# from watchdog.observers import Observer

class Periodic:
    """
    A periodic task running in threading.Timers
    """

    def __init__(self, interval, function, *args, **kwargs):
        self._lock = Lock()
        self._timer = None
        self.function = function
        self.interval = interval
        self.args = args
        self.kwargs = kwargs
        self._stopped = True
        if kwargs.pop('autostart', True):
            self.start()

    def start(self, from_run=False):
        self._lock.acquire()
        if from_run or self._stopped:
            self._stopped = False
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
        self._lock.release()

    def _run(self):
        self.start(from_run=True)
        self.function(*self.args, **self.kwargs)

    def stop(self):
        self._lock.acquire()
        self._stopped = True
        self._timer.cancel()
        self._lock.release()


class AbstractObserver(ABC):
    """ The Observer interface declares the update method, used by subjects. """

    @abstractmethod
    def update(self, ) -> None:
        """ Receive update from subject. """
        pass


class TimerObserver(AbstractObserver):
    _tracker = None
    _start = None

    def create(self, ids: dict) -> None:
        print('Create The Time Line')
        self._tracker = db_models.ProjectTimeLine(
            project_id=ids['project_id'],
            sub_id=ids['sub_id'],
            user=ids['user'],
            date_ended=datetime.now(),
            time_start=datetime.now().time(),
        )
        self._start = datetime.now()  # We need to Fix this
        pass

    def update(self, ) -> None:
        print(f'Update The Time Line {str(datetime.now() - self._start)}')
        self._tracker.duration = datetime.now() - self._start
        print('Updated the Self Duration')
        try:
            self._tracker.insert_to_db(MainController.DB_CONNECTION)
        except Exception as e:
            print(e)
            raise e

        pass


class Observed(ABC):
    """ The Subject interface declares a set of methods for managing subscribers. """
    _state = None
    _observers = {}

    def attach(self, sub_id) -> None:
        """ Attach an observer to the subject. """
        print(f'Task{sub_id} Attached To Observer.')
        self._observers[sub_id] = TimerObserver()

        pass

    def detach(self, sub_id) -> None:
        """ Detach an observer from the subject."""
        print(f'Task{sub_id} Detach From Observer.')
        try:
            self._observers.pop(sub_id, None)
        except ValueError:
            print(f'Task{sub_id} Not found in observers.')
        pass

    @abstractmethod
    def notify(self, timeline, state='create') -> None:
        """ Notify all observers about an event."""
        pass



# TODO: Activate Apps Observer
# TODO: Activate URLs Observer
# TODO: Activate IdelTime Observer
# TODO: Activate ScreenShot Observer

# TODO: Activate ScreenShot Periodic
# TODO: Activate Apps Periodic
# TODO: Activate Idel Time Periodic
# TODO: Activate URLs Periodic
# TODO: `Activate ProjectTimeLine Periodic


class MainController:
    Settings = None
    DB_CONNECTION = None

    @classmethod
    def initiate_settings(cls, settings):
        MainController.Settings = settings

    @classmethod
    def initiate_database_connection(cls, conn):
        MainController.DB_CONNECTION = conn

    @classmethod
    def close_database_connection(cls, ):
        MainController.DB_CONNECTION.close()
