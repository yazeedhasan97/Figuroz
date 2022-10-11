from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

import db_models


class Observer(ABC):
    """ The Observer interface declares the update method, used by subjects. """

    @abstractmethod
    def update(self, ) -> None:
        """ Receive update from subject. """
        pass


class TimerObserver(Observer):
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
        # if (datetime.now() - self._start) # TODO: do we actually needs this
        print(f'Update The Time Line {str(datetime.now() - self._start)}')
        # TODO: Insert Into DataBase the _tracker
        self._tracker.duration = datetime.now() - self._start
        print('Updated the Self Duration')
        self._tracker.insert_to_db()

        pass


class Observed(ABC):
    """ The Subject interface declares a set of methods for managing subscribers. """
    _state = None
    _flag_observers = {}

    def attach(self, sub_id) -> None:
        """ Attach an observer to the subject. """
        print(f'Task{sub_id} Attached To Observer.')
        self._flag_observers[sub_id] = TimerObserver()

        pass

    def detach(self, sub_id) -> None:
        """ Detach an observer from the subject."""
        print(f'Task{sub_id} Detach From Observer.')
        try:
            self._flag_observers.pop(sub_id, None)
        except ValueError:
            print(f'Task{sub_id} Not found in observers.')
        pass

    @abstractmethod
    def notify(self, timeline, state='create') -> None:
        """ Notify all observers about an event."""
        pass

# class CustomTimerFlagNotifier(ObserverSubject):
#     def notify(self, time_line:) -> None:
#         self._observers[task.sub_id].update(task)
#         pass


# class ConcreteSubject(Subject):
#     """
#     The Subject owns some important state and notifies observers when the state
#     changes.
#     """
#
#     _state = None
#     """
#     For the sake of simplicity, the Subject's state, essential to all
#     subscribers, is stored in this variable.
#     """
#
#     _observers = []
#     """
#     List of subscribers. In real life, the list of subscribers can be stored
#     more comprehensively (categorized by event type, etc.).
#     """
#
#     def attach(self, observer: Observer) -> None:
#         print("Subject: Attached an observer.")
#         self._observers.append(observer)
#
#     def detach(self, observer: Observer) -> None:
#         self._observers.remove(observer)
#
#     """
#     The subscription management methods.
#     """
#
#     def notify(self) -> None:
#         """
#         Trigger an update in each subscriber.
#         """
#
#         print("Subject: Notifying observers...")
#         for observer in self._observers:
#             observer.update(self)

# https://refactoring.guru/design-patterns/observer/python/example
