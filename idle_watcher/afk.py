import logging
import platform
import os
from datetime import datetime, timedelta, timezone
import time

from database import models
from common import consts
from scripts.controllers import MainController

from .config import load_config

system = platform.system()

if system == "Windows":
    from idle_watcher.windows import seconds_since_last_input
elif system == "Darwin":
    from idle_watcher.macos import seconds_since_last_input
elif system == "Linux":
    from idle_watcher.unix import seconds_since_last_input
else:
    raise Exception(f"Unsupported platform: {system}")

logger = logging.getLogger(__name__)
td1ms = timedelta(milliseconds=1)


class Settings:
    def __init__(self, config_section, timeout=None, poll_time=None):
        # Time without input before we're considering the user as AFK
        self.timeout = timeout or config_section["timeout"]
        # How often we should poll for input activity
        self.poll_time = poll_time or config_section["poll_time"]

        assert self.timeout >= self.poll_time


class AFKWatcher:
    def __init__(self, args, user, testing=False):
        # Read settings from config
        self.settings = Settings(
            load_config(testing), timeout=args.timeout, poll_time=args.poll_time
        )

        self.user = user
        self.created = False
        self.supplier = None

    def ping(self, afk: bool, timestamp: datetime, duration: float = 0):
        # data = {"status": "afk" if afk else "not-afk"}
        print("afk" if afk else "not-afk")
        if afk and self.supplier is None:
            self.supplier = models.Idle(
                id=str(self.user.id) + datetime.now().strftime(consts.ID_TIME_FORMATS),
                # TODO: we should select this from WindowTracker
                application_id=MainController.CURRENT_ACTIVE_APPLICATION_ID,
                task_id=MainController.CURRENT_ACTIVE_TASK_ID,
            )
        if not afk and self.supplier is not None:
            self.supplier.stopped()  # TODO: timestamp and duration are already supplied.., do we need a recalc?
            self.supplier.register(conn=MainController.DB_CONNECTION)
            self.supplier = None

    def run(self):
        logger.info("aw-watcher-afk started")
        time.sleep(1)
        self.heartbeat_loop()

    def heartbeat_loop(self):
        afk = False
        while True:
            try:
                if system in ["Darwin", "Linux"] and os.getppid() == 1:
                    # TODO: This won't work with PyInstaller which starts a bootloader process
                    #  which will become the parent.
                    #   There is a solution however.
                    #    See: https://github.com/ActivityWatch/aw-qt/issues/19#issuecomment-316741125
                    logger.info("afk-watcher stopped because parent process died")
                    break

                now = datetime.now(timezone.utc)
                seconds_since_input = seconds_since_last_input()
                last_input = now - timedelta(seconds=seconds_since_input)
                logger.debug("Seconds since last input: {}".format(seconds_since_input))

                # If no longer AFK
                if afk and seconds_since_input < self.settings.timeout:
                    logger.info("No longer AFK")
                    self.ping(afk, timestamp=last_input)
                    afk = False
                    # ping with timestamp+1ms with the next event (to ensure the latest event gets retrieved by get_event)
                    self.ping(afk, timestamp=last_input + td1ms)
                # If becomes AFK
                elif not afk and seconds_since_input >= self.settings.timeout:
                    logger.info("Became AFK")
                    self.ping(afk, timestamp=last_input)
                    afk = True
                    # ping with timestamp+1ms with the next event (to ensure the latest event gets retrieved by get_event)
                    self.ping(
                        afk, timestamp=last_input + td1ms, duration=seconds_since_input
                    )
                # Send a heartbeat if no state change was made
                else:
                    if afk:
                        self.ping(
                            afk, timestamp=last_input, duration=seconds_since_input
                        )
                    else:
                        self.ping(afk, timestamp=last_input)

                time.sleep(self.settings.poll_time)

            except KeyboardInterrupt:
                logger.info("aw-watcher-afk stopped by keyboard interrupt")
                break
