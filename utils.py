import os
from datetime import datetime

import consts
from PIL import ImageGrab


def check_if_midnight():
    now = datetime.now()
    seconds_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    return seconds_since_midnight == 0


def take_screenshot():
    snapshot = ImageGrab.grab()
    snapshot.save(os.path.join(consts.OUTPUT_DIR, f'./Image_{datetime.now():%Y%m%d_%H%H%S}.png'))


def pid_filter(pid, lst):
    return list(filter(lambda x: x.project_id == pid, lst))


def extract_before_from(text: str, find: str):
    return text[:text.find(find) + len(find)]
