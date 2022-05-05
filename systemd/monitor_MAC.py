from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer
from configparser import ConfigParser
from paramiko import SSHClient
from scp import SCPClient
from pathlib import Path
# from teddy import getLogger
# from rich import print
import argparse
import logging
import shutil
import time
import sys
import os


# -- CONFIGS -- #
config = ConfigParser()
config.read(Path(Path.cwd(), "systemd", "hosts.ini"))
server = dict(config["server"].items())
udel = dict(config["udel"].items())


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
            pdf_file = Path(event.src_path)
            logging.info('PDF Item Created: "SCP to Server"')
            logging.info(event)
            time.sleep(4)

            logging.info(f'Sending File: {pdf_file}')
            cmd = f"rsync -v -e 'ssh -A -t -p {server['port']} {server['username']}@{server['ip']} ssh -A -t -p {udel['port']} {udel['username']}@{udel['ip']}' {str(pdf_file)} :{udel['remote_path']}/temp.pdf"
            logging.info(cmd)
            os.system(cmd)
            time.sleep(2)

            logging.info(f"Deleting File: {pdf_file}")
            pdf_file.unlink()


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("watch_path", help="the path of the folder being monitored")
    args = ap.parse_args()

    print(Path.cwd())
    # log = getLogger()
    logging.basicConfig(level=logging.INFO)

    event_handler = MonitorChanges(patterns=["*.zip"], ignore_directories=True)
    observer = Observer()
    # -- observer.daemon=True
    observer.schedule(event_handler, args.watch_path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
