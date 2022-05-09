from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer
from configparser import ConfigParser
from paramiko import SSHClient
from scp import SCPClient
from pathlib import Path
import subprocess
# from teddy import getLogger
# from rich import print
import logging
import shutil
import time
import sys


config = ConfigParser()
config.read(Path(Path.cwd(), "systemd", "hosts.ini"))
host = dict(config["macbook"].items())
WATCH_PATH = Path.cwd().joinpath("pdf_outgoing")
TEMP_PATH = Path.cwd().joinpath("systemd", "temp_files")


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
            src_file = Path(event.src_path)
            logging.info(f'PDF Item Created: "SCP to Server"')
            logging.info(event)
            time.sleep(4)

            # -- 1. move pdf file to TEMP_PATH
            TEMP_PATH.mkdir(exist_ok=True)
            pdf_file = shutil.move(src_file, TEMP_PATH)

            # -- 2. run audiveris on the odf file
            OMR_RESULTS = Path(TEMP_PATH, "omr_results")
            OMR_RESULTS.mkdir(exist_ok=True)
            cmd = ["audiveris", "-batch", "-transcribe", "-export", f"{pdf_file}", "-output", f"{OMR_RESULTS}"]
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in iter(p.stdout.readline, b''):
                response = line.decode().strip()
                logging.info(response)

            # -- 3. parse mxl and extract notes
            os.chdir(f"{OMR_RESULTS}")
            BASE_PATH = Path.cwd()
            PARSE_MXL = "/usr/local/bin/parse_mxl"
            cmd = [PARSE_MXL, f'{next(OMR_RESULTS.rglob("*.mxl")).relative_to(OMR_RESULTS)}']
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in iter(p.stdout.readline, b''):
                response = line.decode().strip()
                logging.info(response)

            # -- 4. crop image drawings
            os.chdir(f"{TEMP_PATH}")
            CROP_IMG = "/usr/local/bin/pdf_drawings_png"
            cmd = [CROP_IMG, f'{pdf_file}']
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in iter(p.stdout.readline, b''):
                response = line.decode().strip()
                logging.info(response)

            # -- 5. compress files to a .zip archive
            os.chdir(f'{TEMP_PATH.parent}')
            zip_file = compress(TEMP_PATH, Path.cwd().joinpath('sheet_music.zip'))

            # -- 6. clean-up (delete all files)
            os.chdir(f'{TEMP_PATH.parent}')
            zip_file = compress(TEMP_PATH, Path.cwd().joinpath('sheet_music.zip'))

            # -- 7. send file
            logging.info(f'Sending File: {zip_file}')
            with SSHClient() as ssh:
                ssh.load_system_host_keys()
                logging.info(ssh.connect(hostname=host['ip'], port=host['port'], username=host['username']))
                with SCPClient(ssh.get_transport()) as scp:
                    logging.info(scp.put(files=str(zip_file), remote_path=host['remote_path'], recursive=False))
            time.sleep(2)

            logging.info(f"Deleting File: {zip_file}")
            zip_file.unlink()


if __name__ == '__main__':
    WATCH_PATH.mkdir(exist_ok=True)
    logging.basicConfig(level=logging.INFO)
    event_handler = MonitorChanges(patterns=["*.pdf"], ignore_patterns=["*.py", "*.db"], ignore_directories=True)
    observer = Observer()
    # -- observer.daemon=True
    observer.schedule(event_handler, str(WATCH_PATH), recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
