from pathlib import Path
import sys
sys.path.append(str(Path(__file__).absolute().parents[1].joinpath('utils')))

from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer
from log_handler import getLogger
from configparser import ConfigParser
from paramiko import SSHClient
from scp import SCPClient
import subprocess
import requests
import logging
import shutil
import time
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
        if ".pdf" in event.src_path:
            r = requests.post("https://sokotaro.hopto.org/getINI")
            config = ConfigParser()
            config.read_string(r.text)
            host = dict(config["macbook"].items())

            src_file = Path(event.src_path)
            logger.info(f'PDF Item Created: "SCP to Server"')
            logger.info(event)
            time.sleep(4)

            # -- 1. move pdf file to TEMP_PATH
            logger.info(f"moving {src_file.name} to {TEMP_PATH}")
            shutil.rmtree(str(TEMP_PATH))
            TEMP_PATH.mkdir(exist_ok=True)
            pdf_file = shutil.move(str(src_file), str(TEMP_PATH))

            # -- 2. run audiveris on the odf file
            OMR_RESULTS = Path(TEMP_PATH, "omr_results")
            OMR_RESULTS.mkdir(exist_ok=True)
            cmd = ["audiveris", "-batch", "-transcribe", "-export", f"{pdf_file}", "-output", f"{OMR_RESULTS}"]
            logger.info(' '.join(cmd))
            # os.system(' '.join(cmd))
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in iter(p.stdout.readline, b''):
                response = line.decode().strip()
                logger.debug(response)

            # -- 3. parse mxl and extract notes
            # os.chdir(f"{OMR_RESULTS}")
            PARSE_MXL = BASE_PATH.joinpath("utils", "parse_mxl.py")
            cmd = [str(PARSE_MXL), str(next(OMR_RESULTS.rglob("*.mxl"))), str(OMR_RESULTS)]
            logger.info(cmd)
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in iter(p.stdout.readline, b''):
                response = line.decode().strip()
                logger.debug(response)

            # -- 4. crop image drawings
            # os.chdir(f"{TEMP_PATH}")
            CROP_IMG = BASE_PATH.joinpath("utils", "extract_pdf_drawings.py")
            cmd = [str(CROP_IMG), str(pdf_file), str(TEMP_PATH)]
            logger.info(cmd)
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in iter(p.stdout.readline, b''):
                response = line.decode().strip()
                logger.debug(response)

            # -- 5. compress files to a .zip archive
            # os.chdir(f'{TEMP_PATH.parent}')
            logger.info("compressing files: systemd/ml_results.zip")
            zip_file = compress(TEMP_PATH, TEMP_PATH.parent.joinpath('ml_results.zip'))

            # -- 6. clean-up (delete all files)
            # os.chdir(f'{TEMP_PATH.parent}')
            logger.info("deleting ml files: systemd/ml_results")
            shutil.rmtree(str(TEMP_PATH))
            TEMP_PATH.mkdir(exist_ok=True)

            # -- 7. send file
            logger.info(f'Sending File: {zip_file}')
            logger.debug(f'host: {host}')
            with SSHClient() as ssh:
                ssh.load_system_host_keys()
                ssh.connect(hostname=host['ip'], port=host['port'], username=host['username'])
                with SCPClient(ssh.get_transport()) as scp:
                    scp.put(files=str(zip_file), remote_path=host['remote_path'], recursive=False)
            time.sleep(2)

            logger.info(f"Deleting File: {zip_file}")
            Path(zip_file).unlink()


if __name__ == '__main__':
    # -- GLOBALS -- #
    BASE_PATH = Path(__file__).absolute().parents[1]
    WATCH_PATH = BASE_PATH.joinpath("pdf_outgoing")
    TEMP_PATH = BASE_PATH.joinpath("systemd", "ml_results")
    logger = getLogger()

    # -- SETUP -- #
    WATCH_PATH.mkdir(exist_ok=True)
    event_handler = MonitorChanges(patterns=["*.pdf"], ignore_patterns=["*.py", "*.db"], ignore_directories=True)
    observer = Observer()
    observer.schedule(event_handler, str(WATCH_PATH), recursive=True)
    observer.daemon = True
    observer.start()

    # -- WATCHDOG -- #
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
