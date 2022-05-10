from pathlib import Path
import sys
sys.path.append(str(Path(__file__).absolute().parents[1].joinpath('utils')))

from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer
from log_handler import getLogger
from configparser import ConfigParser
import pandas as pd
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
            TEMP_PATH.mkdir(exist_ok=True)
            pcode_file = shutil.move(src_file, TEMP_PATH)

            ###################################################################
            #                           NEED TO EDIT                          #
            ###################################################################

            # -- 2. parse pcode file
            logger.info(f'parsing pcode file: {CSV_FILE}')
            df = pd.read_csv(pcode_file, header=0)
            for index, note in df.iterrows():
                logger.debug(f'{note["pitch_str"]} (duration: {note["duration"]})')

            # -- 3. send pcode instructions ... ?


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
    event_handler = MonitorChanges(patterns=["*.pcode"], ignore_directories=True)
    observer = Observer()
    observer.schedule(event_handler, str(WATCH_PATH), recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
