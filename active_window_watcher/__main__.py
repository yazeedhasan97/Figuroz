# import os
# import sys
# import time

# def main(child_process, user=None):
#     from active_window_watcher.config import parse_args
#     from active_window_watcher.macos_permissions import background_ensure_permissions
#     from active_window_watcher.main_window_watcher import ActiveWindowWatcher
#     from common.logs import setup_logging
#     args = parse_args()
#
#     if sys.platform.startswith("linux") and (
#             "DISPLAY" not in os.environ or not os.environ["DISPLAY"]
#     ):
#         raise Exception("DISPLAY environment variable not set")
#
#     setup_logging(
#         name="watcher-window",
#         testing=args.testing,
#         verbose=args.verbose,
#         log_stderr=True,
#         log_file=True,
#     )
#
#     if sys.platform == "darwin":
#         background_ensure_permissions()
#
#     active_window_watcher = ActiveWindowWatcher(
#         user=user,
#         args=args,
#         child_process=child_process
#     )
#     active_window_watcher.run()


# if __name__ == "__main__":
#     # main()
#     from multiprocessing import Process, Pipe
#     from scripts.controllers import MainController
#     from scripts.sync import Sync
#
#     MainController.initiate_database_connection()
#     user = Sync.send_login_request('emran.allan@gmail.com', 'Emran@111')
#     parent_conn, child_conn = Pipe()
#     p = Process(target=main, args=(child_conn, user))
#     p.start()
#
#     while True:
#         # print(parent_conn.recv())  # prints "Hello"
#         print(1)
#         time.sleep(1)
