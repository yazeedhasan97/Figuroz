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
            consts.TEST_DB_PATH,
            echo=False,
        )
    else:
        return MainController.DB_CONNECTION


active_application_id = None


class ActiveWindowWatcher:
    def __init__(self, user_id, args, ):

        self.user_id = user_id
        self.args = args
        self.registered = {}  # Hash:ID --> use Hash to compare for new and ID to track
        self.tracked = {}
        self.active_window = None
        self.load_stored_applications()

        self.conn = None

    def load_stored_applications(self):
        from database.models import Application
        data = MainController.DB_CONNECTION.query(Application.hash, Application.id, ).filter(
            Application.user_id == self.user_id
        ).all()
        # data = dict(df.to_dict('tight')['data'])
        self.registered.update(dict(data))
        # self.tracked.update(dict((v, k) for k, v in data.items()))
        self.tracked.update(dict(data))

    def run(self, ):
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
            return

        # now = datetime.now(timezone.utc)
        if current_window is None:
            logger.debug("Unable to fetch window, trying again on next poll")
            return
        else:
            if self.args.exclude_title:
                current_window["title"] = "excluded"

        if self.is_new_app(current_window):
            self.on_new_app(current_window=current_window)

        if self.is_new_window(current_window):
            self.on_change_app(current_window=current_window)

        #     self.on_change_app(current_window)

        print(current_window)

    def heartbeat_loop(self, ):
        self.conn = load_db_connection()
        while True:
            self.heartbeat()
            time.sleep(self.args.poll_time)  # poll_time time is 1 sec

    def on_change_app(self, current_window, ):
        global active_application_id
        hashed = joblib.hash(str(self.user_id) + current_window['name'] + current_window['path'])
        active_application_id = self.registered.get(hashed, None)

        self.active_window = create_and_insert_window(data={
            'user_id': self.user_id,
            # TODO: from where the fuck to get this on
            'application_id': active_application_id,
            'title': current_window['title'],
            'window_url': current_window['path'],
            'url': current_window['url'],
            'domain_url': current_window['domain_url'],
        }, session=self.conn)

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
        global active_application_id
        active_application_id = application.id

    def is_new_app(self, current_window):
        hashed = joblib.hash(str(self.user_id) + current_window['name'] + current_window['path'])
        print(hashed)
        print(self.registered.keys())
        return True if hashed not in self.registered.keys() else False

    def is_new_window(self, current_window):
        # Check For Changed Windows #
        if self.active_window is None or (self.active_window is not None and (
                self.active_window.window_url.lower() != current_window['path'] or
                self.active_window.title.lower() != current_window['title']
        )):
            print('New Window')
            return True
        else:
            print('Not New Window')
            return False


def create_active_window_watcher(user_id=None, ):
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
