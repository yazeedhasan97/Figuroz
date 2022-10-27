import os
import pickle
from datetime import datetime, timezone
from typing import Union
import iso8601
import pandas as pd
import geocoder
from PIL import ImageGrab, ImageFilter

import logging

logger = logging.getLogger(__name__)

ConvertibleTimestamp = Union[datetime, str]


def remember_me(user, path):
    with open(path, 'bw') as file:
        pickle.dump(user, file)


def get_me(path):
    if os.path.exists(path):
        with open(path, 'rb') as file:
            user = pickle.load(file)
        if user is not None:
            return user
        else:
            return None
    else:
        return None


def check_if_midnight():
    now = datetime.now()
    seconds_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    return seconds_since_midnight == 0


def convert_file_to_binary(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        return file.read()


def take_screenshot(save_path, blur=False, blur_deep=4):
    snapshot = ImageGrab.grab()
    if blur:
        snapshot = snapshot.filter(ImageFilter.BoxBlur(blur_deep))

    path = os.path.join(save_path, f'./Image_{datetime.now():%Y%m%d_%H%M%S}.png')
    snapshot.save(path)
    return convert_file_to_binary(path), snapshot.width, snapshot.height


def id_filter(pid, lst, compare=None):
    if compare == 'pid':
        return list(filter(lambda x: x.project_id == pid, lst))
    return list(filter(lambda x: x.id == pid, lst))


# def sub_id_filter(pid, lst):
#     return list(filter(lambda x: x.sub_id == pid, lst))


def extract_before_from(text: str, find: str):
    return text[:text.find(find) + len(find)]


def timestamp_parse(ts_in: ConvertibleTimestamp) -> datetime:
    """
    Takes something representing a timestamp and
    returns a timestamp in the representation we want.
    """
    ts = iso8601.parse_date(ts_in) if isinstance(ts_in, str) else ts_in
    # Set resolution to milliseconds instead of microseconds
    # (Fixes incompability with software based on unix time, for example mongodb)
    ts = ts.replace(microsecond=int(ts.microsecond / 1000) * 1000)
    # Add timezone if not set
    if not ts.tzinfo:
        # Needed? All timestamps should be iso8601 so ought to always contain timezone.
        # Yes, because it is optional in iso8601
        logger.warning(f"timestamp without timezone found, using UTC: {ts}")
        ts = ts.replace(tzinfo=timezone.utc)
    return ts


def create_df_from_object(obj):
    df = pd.DataFrame(obj).T
    df.columns = df.iloc[0]
    df = df.drop(0, ).reset_index(drop=True)
    return df


# def calculate_internet_speed():
#     internet = speedtest.Speedtest()
#     return internet.download(), internet.upload()

def get_user_location(user='me'):
    return geocoder.ip(user).latlng


if __name__ == "__main__":
    print(get_user_location())
