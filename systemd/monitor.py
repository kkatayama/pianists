from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer
from pathlib import Path
from teddy import getLogger
from rich import print
import logging
import time
import sys
import git



class MonitorChanges(PatternMatchingEventHandler):
    def catch_all_handler(self, event):
        pass
        # log.debug(event)

    def on_moved(self, event):
        log.debug(f'MOVED: "{event.src_path}"')
        if ".db" in event.src_path:
            log.warn(f'DB Moved???: "Updating GitHub"')
            self.git_update()

    def on_created(self, event):
        log.debug(f'CREATED: "{event.src_path}"')
        if ".db" in event.src_path:
            log.info(f'DB Item Added: "Updating GitHub"')
            self.git_update()

    def on_deleted(self, event):
        log.debug(f'DELETED: "{event.src_path}"')
        if ".db" in event.src_path:
            log.info(f'DB Item Deleted: "Updating GitHub"')
            self.git_update()

    def on_modified(self, event):
        log.debug(f'MODIFIED: "{event.src_path}"')
        if ".db" in event.src_path:
            log.info(f'DB Item Modified: "Updating GitHub"')
            self.git_update()

    def git_update(self, msg='sync db changes'):
        repo = git.Repo(Path.cwd().joinpath('.git').as_posix())
        log.info("marking git repo...")
        time.sleep(2)

        repo.git.add('--all')
        log.info("git add -A")
        time.sleep(2)

        repo.git.commit('-m', msg, author='katayama@udel.edu')
        log.info("git commit -m")
        time.sleep(4)

        origin = repo.remote(name="main")
        origin.push()
        log.info("git push")
        time.sleep(5)



if __name__ == '__main__':
    print(Path.cwd())
    log = getLogger()

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
