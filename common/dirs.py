import os
from typing import Optional, Callable
from functools import wraps

import appdirs

GetDirFunc = Callable[[Optional[str]], str]


def ensure_path_exists(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)


def _ensure_returned_path_exists(f: GetDirFunc) -> GetDirFunc:
    @wraps(f)
    def wrapper(sub_path: Optional[str] = None) -> str:
        path = f(sub_path)
        ensure_path_exists(path)
        return path

    return wrapper


@_ensure_returned_path_exists
def get_config_dir(module_name: Optional[str] = None) -> str:
    config_dir = appdirs.user_config_dir("activitywatch")
    return os.path.join(config_dir, module_name) if module_name else config_dir


@_ensure_returned_path_exists
def get_log_dir(module_name: Optional[str] = None) -> str:  # pragma: no cover
    log_dir = appdirs.user_log_dir("activitywatch")
    return os.path.join(log_dir, module_name) if module_name else log_dir
