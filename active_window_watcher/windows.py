from typing import Optional, Tuple

import wmi
import win32gui
import win32process
from win32com.client import Dispatch

c = wmi.WMI()

"""
Much of this derived from: http://stackoverflow.com/a/14973422/965332
"""


def get_app_path(hwnd, pid=None) -> Optional[str]:
    """Get application path given hwnd."""
    path = None

    if pid is None:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)

    for p in c.query('SELECT ExecutablePath FROM Win32_Process WHERE ProcessId = %s' % str(pid)):
        path = p.ExecutablePath
        break
    return path


def get_app_name(hwnd, pid=None) -> Optional[str]:
    """Get application filename given hwnd."""
    name = None

    if pid is None:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)

    # for p in c.query('SELECT * FROM Win32_Process WHERE ProcessId = %s' % str(pid)):
    for p in c.query('SELECT Name FROM Win32_Process WHERE ProcessId = %s' % str(pid)):
        name = p.Name
        break
    return name


def get_app_name_and_path(hwnd, pid=None) -> Tuple[str]:
    """Get application filename given hwnd."""
    name = None

    if pid is None:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)

    # for p in c.query('SELECT * FROM Win32_Process WHERE ProcessId = %s' % str(pid)):
    for p in c.query('SELECT Name, ExecutablePath FROM Win32_Process WHERE ProcessId = %s' % str(pid)):
        name = p.Name
        path = p.ExecutablePath
        break
    return name, path


def get_app_pid(hwnd) -> Optional[str]:
    """Get application filename given hwnd."""
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    return pid


def get_window_title(hwnd):
    return win32gui.GetWindowText(hwnd)


def get_active_window_handle_and_pid():
    hwnd = win32gui.GetForegroundWindow()
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    return hwnd, pid


def get_window_app_version(app_location):
    try:
        parser = Dispatch("Scripting.FileSystemObject")
        version = parser.GetFileVersion(app_location)
    except Exception as e:
        print('Unable to retrieve app version')
        return None
    return version


if __name__ == "__main__":
    hwnd, pid = get_active_window_handle_and_pid()
    path = get_app_path(hwnd)
    print("Title:", get_window_title(hwnd))
    print("App:", get_app_name(hwnd))
    print("Path:", path)
    print("Version:", get_window_app_version(path))
