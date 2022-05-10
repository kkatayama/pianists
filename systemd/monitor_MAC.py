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
import pandas as pd
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
    cmd = "ssh -o StrictHostKeyChecking=accept-new -f -N -T -R localhost:2222:localhost:22 -p 42286 katayama@sokotaro.hopto.org"
    logger.info(cmd)
    logger.info(os.system(cmd))



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
            shutil.rmtree(str(TEMP_PATH))
            TEMP_PATH.mkdir(exist_ok=True)
            zip_file = shutil.move(str(src_file), str(TEMP_PATH))

            # -- 2. extract zip file
            logger.info(f'extracting: {zip_file}')
            extract(Path(zip_file), TEMP_PATH)
            cmd = ["ls", f'{TEMP_PATH}']
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
            try:
                temp_key = data["key_signatures"][0]
                key_signature = f'{temp_key["root_str"]} {temp_key["mode"]}'
                logger.debug(f'key_signature: {key_signature}')
            except Exception:
                pass

            try:
                temp_time = data["time_signatures"][0]
                time_signature = f'{temp_time["numerator"]}/{temp_time["denominator"]}'
                logger.debug(f'time_signature: {time_signature}')
            except Exception:
                pass

            logger.info(f'parsing notes: {CSV_FILE}')
            df = pd.read_csv(str(CSV_FILE), header=0)
            for index, note in df.iterrows():
                logger.debug(f'{note["pitch_str"]} (duration: {note["duration"]})')



            ###################################################################
            #                          NEED TO EDIT                           #
            ###################################################################

            # -- 4. parse drawings and do more machine learning ...?

            # -- 5. generate p-code ...
            logger.info(f'generating p-code ...')
            PCODE_FILE = str(CSV_FILE).replace('.csv', '.pcode')

            # -- 6. send p-code to raspberry pi
            logger.info(f'Sending p-code File: {PCODE_FILE}')
            cmd = f"rsync -v -e 'ssh -A -t -p {server['port']} {server['username']}@{server['ip']} ssh -A -t -p {pi['port']} {pi['username']}@{pi['ip']}' {PCODE_FILE} :{pi['remote_path']}/{PCODE_FILE.name}"
            logger.info(cmd)
            os.system(cmd)
            time.sleep(2)

            # -- 7. clean-up (delete all files)
            # os.chdir(f'{TEMP_PATH.parent}')
            logger.info(f"deleting ml files: {TEMP_PATH}")
            shutil.rmtree(str(TEMP_PATH))
            TEMP_PATH.mkdir(exist_ok=True)
            shutil.rmtree(str(WATCH_PATH))
            WATCH_PATH.mkdir(exist_ok=True)


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
    shutil.rmtree(str(WATCH_PATH))
    WATCH_PATH.mkdir(exist_ok=True)

    event_handler = MonitorChanges(patterns=["*.zip"], ignore_patterns="", ignore_directories=True)
    observer = Observer()
    observer.schedule(event_handler, str(WATCH_PATH), recursive=False)
    # observer.daemon = True
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
