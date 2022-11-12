import os
import sys

from PyQt6.QtWidgets import QApplication

from scripts import views
from common import consts
from scripts.controllers import MainController


def main(args):

    try:
        MainController.initiate_database_connection(consts.DB_PATH)
    except Exception as e:
        raise Exception("Couldn't establish a database connection.")

    # db_models.initiate_database_models(conn)

    # try:
    #     settings = db_models.Settings.load_settings(conn)
    #     MainController.initiate_settings(settings)
    #
    # except Exception as e:
    #     print(e)
    #     raise Exception("Couldn't establish the settings.")

    app = QApplication(args)
    MainController.store_screen_details(app.primaryScreen())
    try:
        form = views.LoginForm()
        if not os.path.exists(consts.REMEMBER_ME_FILE_PATH):
            form.show()

    except Exception as e:
        print(e)
        raise e
    finally:
        if MainController.DB_CONNECTION is not None:
            MainController.close_database_connection()
    code = app.exec()
    sys.exit(code)


if __name__ == '__main__':
    main(sys.argv)
