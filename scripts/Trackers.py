from abc import ABC, abstractmethod


class Observer(ABC):
    @abstractmethod
    def update(self, lst) -> None:
        pass


class TrackedSetObserver(Observer):
    def update(self, lst) -> None:
        print(lst)
        pass


class TrackedListObserver(Observer):
    def update(self, lst) -> None:
        print(lst)
        pass


class Tracked(ABC):
    """
    The Subject interface declares a set of methods for managing subscribers.
    """

    @abstractmethod
    def attach(self, observer: Observer) -> None:
        pass

    @abstractmethod
    def detach(self, observer: Observer) -> None:
        pass

    @abstractmethod
    def notify(self) -> None:
        pass


class TrackedSet(Tracked, set):
    _state: int = None
    _observers: list[Observer] = []

    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)


    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def notify(self) -> None:
        for observer in self._observers:
            observer.update(self)

    def add(self, item) -> None:
        super(TrackedSet, self).add(item)
        self.notify()

    def remove(self, item) -> None:
        super(TrackedSet, self).remove(item)
        self.notify()


class TrackedList(Tracked, list):
    _state: int = None
    _observers: list[Observer] = []

    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def notify(self) -> None:
        for observer in self._observers:
            observer.update(self)

    def append(self, item) -> None:
        super(TrackedList, self).append(item)
        self.notify()

    def remove(self, item) -> None:
        super(TrackedList, self).remove(item)
        self.notify()

    def insert(self, item, **kwargs) -> None:
        super(TrackedList, self).insert(item, **kwargs)
        self.notify()


if __name__ == "__main__":
    # tracked_set = TrackedSet()
    # x = TrackedSetObserver()
    tracked_set = TrackedList()
    x = TrackedListObserver()
    tracked_set.attach(x)
    tracked_set.append(5)

    pass
