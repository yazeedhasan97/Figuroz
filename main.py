import os
import sys

from PyQt6.QtWidgets import QApplication

from scripts import views, db, consts
from scripts.controllers import MainController


# TODO: Check what changes the datatypes in teh databases
# TODO: Validate the double insert behaviour of the first task in the first loaded project
# TODO: Remove the double click behavior over the tasks
# TODO: More modifications over the UI/UX

# TODO: Check why multiple users continue to each other

def main(args):
    try:
        conn = db.create_db_connection()
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
