from __future__ import annotations
import time
from abc import ABC, abstractmethod
from datetime import datetime

from scripts import models

from threading import Timer, Lock

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from scripts.models import ProjectTimeLine


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


class AbstractObserved(ABC):
    """ The Subject interface declares a set of methods for managing subscribers. """
    _state = None
    _observers = {}

    @abstractmethod
    def attach(self, id) -> None:
        pass

    def detach(self, id) -> None:
        """ Detach an observer from the subject."""
        print(f'Task{id} Detach From Observer.')
        try:
            self._observers.pop(id, None)
        except ValueError:
            print(f'Task{id} Not found in observers.')
        pass

    @abstractmethod
    def notify(self, ids, state='create') -> None:
        """ Notify all observers about an event."""
        pass


class TimerObserver(AbstractObserver):
    _tracker = None
    _start = None

    def create(self, ids: dict) -> None:
        print('Create The Time Line')
        self._tracker = ProjectTimeLine(
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


class ObservedTimer(AbstractObserved):
    """ The Subject interface declares a set of methods for managing subscribers. """
    _state = None
    _observers = {}

    def attach(self, id) -> None:
        """ Attach an observer to the subject. """
        print(f'Task{id} Attached To Observer.')
        self._observers[id] = TimerObserver()
        pass

    def notify(self, ids: dict, state='create') -> None:
        """ Notify all observers about an event."""
        if state == 'create':
            self._observers[ids['sub_id']].create(ids)
        elif state == 'update':
            self._observers[ids['sub_id']].update()
        else:
            pass
        pass


# TODO: Activate ScreenShot Observer
# TODO: Activate ScreenShot Periodic
class ScreenShotDirectoryWatcher:
    def __init__(self, directory):
        self.observer = Observer()
        self.__directory = directory

    def __get_directory(self):
        return self.__directory

    def __set_directory(self, directory):
        self.__directory = directory

    def __del_directory(self, ):
        self.__directory = None

    directory = property(
        fset=__set_directory,
        fget=__get_directory,
        fdel=__del_directory,
    )

    def run(self, recursive=True):
        event_handler = ScreenShotDirectoryHandler()
        self.observer.schedule(event_handler, self.__directory, recursive=recursive)
        self.observer.start()
        try:
            while True:  # TODO: this is not needed in stoppable apps behaviour
                time.sleep(3)
        except Exception as e:
            self.observer.stop()
            print(e)
            # raise e

        self.observer.join()
        return self


class ScreenShotDirectoryHandler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event, **kwargs):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            path = event.src_path
            print(f"Received created event - {path}.")
            time.sleep(1)
            try:
                pass
            except Exception as e:
                print(e)
                raise e

        elif event.event_type == 'modified':
            # Taken any action here when a file is modified.
            path = event.src_path
            print(f"Received modified event - {path}.")
            time.sleep(1)
            try:
                pass
            except Exception as e:
                print(e)
                raise e


# TODO: Activate Apps Observer
# TODO: Activate Apps Periodic
class ApplicationObserver(AbstractObserver):
    _tracker = None
    _start = None

    def update(self, ) -> None:
        pass


class ObservedApplication(AbstractObserved):
    """ The Subject interface declares a set of methods for managing subscribers. """
    _state = None
    _observers = {}

    def attach(self, id) -> None:
        """ Attach an observer to the subject. """
        pass

    def notify(self, ids: dict, state='create') -> None:
        """ Notify all observers about an event."""
        pass


# TODO: Activate URLs Observer
# TODO: Activate URLs Periodic
class URLObserver(AbstractObserver):
    _tracker = None
    _start = None

    def update(self, ) -> None:
        pass


class ObservedURL(AbstractObserved):
    """ The Subject interface declares a set of methods for managing subscribers. """
    _state = None
    _observers = {}

    def attach(self, id) -> None:
        """ Attach an observer to the subject. """
        pass

    def notify(self, ids: dict, state='create') -> None:
        """ Notify all observers about an event."""
        pass


# TODO: Activate Ideal Time Observer
# TODO: Activate Ideal Time Periodic
class IdealTimeObserver(AbstractObserver):
    _tracker = None
    _start = None

    def update(self, ) -> None:
        pass


class ObservedIdealTime(AbstractObserved):
    """ The Subject interface declares a set of methods for managing subscribers. """
    _state = None
    _observers = {}

    def attach(self, id) -> None:
        """ Attach an observer to the subject. """
        pass

    def notify(self, ids: dict, state='create') -> None:
        """ Notify all observers about an event."""
        pass
