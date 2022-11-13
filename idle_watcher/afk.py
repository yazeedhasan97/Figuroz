import logging
import platform
import os
from datetime import datetime, timedelta, timezone
import time

from common.logs import setup_logging
from database.models import create_idle
from scripts.controllers import MainController

from idle_watcher.config import load_config

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
    def __init__(self, user_id, timeout, pull_time=1):
        # self.args = parse_args()

        self.timeout = timeout
        self.pull_time = pull_time
        # Read settings from config
        self.settings = Settings(
            load_config(False), timeout=self.timeout, poll_time=self.pull_time
        )

        # Set up logging
        setup_logging(
            "aw-watcher-afk",
            testing=False,
            verbose=False,
            log_stderr=True,
            log_file=False,
        )

        self.user_id = user_id
        self.created = False
        self.supplier = None
        self.afk = False

    def ping(self, afk: bool, timestamp: datetime, duration: float = 0):
        # data = {"status": "afk" if afk else "not-afk"}
        print("afk" if afk else "not-afk")
        if afk and self.supplier is None:
            self.supplier = create_idle({
                'user_id': self.user_id,
                'application_id': MainController.CURRENT_ACTIVE_APPLICATION_ID,  # TODO: must not be None
                'task_id': MainController.CURRENT_ACTIVE_TASK_ID,  # TODO: must not be None
            })
        if not afk and self.supplier is not None:
            self.supplier.end = datetime.now()
            self.supplier.duration = (self.supplier.end - self.supplier.start).total_seconds()
            MainController.DB_CONNECTION.add(self.supplier)
            MainController.DB_CONNECTION.commit()
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

    def heartbeat(self):
        try:
            if system in ["Darwin", "Linux"] and os.getppid() == 1:
                # TODO: This won't work with PyInstaller which starts a bootloader process
                #  which will become the parent.
                #   There is a solution however.
                #    See: https://github.com/ActivityWatch/aw-qt/issues/19#issuecomment-316741125
                logger.info("afk-watcher stopped because parent process died")
                return

            now = datetime.now(timezone.utc)
            seconds_since_input = seconds_since_last_input()
            last_input = now - timedelta(seconds=seconds_since_input)
            logger.debug("Seconds since last input: {}".format(seconds_since_input))
            print("Seconds since last input: {}".format(seconds_since_input))
            # If no longer AFK
            if self.afk and seconds_since_input < self.settings.timeout:
                logger.info("No longer AFK")
                self.ping(self.afk, timestamp=last_input)
                self.afk = False
                # ping with timestamp+1ms with the next event (to ensure the latest event gets retrieved by get_event)
                self.ping(self.afk, timestamp=last_input + td1ms)
            # If becomes AFK
            elif not self.afk and seconds_since_input >= self.settings.timeout:
                logger.info("Became AFK")
                self.ping(self.afk, timestamp=last_input)
                self.afk = True
                # ping with timestamp+1ms with the next event (to ensure the latest event gets retrieved by get_event)
                self.ping(
                    self.afk, timestamp=last_input + td1ms, duration=seconds_since_input
                )
            # Send a heartbeat if no state change was made
            else:
                if self.afk:
                    self.ping(
                        self.afk, timestamp=last_input, duration=seconds_since_input
                    )
                else:
                    self.ping(self.afk, timestamp=last_input)

        except KeyboardInterrupt:
            logger.info("aw-watcher-afk stopped by keyboard interrupt")
            return
