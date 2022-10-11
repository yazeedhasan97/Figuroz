import os
import sys

from PyQt6.QtWidgets import QApplication

import consts
import views


def main(args):
    app = QApplication(sys.argv)

    form = views.LoginForm()
    if not os.path.exists(consts.REMEMBER_ME_FILE_PATH):
        form.show()

    # sys.exit(app.exec())
    sys.exit(app.exec())


if __name__ == '__main__':
    main(sys.argv)
