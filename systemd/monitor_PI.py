from pathlib import Path
import sys
sys.path.append(str(Path(__file__).absolute().parents[1].joinpath('utils')))

from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer
from log_handler import getLogger
from configparser import ConfigParser
import subprocess
import requests
import shutil
import json
import time
import os


class MonitorChanges(PatternMatchingEventHandler):
    """Only Triger on file create, delay, then process"""

    def on_created(self, event):
        """Delay after trigger"""
        if ".pcode" in event.src_path:
            src_file = Path(event.src_path)
            logger.info(f'detected pcode file: {src_file}')
            time.sleep(4)

            # -- CONFIGS -- #
            r = requests.post("https://sokotaro.hopto.org/getINI")
            config = ConfigParser()
            config.read_string(r.text)
            macbook = dict(config["macbook"].items())
            server = dict(config["server"].items())
            pi = dict(config["pi"].items())
            TEMP_PATH = Path(pi["temp_path"])

            # -- 1. move pcode file to TEMP_PATH
            logger.info(f"moving {src_file.name} to {TEMP_PATH}")
            shutil.rmtree(str(TEMP_PATH))
            TEMP_PATH.mkdir(exist_ok=True)
            pcode_file = shutil.move(str(src_file), str(TEMP_PATH))

            ###################################################################
            #                           NEED TO EDIT                          #
            ###################################################################

            # -- 2. parse pcode file
            logger.info(f'parsing pcode file: {pcode_file}')
            with open(pcode_file) as f:
                data = f.read()
            logger.debug(data)

            # -- 3. send pcode instructions ... ?

            # -- 4. cleanup
            shutil.rmtree(str(TEMP_PATH))
            TEMP_PATH.mkdir(exist_ok=True)
            shutil.rmtree(str(WATCH_PATH))
            WATCH_PATH.mkdir(exist_ok=True)


if __name__ == '__main__':
    # -- CONFIGS -- #
    r = requests.post("https://sokotaro.hopto.org/getINI")
    config = ConfigParser()
    config.read_string(r.text)
    pi = dict(config["pi"].items())
    logger = getLogger()
    WATCH_PATH = Path(pi["remote_path"])

    # -- SETUP -- #
    WATCH_PATH.mkdir(exist_ok=True)
    shutil.rmtree(str(WATCH_PATH))
    WATCH_PATH.mkdir(exist_ok=True)
    event_handler = MonitorChanges(patterns=["*.pcode"], ignore_patterns="", ignore_directories=True)
    observer = Observer()
    observer.schedule(event_handler, str(WATCH_PATH), recursive=True)
    # observer.daemon = True
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
