import logging

from datetime import timedelta, datetime
from typing import Union, Dict, Any, Optional

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QWidget, QHBoxLayout, QStyledItemDelegate, QStyleOptionViewItem

from common import consts, utils
from scripts.new_controllers import ObservedTimer

logger = logging.getLogger(__name__)

Id = Optional[Union[int, str]]
Number = Union[int, float]
Duration = Union[timedelta, Number]
ConvertibleTimestamp = Union[datetime, str]
Data = Dict[str, Any]


class QClickableLabel(QLabel):
    def __init__(self, msg, when_clicked, parent=None):
        QLabel.__init__(
            self,
            msg,
            parent=parent
        )
        self._when_clicked = when_clicked

    def mouseReleaseEvent(self, event):
        self._when_clicked(event)


class ItemDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        option.decorationPosition = QStyleOptionViewItem.ViewItemPosition.Right
        super(ItemDelegate, self).paint(painter, option, index)


class CustomTimerMeta(type(QWidget), type(ObservedTimer)):
    pass


class CustomTimer(QWidget, ObservedTimer, metaclass=CustomTimerMeta):
    def __init__(self, time_line, timer: QTimer = None, label: QLabel = None, icon: QLabel = None, ):
        super(CustomTimer, self).__init__()
        self.__flag = False
        self.__today = datetime.today()
        self.__running_count = 0
        if timer is None:
            self.__timer = QTimer(self)
        else:
            self.__timer = timer

        if label is None:
            self.__label = QLabel()
        else:
            self.__label = label

        self.__time_line = time_line

        self.__label.setText(str(self.__time_line.duration))
        self.__label.setAlignment(Qt.AlignmentFlag.AlignRight)

        if icon is None:
            self.__icon = QLabel()
        else:
            self.__icon = icon
        self.__icon.setPixmap(QPixmap(consts.START_ICON_PATH))

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()
        layout.addWidget(self.__label)
        layout.addSpacing(2)
        layout.addWidget(self.__icon)

        # update the timer every single second
        self.__timer.start(1000)
        self.__timer.timeout.connect(self.show_time)

    def __get_time(self):
        return self.__time_line.duration

    def __set_time(self, time: timedelta, reset: bool = False):
        if isinstance(time, timedelta):
            if reset:
                self.__time_line.duration = time
            else:
                self.__time_line.duration += time
        else:
            raise TypeError(f"Couldn't parse duration of invalid type {type(time)}")

    time = property(
        fget=__get_time,
        fset=__set_time,
        doc='None.',
    )

    def __get_text(self):
        return self.__label.text()

    def __set_text(self, text):
        self.__label.setText(str(text))

    text = property(
        fget=__get_text,
        fset=__set_text,
        doc='None.',
    )

    def __get_flag(self):
        return self.__flag

    def __set_flag(self, flag):
        self.__flag = flag

    flag = property(
        fget=__get_flag,
        fset=__set_flag,
        doc='None.',
    )

    # method called by timer
    def show_time(self, mode=None):
        if not mode:
            # checking if flag is true
            if self.flag:
                # incrementing the counter
                self.time = timedelta(seconds=1)

            if utils.check_if_midnight() or self.__today.date() > datetime.today().date():
                self.__reset()
        # showing text
        self.__label.setText(str(self.time))

    def change(self):
        # making flag to true
        if not self.flag:
            return self.start()
        else:
            return self.pause()

    def start(self):
        # making flag to true
        self.__icon.setPixmap(QPixmap(consts.PAUSE_ICON_PATH))

        self.flag = True
        self.__running_count += self.flag
        if self.__running_count == 1:
            self.notify({
                'project_id': self.__time_line.project_id,
                'task_id': self.__time_line.task_id,
                'user_id': self.__time_line.user_id,
            })
            # self.__time_line.time_start = datetime.now().time()

        return self

    def pause(self):  # Notify the Observer Only On stop to update the DB
        # making flag to False
        self.__icon.setPixmap(QPixmap(consts.START_ICON_PATH))
        self.flag = False
        self.__running_count = 0
        self.notify({
            'project_id': self.__time_line.project_id,
            'task_id': self.__time_line.task_id,
            'user_id': self.__time_line.user_id,
        }, state='update')

        return self

    def __reset(self):
        self.__set_time(timedelta(seconds=0), reset=True)


class TimeTracker(QWidget):
    def __init__(self, parent=None, timer: QTimer = None, label: QLabel = None, icon: QLabel = None, icon_flag=True):
        super(TimeTracker, self).__init__(parent=parent)
        self.__icon_flag = icon_flag
        self.__flag = False
        self.__today = datetime.today()

        self.__time = timedelta(seconds=0)

        if timer is None:
            self.__timer = QTimer(self)
        else:
            self.__timer = timer

        if label is None:
            self.__label = QLabel()
        else:
            self.__label = label

        self.__label.setText(str(timedelta(seconds=0)))
        self.__label.setAlignment(Qt.AlignmentFlag.AlignRight)

        if icon is None:
            self.__icon = QLabel()
        else:
            self.__icon = icon
        self.__icon.setPixmap(QPixmap(consts.START_ICON_PATH))

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()
        layout.addWidget(self.__label)
        if self.__icon_flag:
            layout.addSpacing(2)
            layout.addWidget(self.__icon)

        # update the timer every single second
        self.__timer.start(1000)
        self.__timer.timeout.connect(self.show_time)
        self.show_time()

    def __get_time(self) -> timedelta:
        return self.__time

    def __set_time(self, time: timedelta, reset: bool = False):
        if isinstance(time, timedelta):
            if reset:
                self.__time = time
            else:
                self.__time += time
        else:
            raise TypeError(f"Couldn't parse duration of invalid type {type(time)}")

    time = property(
        fget=__get_time,
        fset=__set_time,
        doc='None.',
    )

    def __get_text(self):
        return self.__label.text()

    def __set_text(self, text):
        self.__label.setText(str(text))

    text = property(
        fget=__get_text,
        fset=__set_text,
        doc='None.',
    )

    def __get_flag(self):
        return self.__flag

    def __set_flag(self, flag):
        self.__flag = flag

    flag = property(
        fget=__get_flag,
        fset=__set_flag,
        doc='None.',
    )

    # method called by timer
    def show_time(self, mode=None):
        # check if display or change mode # default is None --> change mode
        if not mode:
            # checking if flag is true
            if self.flag:
                # incrementing the counter
                self.time = timedelta(seconds=1)

            if utils.check_if_midnight() or self.__today.date() > datetime.today().date():
                self.reset()
        # showing text
        self.__label.setText(str(self.time))

    def start(self):
        # making flag to true
        if self.__icon_flag:
            self.__icon.setPixmap(QPixmap(consts.PAUSE_ICON_PATH))
        self.flag = True
        return self

    def pause(self):  # Notify the Observer Only On stop to update the DB
        # making flag to False
        if self.__icon_flag:
            self.__icon.setPixmap(QPixmap(consts.START_ICON_PATH))
        self.flag = False

        return self

    def reset(self, time: timedelta = timedelta(seconds=0)):
        self.__set_time(time, reset=True)

    def hide(self) -> None:
        super().hide()


if __name__ == '__main__':
    pass
