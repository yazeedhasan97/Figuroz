import logging
import os
import sys
import time
from datetime import datetime
import joblib
from active_window_watcher.lib import get_current_window
from common import consts
from database.models import create_and_insert_application, create_and_insert_window, create_database_session
from scripts.controllers import MainController

# from scripts.controllers import MainController

logger = logging.getLogger(__name__)

# run with LOG_LEVEL=DEBUG
log_level = os.environ.get("LOG_LEVEL")
if log_level:
    logger.setLevel(logging.__getattribute__(log_level.upper()))


def load_db_connection(path=None):
    # TODO: make sure to fix the path
    if MainController.DB_CONNECTION is None:
        return create_database_session(
            'C:/Users/yazee/PycharmProjects/Figuroz/env/new_local.db',
            echo=False,
        )
    else:
        return MainController.DB_CONNECTION


class ActiveWindowWatcher:
    def __init__(self, user_id, connection, args, ):

        self.user_id = user_id
        self.args = args
        self.registered = {}  # Hash:ID --> use Hash to compare for new and ID to track
        self.tracked = {}
        self.active_window = None
        self.load_stored_applications()
        self.conn = connection

    def load_stored_applications(self):
        from database.models import Application
        data = MainController.DB_CONNECTION.query(Application.hash, Application.id, ).filter(
            Application.user_id == self.user_id
        ).all()
        print(data)
        # data = dict(df.to_dict('tight')['data'])
        self.registered.update(dict(data))
        # self.tracked.update(dict((v, k) for k, v in data.items()))
        self.tracked.update(dict(data))

    def run(self):
        logger.info("watcher-window started")
        time.sleep(1)
        self.heartbeat_loop()
        pass

    def heartbeat(self):
        if os.getppid() == 1:
            logger.info("window-watcher stopped because parent process died")
            return

        current_window = None

        try:
            current_window = get_current_window(self.args.strategy)
            logger.debug(current_window)
        except Exception as e:
            logger.exception("Exception thrown while trying to get active window")
            logger.exception(str(e))

        print(current_window)
        # now = datetime.now(timezone.utc)
        if current_window is None:
            logger.debug("Unable to fetch window, trying again on next poll")
        else:
            if self.args.exclude_title:
                current_window["title"] = "excluded"

        if self.is_new_app(current_window):
            self.on_new_app(current_window=current_window)

        # Check For Changed Windows #
        # if self.active_window is None or (
        #         self.active_window is not None
        #         and self.active_window.window_url != current_window['path']
        # ) or (
        #         self.active_window is not None
        #         and self.active_window.title != current_window['title']
        # ):
        #     self.on_change_app(current_window)

        print(current_window)

    def heartbeat_loop(self, ):
        self.load_connection()
        while True:
            self.heartbeat()
            time.sleep(self.args.poll_time)  # poll_time time is 1 sec

    def on_change_app(self, current_window, conn=None):
        if self.active_window is not None:
            self.active_window.register(MainController.DB_CONNECTION)

        # self.active_window = Window(
        #     id=str(self.user_id) + datetime.now().strftime(consts.ID_TIME_FORMATS),
        #     application_id=self.tracked.get(current_window['name'], 'Error...'),
        #     title=current_window['title'],
        #     window_url=current_window['path'],
        #     start=datetime.now(),
        #     url='' if current_window['name'] not in consts.WEB_BROWSERS else current_window['url'],
        # )

    def on_new_app(self, current_window):
        application = create_and_insert_application(data={
            'description': current_window['description'],
            'version': current_window['description'],
            'path': current_window['path'],
            'name': current_window['name'],
            'user_id': self.user_id,
        }, session=self.conn)

        self.active_window = create_and_insert_window(data={
            'user_id': self.user_id,
            'application_id': application.id,
            'title': current_window['title'],
            'window_url': current_window['path'],
            'url': current_window['url'],
            'domain_url': current_window['domain_url'],
        }, session=self.conn)

        self.registered[application.hash] = application.id
        # self.tracked[current_window['name']] = application.id

    def is_new_app(self, current_window):
        hashed = joblib.hash(str(self.user_id) + current_window['name'] + current_window['path'])
        print(hashed)
        print(self.registered.keys())
        return True if hashed not in self.registered.keys() else False

    def is_new_window(self, current_window):
        pass


def create_active_window_watcher(connection, user_id=None, ):
    from active_window_watcher.config import parse_args
    from active_window_watcher.macos_permissions import background_ensure_permissions
    from common.logs import setup_logging
    args = parse_args()

    if sys.platform.startswith("linux") and (
            "DISPLAY" not in os.environ or not os.environ["DISPLAY"]
    ):
        raise Exception("DISPLAY environment variable not set")

    setup_logging(
        name="watcher-window",
        testing=args.testing,
        verbose=args.verbose,
        log_stderr=True,
        log_file=True,
    )

    if sys.platform == "darwin":
        background_ensure_permissions()

    return ActiveWindowWatcher(
        user_id=user_id,
        args=args,
        connection=connection
    )


if __name__ == "__main__":
    # import threading
    # watcher_thread = threading.Thread( # Threading will not work here
    #     target=main,
    #     daemon=True,
    # )
    # watcher_thread.start()
    #
    # while True:
    #     time.sleep(1)

    # main()
    # df = db.execute(
    #     SQLs.SELECT_ID_AND_NAME_FROM_APPLICATIONS,
    #     # conn_s=MainController.DB_CONNECTION
    # )
    print()
    pass
