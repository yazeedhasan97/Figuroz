from __future__ import annotations

import platform
import threading
from abc import ABC, abstractmethod
from datetime import datetime


# from database import db
from common import consts


from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener

import sys
import time


class MainController:
    API_CONNECTION = None
    CURRENT_ACTIVE_USER_ID = None
    DB_CONNECTION = None

    SETTINGS = None
    CURRENT_COMPUTER_SCREEN = None
    KEYBOARD_KEYS_COUNT = 0
    MOUSE_KEYS_COUNT = 0
    MOUSE_MOVE_COUNT = 0
    SYSTEM = None
    CURRENT_ACTIVE_PROJECT_ID = None
    CURRENT_ACTIVE_TASK_ID = None
    CURRENT_ACTIVE_APPLICATION_ID = None
    CURRENT_ACTIVE_URL_ID = None

    @classmethod
    def store_api_connection(cls, connection):
        if MainController.API_CONNECTION is None:
            MainController.API_CONNECTION = connection

    @classmethod
    def store_database_connection(cls, connection):
        if MainController.DB_CONNECTION is None:
            MainController.DB_CONNECTION = connection

    @classmethod
    def store_current_active_project_id(cls, id):
        MainController.CURRENT_ACTIVE_PROJECT_ID = id

    @classmethod
    def store_current_active_task_id(cls, id):
        MainController.CURRENT_ACTIVE_TASK_ID = id

    @classmethod
    def store_current_active_application_id(cls, id):
        MainController.CURRENT_ACTIVE_APPLICATION_ID = id

    @classmethod
    def store_current_active_url_id(cls, id):
        MainController.CURRENT_ACTIVE_URL_ID = id

    @classmethod
    def store_system_type(cls, ):
        MainController.SYSTEM = platform.system()

    @classmethod
    def store_settings(cls, settings):
        MainController.SETTINGS = settings

    # @classmethod
    # def initiate_database_connection(cls, ):
    #     if MainController.DB_CONNECTION is None:
    #         MainController.DB_CONNECTION = db.create_db_connection()

    @classmethod
    def close_database_connection(cls, ):
        if MainController.DB_CONNECTION is not None:
            MainController.DB_CONNECTION.close()

    @classmethod
    def store_screen_details(cls, screen):
        MainController.CURRENT_COMPUTER_SCREEN = screen

    @classmethod
    def increase_keyboard_keys_count(cls, ):
        MainController.KEYBOARD_KEYS_COUNT += 1

    @classmethod
    def reset_keyboard_keys_count(cls, ):
        MainController.KEYBOARD_KEYS_COUNT = 0

    @classmethod
    def increase_mouse_keys_count(cls, ):
        MainController.MOUSE_KEYS_COUNT += 1

    @classmethod
    def reset_mouse_keys_count(cls, ):
        MainController.MOUSE_KEYS_COUNT = 0

    @classmethod
    def increase_mouse_moves_count(cls, ):
        MainController.MOUSE_MOVE_COUNT += 1

    @classmethod
    def reset_mouse_moves_count(cls, ):
        MainController.MOUSE_MOVE_COUNT = 0


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
        from database.models import create_project_time_line
        self._tracker = create_project_time_line(
            project_id=ids['project_id'],
            task_id=ids['task_id'],
            user_id=ids['user_id'],
        )
        self._start = datetime.now()  # We need to Fix this
        pass

    def update(self, ) -> None:
        print(f'Update The Time Line {str(datetime.now() - self._start)}')
        self._tracker.duration = datetime.now() - self._start
        print('Updated the Self Duration')
        try:
            MainController.DB_CONNECTION.add(self._tracker)
            MainController.DB_CONNECTION.commit()
            # self._tracker.register(MainController.DB_CONNECTION)
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
        observer_id = ''.join([str(ids['user_id']), str(ids['project_id']), str(ids['task_id'])])
        if state == 'create':
            self._observers[observer_id].create(ids)
        elif state == 'update':
            self._observers[observer_id].update()
        else:
            pass
        pass


class InputsObserver:
    __moves_divider = 0

    def __init__(self, auto_start=False):
        if sys.platform in ['Mac', 'darwin', 'os2', 'os2emx']:
            import HIServices
            if not HIServices.AXIsProcessTrusted():
                print('Recording user inputs are not trusted, please modify your computer settings')

        self.mouse_listener = MouseListener(
            on_move=self.on_mouse_move,
            on_click=self.on_mouse_click,
            on_scroll=self.on_mouse_scroll,
        )
        self.keyboard_listener = KeyboardListener(
            on_press=self.on_keyboard_press,
            on_release=self.on_keyboard_release,
        )
        if auto_start:
            self.start()

    def stop(self):
        # self.mouse_listener.join()
        self.mouse_listener.stop()
        # self.keyboard_listener.join()
        self.keyboard_listener.stop()

    def start(self):
        self.mouse_listener.start()
        self.keyboard_listener.start()

    def on_mouse_move(self, x, y):
        self.__moves_divider += 1
        if self.__moves_divider % consts.MOUSE_MOVE_DIVIDER == 0:
            MainController.increase_mouse_moves_count()
            self.__moves_divider = 0

    def on_mouse_click(self, x, y, button, pressed):
        if pressed:
            MainController.increase_mouse_keys_count()
            print('on_mouse_click')

    def on_mouse_scroll(self, x, y, dx, dy):
        MainController.increase_mouse_moves_count()
        # print('Scrolled {0} at {1}'.format(
        #     'down' if dy < 0 else 'up',
        #     (x, y)))

    def on_keyboard_press(self, key):
        pass

    def on_keyboard_release(self, key):
        MainController.increase_keyboard_keys_count()
        pass


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()
        self.join()

    def stopped(self):
        return self._stop_event.is_set()


if __name__ == "__main__":
    x = InputsObserver(auto_start=True)
    while True:
        time.sleep(1)
