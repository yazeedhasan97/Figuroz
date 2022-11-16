import io
import os
from datetime import datetime
from threading import Timer, Lock

from PIL import ImageGrab, ImageFilter, Image, ImageFile

from database.models import create_and_insert_screenshot, create_and_insert_user_account_settings
from scripts.controllers import MainController

import socket
import speedtest

ImageFile.LOAD_TRUNCATED_IMAGES = True


class Periodic:
    """ A periodic task running in threading.Timers """

    def __init__(self, interval, function, *args, **kwargs):
        self._lock = Lock()
        self._timer = None
        self.function = function
        self.interval = interval
        self.args = args
        self.kwargs = kwargs
        self._stopped = True
        if kwargs.pop('autostart', True):
            self.start()

    def start(self, from_run=False):
        self._lock.acquire()
        if from_run or self._stopped:
            self._stopped = False
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
        self._lock.release()

    def _run(self):
        self.start(from_run=True)
        self.function(*self.args, **self.kwargs)

    def stop(self):
        self._lock.acquire()
        self._stopped = True
        self._timer.cancel()
        self._lock.release()


class ScreenshotsCapture:
    def __init__(self, user_id, directory, blur=False, blur_deep=2, file_date_format='%Y_%m_%dT%H_%M_%S'):
        self.user_id = user_id
        self.directory = directory
        self.blur = blur
        self.blur_deep = blur_deep
        self.format = file_date_format

    def run(self):
        print('Capturing Screen')
        img = self.take_screenshot()
        binary_img = self.convert_image_to_binary(img)
        print('Inserting Screen to DB')
        create_and_insert_screenshot(data={
            'user_id': self.user_id,
            'img': binary_img,
            'mouse_move': MainController.MOUSE_MOVE_COUNT,
            'key_click': MainController.KEYBOARD_KEYS_COUNT,
            'mouse_clicks': MainController.MOUSE_KEYS_COUNT,
        }, session=MainController.DB_CONNECTION)

    def take_screenshot(self):
        snapshot = ImageGrab.grab()
        if self.blur:
            snapshot = snapshot.filter(ImageFilter.BoxBlur(self.blur_deep))

        path = os.path.join(self.directory, f'{self.user_id}_{datetime.now().strftime(self.format)}_image.png')
        snapshot.save(path, optimize=True, quality=50)
        return snapshot

    def read_image(self, path):
        return Image.open(path)

    def convert_image_to_binary(self, img):
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        byte_im = buf.getvalue()
        return byte_im


class InternetStateTracker:
    def __init__(self, user_id, ):
        self.user_id = user_id
        self.ip_address = None
        self.get_ip_address()

        self.geo_location = None
        self.get_geo_location()

        self.internet_speed = None
        self.get_internet_state()
        pass

    def get_ip_address(self):
        self.ip_address = str(socket.gethostbyname(socket.gethostname()))

    def get_geo_location(self, user='me'):
        import geocoder
        try:
            self.geo_location = str(geocoder.ip(user).latlng)
        except Exception as e:
            print("Unable to extract the current user location")
            self.geo_location = 'unknown'

    def get_internet_state(self):
        try:
            speed_test = speedtest.Speedtest()
            speedtest.get_best_server()
            speed_test.download()
            speed_test.upload()
            res = speed_test.results.dict()
            self.internet_speed = [res["upload"], res["download"]]
            # print(self.internet_speed)
        except Exception as e:
            print('No internet connection available')
            if self.internet_speed is None:
                self.internet_speed = [0, 0]

            # create_and_insert_user_account_settings(data={
            #     'internet': self.internet_speed,
            #     'ip_address': self.ip_address,
            #     'geo_location': self.geo_location,
            #     'user_id': self.user_id,
            # }, session=MainController.DB_CONNECTION)


if __name__ == "__main__":

    pass
