import argparse

from common.config_util import load_config_toml

default_config = """
[aw-watcher-window]
exclude_title = false
poll_time = 1.0
strategy_macos = "jxa"
""".strip()


def load_config():
    return load_config_toml("aw-watcher-window", default_config)["aw-watcher-window"]


def parse_args():
    config = load_config()

    default_poll_time = config["poll_time"]
    default_exclude_title = config["exclude_title"]
    default_strategy_macos = config["strategy_macos"]

    parser = argparse.ArgumentParser(
        "A cross platform window watcher for Figuroz.\n"
        "Supported on: Linux (X11), macOS and Windows."
    )
    parser.add_argument("--host", dest="host")
    parser.add_argument("--port", dest="port")
    parser.add_argument("--testing", dest="testing", action="store_true")
    parser.add_argument(
        "--exclude-title",
        dest="exclude_title",
        action="store_true",
        default=default_exclude_title,
    )
    parser.add_argument("--verbose", dest="verbose", action="store_true")
    parser.add_argument(
        "--poll-time", dest="poll_time", type=float, default=default_poll_time
    )
    parser.add_argument(
        "--strategy",
        dest="strategy",
        default=default_strategy_macos,
        choices=["jxa", "applescript"],
        help="(macOS only) strategy to use for retrieving the active window",
    )
    parsed_args = parser.parse_args()
    return parsed_args
