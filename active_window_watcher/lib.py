import sys
from typing import Optional


def get_current_window_linux() -> Optional[dict]:
    from active_window_watcher import xlib

    window = xlib.get_current_window()

    if window is None:
        cls = "unknown"
        name = "unknown"
    else:
        cls = xlib.get_window_class(window)
        name = xlib.get_window_name(window)

    return {"app": cls, "title": name}


def get_current_window_macos(strategy: str) -> Optional[dict]:
    # TODO should we use unknown when the title is blank like the other platforms?

    # `jxa` is the default & preferred strategy. It includes the url + incognito status
    if strategy == "jxa":
        from active_window_watcher import macos_jxa

        return macos_jxa.getInfo()
    elif strategy == "applescript":
        from active_window_watcher import macos_applescript

        return macos_applescript.getInfo()
    else:
        raise ValueError(f"invalid strategy '{strategy}'")


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
    if sys.platform.startswith("linux"):
        return get_current_window_linux()
    elif sys.platform == "darwin":
        return get_current_window_macos(strategy)
    elif sys.platform in ["win32", "cygwin"]:
        return get_current_window_windows()
    else:
        raise Exception("Unknown platform: {}".format(sys.platform))
