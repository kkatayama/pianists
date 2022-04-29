from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer
from pathlib import Path
# from teddy import getLogger
# from rich import print
import logging
import time
import sys
import git



class MonitorChanges(PatternMatchingEventHandler):
    # def catch_all_handler(self, event):
    #     pass
    #     log.debug(event)

    def on_moved(self, event):
        # if ".db" in event.src_path:
        #     log.warn(f'DB Moved???: "Updating GitHub"')
        #     # self.git_update()
        return

    def on_created(self, event):
        # if ".db" in event.src_path:
        #     log.info(f'DB Item Added: "Updating GitHub"')
        #     # self.git_update()
        return

    def on_deleted(self, event):
        # if ".db" in event.src_path:
        #     log.info(f'DB Item Deleted: "Updating GitHub"')
        #     # self.git_update()
        return

    def on_modified(self, event):
        if ".db" in event.src_path:
            logging.info(f'DB Item Modified: "Updating GitHub"')
            # self.git_update()

            msg='sync db changes'
            repo = git.Repo(Path.cwd().joinpath('.git').as_posix())
            logging.info("marking git repo...")
            time.sleep(5)

            repo.git.add('--all')
            logging.info("git add -A")
            time.sleep(4)

            repo.git.commit('-am', f'{msg}', author='katayama@udel.edu')
            logging.info("git commit -am")
            time.sleep(4)

            origin = repo.remote(name="origin")
            origin.push()
            logging.info("git push")
            time.sleep(3)


if __name__ == '__main__':
    print(Path.cwd())
    # log = getLogger()
    logging.basicConfig(level=logging.INFO)

    event_handler = MonitorChanges(patterns=["*.db", "*.pdf"], ignore_patterns=["*.py"], ignore_directories=True)
    observer = Observer()
    # -- observer.daemon=True
    observer.schedule(event_handler, Path.cwd().as_posix(), recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
