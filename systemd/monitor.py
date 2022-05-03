from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer
from pathlib import Path
# from teddy import getLogger
# from rich import print
import logging
import time
import sys


class MonitorChanges(PatternMatchingEventHandler):
    # def catch_all_handler(self, event):
    #     pass
    #     log.debug(event)

    # def on_moved(self, event):
    #     # if ".db" in event.src_path:
    #     #     log.warn(f'DB Moved???: "Updating GitHub"')
    #     #     # self.git_update()
    #     return

    # def on_created(self, event):
    #     if ".pdf" in event.src_path:
    #         logging.info(f'PDF Item Created: "SCP to Server"')
    #         logging.info(event)

    # def on_deleted(self, event):
    #     # if ".db" in event.src_path:
    #     #     log.info(f'DB Item Deleted: "Updating GitHub"')
    #     #     # self.git_update()
    #     return

    def on_modified(self, event):
        if ".pdf" in event.src_path:
            logging.info(f'PDF Item Modified: "SCP to Server"')
            logging.info(event)


if __name__ == '__main__':
    print(Path.cwd())
    # log = getLogger()
    logging.basicConfig(level=logging.INFO)

    event_handler = MonitorChanges(patterns=["*.pdf"], ignore_patterns=["*.py", "*.db"], ignore_directories=True)
    observer = Observer()
    # -- observer.daemon=True
    observer.schedule(event_handler, Path.cwd().joinpath("pdf_outgoing").as_posix(), recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
