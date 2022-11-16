import sys
from typing import Optional
from active_window_watcher.exceptions import FatalError


def get_current_window_linux() -> Optional[dict]:
    from active_window_watcher import xlib

    window = xlib.get_current_window()

    if window is None:
        title = "unknown"
        name = "unknown"
        pid = "unknown"
    else:
        pid = xlib.get_window_pid(window)
        name = xlib.get_window_class(window)
        title = xlib.get_window_name(window)

    return {
        "pid": pid,
        "name": name.lower(),
        "path": 'path'.lower(),  # also called window url
        "title": title.lower(),
        "version": 'version',
        "description": '',
        "url": '',
        "domain_url": '',
    }


def get_current_window_macos(strategy: str) -> Optional[dict]:
    # TODO should we use unknown when the title is blank like the other platforms?

    # `jxa` is the default & preferred strategy. It includes the url + incognito status
    if strategy == "jxa":
        from active_window_watcher import macos_jxa

        return macos_jxa.getInfo()
    elif strategy == "applescript":
        from . import macos_applescript

        return macos_applescript.getInfo()
    else:
        raise FatalError(f"invalid strategy '{strategy}'")


def get_current_window_windows() -> Optional[dict]:
    from active_window_watcher import windows

    window_handle, pid = windows.get_active_window_handle_and_pid()
    app = windows.get_app_name(window_handle, pid=pid)

    title = windows.get_window_title(window_handle)
    path = windows.get_app_path(window_handle, pid=pid)

    if path is None:
        path = "unknown"
        version = "unknown"
    else:
        version = windows.get_window_app_version(path)
        if version is None:
            version = "unknown"

    if app is None:
        app = "unknown"

    if title is None:
        title = "unknown"

    return {
        "pid": pid,
        "name": app[:app.rfind('.')].lower(),
        "path": path.lower(),  # also called window url
        "title": title.lower(),
        "version": version,
        "description": '',
        "url": '',
        "domain_url": '',
    }


def get_current_window(strategy: str = None) -> Optional[dict]:
    """ :raises FatalError: if a fatal error occurs (e.g. unsupported platform, X server closed)
    """
    if sys.platform.startswith("linux"):
        return get_current_window_linux()
    elif sys.platform == "darwin":
        if strategy is None:
            raise FatalError("macOS strategy not specified")
        return get_current_window_macos(strategy)
    elif sys.platform in ["win32", "cygwin"]:
        return get_current_window_windows()
    else:
        raise FatalError(f"Unknown platform: {sys.platform}")
