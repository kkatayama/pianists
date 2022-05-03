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


config = ConfigParser()
config.read(Path.cwd().joinpath("hosts.ini"))
host = dict(config["macbook"].items())
# host = {
#     "ip": "192.168.1.95",
#     "port": 22,
#     "username": "katayama",
#     "remote_path": "/Users/katayama/temp/incoming"
# }

class MonitorChanges(PatternMatchingEventHandler):
    def on_created(self, event):
        if ".pdf" in event.src_path:
            pdf_file = Path(event.src_path)
            logging.info(f'PDF Item Created: "SCP to Server"')
            logging.info(event)
            time.sleep(4)

            logging.info(f'Sending File: {pdf_file}')
            with SSHClient() as ssh:
                ssh.load_system_host_keys()
                logging.info(ssh.connect(hostname=host['ip'], port=host['port'], username=host['username']))
                with SCPClient(ssh.get_transport()) as scp:
                    logging.info(scp.put(files=str(pdf_file), remote_path=host['remote_path'], recursive=False))
            time.sleep(2)

            logging.info(f"Deleting File: {pdf_file}")
            pdf_file.unlink()


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
