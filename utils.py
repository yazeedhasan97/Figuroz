import os
from datetime import datetime, timezone
from typing import Union

import iso8601
import pandas as pd

import consts
from PIL import ImageGrab

import logging

logger = logging.getLogger(__name__)

ConvertibleTimestamp = Union[datetime, str]


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
    df = df.drop(df.index, )
    return df
