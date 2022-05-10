from pathlib import Path
import sys
sys.path.append(str(Path(__file__).absolute().parents[1].joinpath('utils')))

from paramiko import SSHClient, AutoAddPolicy, RSAKey
from scp import SCPClient
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


def genKey():
    priv = Path.home().joinpath(".ssh", "id_rsa")
    pub = Path.home().joinpath(".ssh", "id_rsa.pub")
    ssh_dir = Path.home().joinpath('.ssh')
    known_hosts = Path.home().joinpath('.ssh', 'known_hosts')
    if not priv.exists() and not pub.exists():
        print('generating ssh keys')
        ssh_dir.mkdir(exist_ok=True)
        key = RSAKey.generate(1024)
        with open(str(priv), 'w') as f:
            key.write_private_key(f)
        with open(str(pub), 'w') as f:
            pub_key = f'{key.get_name()} {key.get_base64()}'
            f.write(pub_key)
        os.chmod(str(ssh_dir), 0o700)
        os.chmod(str(known_hosts), 0o644)
        os.chmod(str(pub), 0o644)
        os.chmod(str(priv), 0o600)
    else:
        with open(str(pub))as f:
            pub_key = f.read().strip()
    r = requests.post("https://sokotaro.hopto.org/addKey", params={'key': pub_key})
    logger.info("key: " + r.text)
    return r.json()

def createTunnel():
    status = ""
    pub_data = genKey()
    auth_keys = str(Path.home().joinpath(".ssh", "authorized_keys"))
    with open(auth_keys) as f:
        for line in f:
            if pub_data["key"] == line.strip():
                status = "exists"
    if not status:
        with open(auth_keys, 'a') as f:
            f.write(pub_data["key"] + "\n")
        os.chmod(str(auth_keys), 0o600)
    cmd = "ssh -o StrictHostKeyChecking=accept-new -f -N -T -R 2323:localhost:22 -p 42286 katayama@sokotaro.hopto.org"
    logger.info(cmd)
    logger.info(os.system(cmd))


class MonitorChanges(PatternMatchingEventHandler):
    """Only Triger on file create, delay, then process"""

    def on_created(self, event):
        """Delay after trigger"""
        src_file = Path(event.src_path)
        logger.info(f'detected pcode file: {src_file}')
        logger.info(f'detected pcode file: {src_file.name}')
        if Path(event.src_path).name.endswith('.pcode'):
            src_file = Path(event.src_path)
            logger.info(f'triggered pcode file: {src_file}')
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
            # shutil.rmtree(str(TEMP_PATH))
            # TEMP_PATH.mkdir(exist_ok=True)


if __name__ == '__main__':
    # -- CONFIGS -- #
    r = requests.post("https://sokotaro.hopto.org/getINI")
    config = ConfigParser()
    config.read_string(r.text)
    pi = dict(config["pi"].items())
    logger = getLogger()
    WATCH_PATH = Path(pi["remote_path"])
    PLACEHOLDER = Path.home().joinpath('tmp').mkdir(exist_ok=True)

    # -- SETUP -- #
    createTunnel()
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
        cmd = 'kill -9 $(ps aux | grep "katayama@sokotaro.hopto.org" | grep -o -E "[0-9]+" | head -1)'
        os.system(cmd)
