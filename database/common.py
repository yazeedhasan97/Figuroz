from abc import ABC, abstractmethod


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


class DBModel(Model):
    pass


class DataModel(Model):
    @abstractmethod
    def register(self, conn):
        pass

