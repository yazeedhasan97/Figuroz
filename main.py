import os
import sys

from PyQt6.QtWidgets import QApplication

from apis.sync import MasterSync
from database.models import create_database_session
from common import consts
from scripts.controllers import MainController
from scripts.views import LoginForm


def main(args):
    api_sync = MasterSync('test')
    MainController.store_api_connection(api_sync)

    db_sync = create_database_session('C:/Users/yazee/PycharmProjects/Figuroz/env/new_local.db', echo=False)
    MainController.store_database_connection(db_sync)

    app = QApplication(sys.argv)
    try:
        form = LoginForm()
        if not os.path.exists(consts.REMEMBER_ME_FILE_PATH):
            form.show()

    except Exception as e:
        print(e)
        raise e
    finally:
        pass
    code = app.exec()
    sys.exit(code)


if __name__ == '__main__':
    main(sys.argv)
