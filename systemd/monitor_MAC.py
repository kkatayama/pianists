from pathlib import Path
import sys
sys.path.append(str(Path(__file__).absolute().parents[1].joinpath('utils')))

from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer
from log_handler import getLogger
from configparser import ConfigParser
from pathlib import Path
import pandas as pd
import requests
import argparse
import logging
import shutil
import json
import time
import sys
import os


def compress(source: Path, destination: Path):
    base_name = destination.parent / destination.stem
    fmt = destination.suffix.replace(".", "")
    root_dir = source.parent
    base_dir = source.name
    return shutil.make_archive(str(base_name), fmt, root_dir, base_dir)


def extract(file_name: Path, destination: Path):
    shutil.unpack_archive(file_name, destination)


class MonitorChanges(PatternMatchingEventHandler):
    """Only Triger on file create, delay, then process"""

    def on_created(self, event):
        """Delay after trigger"""
        if ".zip" in event.src_path:
            src_file = Path(event.src_path)
            logger.info(f'detected zip file: {src_file}')
            time.sleep(4)

            # -- CONFIGS -- #
            r = requests.post("https://sokotaro.hopto.org/getINI")
            config = ConfigParser()
            config.read_string(r.text)
            macbook = dict(config["macbook"].items())
            server = dict(config["server"].items())
            pi = dict(config["pi"].items())
            TEMP_PATH = Path(macbook["temp_path"])

            # -- 1. move zip file to TEMP_PATH
            logger.info(f"moving {src_file.name} to {TEMP_PATH}")
            TEMP_PATH.mkdir(exist_ok=True)
            zip_file = shutil.move(src_file, TEMP_PATH)

            # -- 2. extract zip file
            logger.info(f'extracting: {zip_file}')
            extract(Path(zip_file), TEMP_PATH)
            cmd = ["ls", "-lh", "*/*"]
            logger.info(cmd)
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in iter(p.stdout.readline, b''):
                response = line.decode().strip()
                logger.debug(response)

            # -- 3. parse signature and notes
            CSV_FILE = f'{next(TEMP_PATH.rglob("*.csv"))}'
            JSON_FILE = f'{next(TEMP_PATH.rglob("*.json"))}'
            logger.info(f'parsing signature: {JSON_FILE}')
            with open(JSON_FILE) as f:
                data = json.load(f)
            temp_key = data["key_signatures"][0]
            temp_time = data["time_signatures"][0]
            key_signature = f'{temp_key["root_str"]} {temp_key["mode"]}'
            time_signature = f'{temp_time["numerator"]}/{temp_time["denominator"]}'
            logger.debug(f'key_signature: {key_signature}')
            logger.debug(f'time_signature: {time_signature}')

            logger.info(f'parsing notes: {CSV_FILE}')
            df = pd.read_csv(CSV_FILE, header=0)
            for index, note in df.iterrows():
                logger.debug(f'{note["pitch_str"]} (duration: {note["duration"]})')

            # -- 4. parse drawings and do more machine learning ...?

            # -- 5. generate p-code ...
            logger.info(f'generating p-code ...')

            # -- 6. send p-code to raspberry pi
            logger.info(f'Sending p-code File: {CSV_FILE}')
            cmd = f"rsync -v -e 'ssh -A -t -p {server['port']} {server['username']}@{server['ip']} ssh -A -t -p {udel['port']} {pi['username']}@{pi['ip']}' {str(pdf_file)} :{pi['remote_path']}/temp.pdf"
            logger.info(cmd)
            os.system(cmd)
            time.sleep(2)



if __name__ == '__main__':
    # -- CONFIGS -- #
    r = requests.post("https://sokotaro.hopto.org/getINI")
    config = ConfigParser()
    config.read_string(r.text)
    macbook = dict(config["macbook"].items())
    logger = getLogger()
    WATCH_PATH = Path(macbook["remote_path"])

    # -- SETUP -- #
    WATCH_PATH.mkdir(exist_ok=True)
    event_handler = MonitorChanges(patterns=["*.zip"], ignore_directories=True)
    observer = Observer()
    observer.schedule(event_handler, str(WATCH_PATH), recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
