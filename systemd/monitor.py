from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer
from pathlib import Path

from paramiko import SSHClient
from scp import SCPClient
# from teddy import getLogger
# from rich import print
import logging
import shutil
import time
import sys


host = {
    "ip": "192.168.1.95",
    "port": "2222",
    "username": "katayama",
    "remote_path": "/Users/katayama/temp/incoming"
}

def progress4(filename, size, sent, peername):
    if isinstance(filename, bytes):
        filename = filename.decode()
    sys.stdout.write("(%s:%s) %s\'s progress: %.2f%%   \r" % (peername[0], peername[1], filename, float(sent)/float(size)*100))

class MonitorChanges(PatternMatchingEventHandler):
    def on_modified(self, event):
        if ".pdf" in event.src_path:
            pdf_file = Path(event.src_path)
            logging.info(f'PDF Item Modified: "SCP to Server"')
            logging.info(event)
            time.sleep(4)

            with SSHClient() as ssh:
                ssh.load_system_host_keys()
                ssh.connect(hostname=host['ip'], port=host['port'], username=host['username'])
                with SCPClient(ssh.get_transport(), progress4=progress4) as scp:
                    scp.put(files=str(pdf_file), remote_path=host['remote_path'], recursive=False)


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
