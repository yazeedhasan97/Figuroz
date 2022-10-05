import logging
import numbers
import os
import sys

from datetime import timedelta, datetime
from typing import Union

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QLabel, QWidget, QHBoxLayout, QStyledItemDelegate, QStyleOptionViewItem, QApplication

import consts
import utils

logger = logging.getLogger(__name__)

Number = Union[int, float]
Duration = Union[timedelta, Number]


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


class CustomTimer(QWidget, ):
    def __init__(self, parent=None, count: Duration = timedelta(seconds=0), flag: bool = False, timer: QTimer = None,
                 label: QLabel = None, icon: QLabel = None):
        super(CustomTimer, self).__init__(parent)
        self.__count = count
        self.__flag = flag
        self.__today = datetime.today()

        if timer is None:
            self.__timer = QTimer(self)
        else:
            self.__timer = timer
        # update the timer every single second

        if label is None:
            self.__label = QLabel()
        else:
            self.__label = label

        self.__label.setText(str(self.count))
        self.__label.setAlignment(Qt.AlignmentFlag.AlignRight)

        if icon is None:
            self.__icon = QLabel()
        else:
            self.__icon = icon
        # TODO: the size problem is in here for the icons
        self.__icon.setPixmap(QPixmap(consts.START_ICON_PATH))

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()
        layout.addWidget(self.__label)
        layout.addSpacing(2)
        layout.addWidget(self.__icon)

        self.__timer.start(1000)
        self.__timer.timeout.connect(self.show_time)

    def __get_count(self):
        # return self.__count
        return self.__count

    def __set_count(self, count: Duration, reset: bool = False):
        if isinstance(count, timedelta):
            if reset:
                self.__count = count
            else:
                self.__count += count
        elif isinstance(count, numbers.Real):
            if reset:
                self.__count = timedelta(seconds=count)
            else:
                self.__count += timedelta(seconds=count)
        else:
            raise TypeError(f"Couldn't parse duration of invalid type {type(count)}")

    count = property(
        fget=__get_count,
        fset=__set_count,
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
        # checking if flag is true
        if not mode:
            if self.flag:
                # incrementing the counter
                self.count = timedelta(seconds=1)

            if utils.check_if_midnight() or self.__today.date() > datetime.today().date():
                self.__reset()
        # showing text
        self.__label.setText(str(self.count))


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

        return self

    def pause(self):
        # making flag to False
        self.__icon.setPixmap(QPixmap(consts.START_ICON_PATH))
        self.flag = False
        return self

    def __reset(self):
        self.flag = False
        self.__set_count(timedelta(seconds=0), reset=True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = CustomTimer()
    form.show()

    sys.exit(app.exec())
    pass
