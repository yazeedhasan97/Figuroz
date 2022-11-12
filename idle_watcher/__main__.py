import time

from common.logs import setup_logging
from idle_watcher.afk import AFKWatcher
from idle_watcher.config import parse_args


def main() -> None:
    args = parse_args()

    # Set up logging
    setup_logging(
        "aw-watcher-afk",
        testing=args.testing,
        verbose=args.verbose,
        log_stderr=True,
        log_file=True,
    )

    # Start watcher
    watcher = AFKWatcher(args, testing=args.testing)
    watcher.run()


if __name__ == "__main__":
    import threading
    x = threading.Thread(
        target=main,
        daemon=True
    )
    x.start()
    while 1:
        time.sleep(1)

    # main()
