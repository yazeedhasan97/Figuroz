import time
from multiprocessing import Pipe, Process

from common import consts
from scripts.controllers import InputsObserver, MainController
from scripts.trackers import ScreenshotsCapture, Periodic, InternetStateTracker


def test_screenshots():
    screen_capturer = ScreenshotsCapture(
        user_id=182,
        directory=consts.OUTPUT_DIR,
        blur=True,
    )

    periodic = Periodic(
        10,
        screen_capturer.run
    )
    periodic.start()
    pass


def test_active_window_watcher_process():
    # TODO: whatever I do, This won't work as thread
    #  Check what the fuck is going on

    window_watcher = create_active_window_watcher(
        user_id=182,
    )
    parent_conn, child_conn = Pipe()
    window_activity_tracker = Process(
        target=window_watcher.run,
        # args=(child_conn, user),
        daemon=True,
    )
    window_activity_tracker.daemon = True
    window_activity_tracker.start()
    print('Main Thread')
    time.sleep(15)
    window_activity_tracker.kill()
    window_activity_tracker.terminate()
    window_activity_tracker.join()
    window_activity_tracker.close()
    print('Stopping App Watcher ')
    time.sleep(15)
    print('we are still going')

    pass


def test_active_window_watcher_main():
    # TODO: whatever I do, This won't work as thread
    #  Check what the fuck is going on

    window_watcher = create_active_window_watcher(
        user_id=182,
    )
    window_watcher.run()
    pass


def test_idle_watcher():
    from idle_watcher.afk import AFKWatcher

    # Start watcher
    watcher = AFKWatcher(
        user_id=182,
        timeout=5,
    )
    MainController.CURRENT_ACTIVE_APPLICATION_ID = 10
    MainController.CURRENT_ACTIVE_TASK_ID = 122

    periodic = Periodic(
        1,
        watcher.heartbeat
    )
    periodic.start()
    pass


def test_inputs_observer():
    obs = InputsObserver(auto_start=True)
    print(MainController.MOUSE_MOVE_COUNT)
    print(MainController.MOUSE_KEYS_COUNT)
    time.sleep(10)
    print(MainController.MOUSE_MOVE_COUNT)
    print(MainController.MOUSE_KEYS_COUNT)
    obs.stop()
    print('we are here')
    time.sleep(10)
    print(MainController.MOUSE_MOVE_COUNT)
    print(MainController.MOUSE_KEYS_COUNT)
    print('we are here')
    time.sleep(10)


def test_internet_connectivity():
    tracker = InternetStateTracker(
        user_id=182
    )
    print(tracker.ip_address)
    print(tracker.geo_location)
    print(tracker.internet_speed)
    periodic = Periodic(
        5,
        tracker.get_internet_state()
    )
    periodic.start()


if __name__ == "__main__":
    from active_window_watcher.main_window_watcher import create_active_window_watcher
    from apis.sync import DataRequester
    from database.models import create_database_session

    mode = 'test'
    api_sync = DataRequester(mode)

    db_sync = create_database_session(
        consts.TEST_DB_PATH,
        echo=False,
    )

    MainController.store_api_connection(
        api_sync
    )
    MainController.store_database_connection(
        db_sync
    )

    #####################################
    # DONE
    # test_screenshots()
    # test_idle_watcher()
    # test_inputs_observer()
    # test_internet_connectivity()
    # test_active_window_watcher_main()
    # test_active_window_watcher_process()
    #####################################


