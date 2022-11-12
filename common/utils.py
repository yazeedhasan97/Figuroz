import base64
import functools
from operator import itemgetter
from itertools import groupby
import os
import pickle
from datetime import datetime, timedelta
from typing import Union
import io
import pandas as pd
import geocoder
from PIL import ImageGrab, ImageFilter, Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

from common import consts

# logging.debug('This is a debug message')
# logging.info('This is an info message')
# logging.warning('This is a warning message')
# logging.error('This is an error message')
# logging.critical('This is a critical message')


ConvertibleTimestamp = Union[datetime, str]


def read_image(path):
    return Image.open(path)


def convert_image_to_binary(img):
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    byte_im = buf.getvalue()
    return byte_im


def remember_me(user, path):
    with open(path, 'bw') as file:
        pickle.dump(user, file)


def base64_converter(img):
    return base64.b64encode(img).decode("utf8")


def get_me(path):
    if os.path.exists(path):
        with open(path, 'rb') as file:
            user = pickle.load(file)
        if user:
            return user
        else:
            return None
    else:
        return None


def check_if_midnight():
    now = datetime.now()
    seconds_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    return seconds_since_midnight == 0


def take_screenshot(user_id, directory, blur=False, blur_deep=2, format='%Y-%m-%dT%H:%M:%S'):
    snapshot = ImageGrab.grab()
    if blur:
        snapshot = snapshot.filter(ImageFilter.BoxBlur(blur_deep))

    path = os.path.join(directory, f'{user_id}_{datetime.now().strftime(format)}_image.png')
    snapshot.save(path, optimize=True, quality=50)


def id_filter(pid, lst, compare=None):
    if compare == 'pid':
        return list(filter(lambda x: x.project_id == pid, lst))
    return list(filter(lambda x: x.id == pid, lst))


def group_by_and_accumulate_timedelta_list_of_tuples(lst) -> dict:
    it = groupby(lst, itemgetter(0))
    items = {}
    for key, subiter in it:
        durations = list(item[1] for item in subiter)
        items[key] = sum(durations, timedelta())
    return items


def extract_before_from(text: str, find: str):
    return text[:text.find(find) + len(find)]


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


def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        import time
        start = time.time()
        x = func(*args, **kwargs)
        end = time.time()
        print(f'{func.__name__} Took {end - start} Time to excute')
        return x

    return wrapper


if __name__ == "__main__":
    print(take_screenshot(
        user_id=182,
        format=consts.IMAGE_DATE_TIME_FORMATS,
        directory=consts.OUTPUT_DIR,
        blur=True,
    ))
