import sys
import logging
from datetime import datetime
import os

from common.dirs import get_log_dir


def _create_human_formatter() -> logging.Formatter:  # pragma: no cover
    return logging.Formatter(
        "%(asctime)s [%(levelname)-5s]: %(message)s  (%(name)s:%(lineno)s)",
        "%Y-%m-%d %H:%M:%S",
    )


def _create_stderr_handler() -> logging.Handler:  # pragma: no cover
    stderr_handler = logging.StreamHandler(stream=sys.stderr)
    stderr_handler.setFormatter(_create_human_formatter())

    return stderr_handler


def _create_file_handler(
        name, testing=False, log_json=False
) -> logging.Handler:  # pragma: no cover
    log_dir = get_log_dir(name)

    # Set logfile path and name
    global log_file_path

    # Should result in something like:
    # $LOG_DIR/aw-server_testing_2017-01-05T00:21:39.log
    file_ext = ".log.json" if log_json else ".log"
    now_str = str(datetime.now().replace(microsecond=0).isoformat()).replace(":", "-")
    log_name = name + "_" + ("testing_" if testing else "") + now_str + file_ext
    log_file_path = os.path.join(log_dir, log_name)

    fh = logging.FileHandler(log_file_path, mode="w")
    if log_json:
        fh.setFormatter(_create_json_formatter())
    else:
        fh.setFormatter(_create_human_formatter())

    return fh


def _create_json_formatter() -> logging.Formatter:  # pragma: no cover
    supported_keys = [
        "asctime",
        # 'created',
        "filename",
        "funcName",
        "levelname",
        # 'levelno',
        "lineno",
        "module",
        # 'msecs',
        "message",
        "name",
        "pathname",
        # 'process',
        # 'processName',
        # 'relativeCreated',
        # 'thread',
        # 'threadName'
    ]

    def log_format(x):
        """Used to give JsonFormatter proper parameter format"""
        return [f"%({i:s})" for i in x]

    custom_format = " ".join(log_format(supported_keys))

    try:
        from pythonjsonlogger import jsonlogger
    except ImportError:
        raise ImportError("pythonjsonlogger is required to use json logging.")

    return jsonlogger.JsonFormatter(custom_format)


def setup_logging(name: str, testing=False, verbose=False, log_stderr=True, log_file=False,
                  log_file_json=False, ):  # pragma: no cover
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    root_logger.handlers = []

    # run with LOG_LEVEL=DEBUG to customize log level across all AW components
    log_level = os.environ.get("LOG_LEVEL")
    if log_level:
        if hasattr(logging, log_level.upper()):
            root_logger.setLevel(getattr(logging, log_level.upper()))
        else:
            root_logger.warning(
                f"No logging level called {log_level} (as specified in env var)"
            )

    if log_stderr:
        root_logger.addHandler(_create_stderr_handler())
    if log_file:
        root_logger.addHandler(
            _create_file_handler(name, testing=testing, log_json=log_file_json)
        )

    def excepthook(type_, value, traceback):
        root_logger.exception("Unhandled exception", exc_info=(type_, value, traceback))
        # call the default excepthook if log_stderr isn't true (otherwise it'll just get duplicated)
        if not log_stderr:
            sys.__excepthook__(type_, value, traceback)

    sys.excepthook = excepthook
