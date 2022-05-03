from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer
from configparser import ConfigParser
from paramiko import SSHClient
from scp import SCPClient
from pathlib import Path
# from teddy import getLogger
# from rich import print
import logging
import shutil
import time
import sys
import os


config = ConfigParser()
config.read(Path(Path.cwd(), "systemd", "hosts.ini"))
server = dict(config["server"].items())
udel = dict(config["udel"].items())

monitor_folder = str(Path("~").expanduser().joinpath('temp/incoming'))
class MonitorChanges(PatternMatchingEventHandler):
    def on_created(self, event):
        if ".pdf" in event.src_path:
            pdf_file = Path(event.src_path)
            logging.info(f'PDF Item Created: "SCP to Server"')
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
    print(Path.cwd())
    print(monitor_folder)
    # log = getLogger()
    logging.basicConfig(level=logging.INFO)

    event_handler = MonitorChanges(patterns=["*.pdf"], ignore_patterns=["*.py", "*.db"], ignore_directories=True)
    observer = Observer()
    # -- observer.daemon=True
    observer.schedule(event_handler, monitor_folder, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
