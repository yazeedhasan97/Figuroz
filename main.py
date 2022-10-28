import os
import sys

from PyQt6.QtWidgets import QApplication

from scripts import views, db, consts
from scripts.controllers import MainController

# TODO: check what changes the datatypes in teh databases
# TODO: validate the double insert behaviour of the first task in the first loaded project
# TODO:  remove the double click behavior over the tasks
# TODO: more modifications over the UI/UX


def main(args):
    try:
        conn = db.create_db_connection(path=consts.DB_CONFIG_FILE)
        MainController.initiate_database_connection(conn)

    except Exception as e:
        print(e)
        raise Exception("Couldn't establish a database connection.")

    # db_models.initiate_database_models(conn)

    # try:
    #     settings = db_models.Settings.load_settings(conn)
    #     MainController.initiate_settings(settings)
    #
    # except Exception as e:
    #     print(e)
    #     raise Exception("Couldn't establish the settings.")

    try:
        app = QApplication(args)
        form = views.LoginForm()
        if not os.path.exists(consts.REMEMBER_ME_FILE_PATH):
            form.show()
        code = app.exec()

        MainController.close_database_connection()
        sys.exit(code)
    except Exception as e:
        print(e)
        raise e
    finally:
        pass


if __name__ == '__main__':
    main(sys.argv)
