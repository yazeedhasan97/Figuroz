import logging
import os
import sys
import time
from datetime import datetime

from active_window_watcher.lib import get_current_window
from database import models, db, SQLs
from common import consts
from scripts.controllers import MainController

logger = logging.getLogger(__name__)

# run with LOG_LEVEL=DEBUG
log_level = os.environ.get("LOG_LEVEL")
if log_level:
    logger.setLevel(logging.__getattribute__(log_level.upper()))


class ActiveWindowWatcher:
    def __init__(self, user, args, child_process):

        self.user = user
        self.args = args
        self.child_process = child_process
        # TODO: don't forget to load previous ones from the database -- at least the names
        self.registered = {}  # PID:Name --> use both to compare for new
        self.tracked = {}
        self.active_window = None
        self.load_stored_application()

    def load_stored_application(self):
        df = db.execute(
            SQLs.SELECT_ID_AND_NAME_FROM_APPLICATIONS,
            conn=MainController.DB_CONNECTION
        )
        data = dict(df.to_dict('tight')['data'])
        self.registered.update(data)
        self.tracked.update(dict((v, k) for k, v in data.items()))
        return

    def run(self):
        logger.info("watcher-window started")
        time.sleep(2)
        self.heartbeat_loop()
        pass

    def heartbeat_loop(self, ):
        while True:
            if os.getppid() == 1:
                logger.info("window-watcher stopped because parent process died")
                break

            current_window = None

            try:
                current_window = get_current_window(self.args.strategy)
                logger.debug(current_window)
            except Exception:
                logger.exception("Exception thrown while trying to get active window")

            # now = datetime.now(timezone.utc)
            if current_window is None:
                logger.debug("Unable to fetch window, trying again on next poll")
            else:
                if self.args.exclude_title:
                    current_window["title"] = "excluded"

            # Check For New Applications #
            # TODO: so critical, the name is our primary key ?
            if current_window['app'] not in self.registered.values():
                self.on_new_app(current_window=current_window)

            # Check For Changed Windows #
            if self.active_window is None or (
                    self.active_window is not None
                    and self.active_window.window_url != current_window['path']
            ) or (
                    self.active_window is not None
                    and self.active_window.title != current_window['title']
            ):
                self.on_change_app(current_window)

            print(current_window)
            self.child_process.send(current_window)
            time.sleep(self.args.poll_time)  # poll_time time is 1 sec

    def on_change_app(self, current_window):
        if self.active_window is not None:
            self.active_window.register(MainController.DB_CONNECTION)

        self.active_window = models.Window(
            id=str(self.user.id) + datetime.now().strftime(consts.ID_TIME_FORMATS),
            application_id=self.tracked.get(current_window['app'], 'Error...'),
            title=current_window['title'],
            window_url=current_window['path'],
            start_date=datetime.now(),
            url='' if current_window['app'] not in consts.WEB_BROWSERS else current_window['url'],
        )

    def on_new_app(self, current_window):
        self.registered[current_window['pid']] = current_window['app']

        application = models.Application(
            id=str(self.user.id) + datetime.now().strftime(consts.ID_TIME_FORMATS),
            user=self.user.id,
            name=current_window['app'],
            path=current_window['path'],
            version=current_window['version'],
            description=current_window['description'],
        )
        MainController.store_current_active_application_id(application.id)
        self.tracked[current_window['app']] = application.id

        if self.active_window is not None:
            self.active_window.register(MainController.DB_CONNECTION)
            self.active_window = models.Window(
                id=str(self.user.id) + datetime.now().strftime(consts.ID_TIME_FORMATS),
                application_id=application.id,
                title=current_window['title'],
                window_url=application.path,
                start_date=datetime.now(),
                url='' if application.name not in consts.WEB_BROWSERS else current_window['url'],
            )
        application.register(MainController.DB_CONNECTION)


def main(child_process, user=None):
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

    active_window_watcher = ActiveWindowWatcher(
        user=user,
        args=args,
        child_process=child_process
    )
    active_window_watcher.run()


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
