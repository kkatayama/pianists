#!/usr/bin/env python3
from configparser import ConfigParser
from pathlib import Path
import subprocess
import shutil
import sys
import git
import pip
import re
import os


# Attempt to Import Dependencies, Otherwise Install ###########################
for pkg in ["watchdog", "git", "rich", "coloredlogs", "teddy"]:
    try:
        exec(f'import {pkg}')
    except ImportError:
        if pkg == "teddy":
            pip.main(["install", "-U", "git+https://github.com/kkatayama/teddy.git@master"])
        else:
            pip.main(["install", pkg])

from rich import print
py_file = Path(__file__).parent.absolute()
pwd = py_file.parent

"""
repo = git.Repo(Path.cwd().joinpath('.git').as_posix())
repo.git.add('--all')
repo.git.commit('-m', 'commit test', author='katayama@udel.edu')
origin = repo.remote(name="main")
origin.push()
"""

# Extract Current User Info Running This Script ###############################
user = os.environ.get("USER")
wd = pwd.as_posix()
py = sys.executable
app = next(Path(pwd).rglob('server.py')).absolute().as_posix()
conf = next(Path().rglob('pianists_service.conf')).absolute().as_posix()
monitor = next(Path().rglob('monitor.py')).absolute().as_posix()

user_info = {"user": user, "wd": wd, "py": py, "app": app, "conf": conf, "monitor": monitor}
temp_dir = next(Path().rglob("temp")).absolute()

# Configure Service Daemons #####################################################
services = Path.cwd().rglob('*.service')
for service in services:
    config = ConfigParser()
    config.optionxform = str
    config.read(service)

    # -- Update Config to User's Environment
    config["Service"]["User"] = user_info["user"]
    config["Service"]["WorkingDirectory"] = user_info["wd"]

    # -- "monitor.py" doesn't use Environment Variables
    if "monitor" in service.name:
        config["Service"]["ExecStart"] = f'{user_info["py"]} {user_info["monitor"]}'
    else:
        config["Service"]["ExecStart"] = f'{user_info["py"]} {user_info["app"]}'
        config["Service"]["EnvironmentFile"] = user_info["conf"]

    # -- Export Service to temp directory
    temp_service = temp_dir.joinpath(service.name + '.tmp')
    with open(temp_service, 'w') as f:
        config.write(f)

    # -- repair format
    with open(temp_service) as ff:
        raw = ff.read()
    with open(temp_service, 'w') as f:
        f.write(raw.replace(' = ', '='))

    # -- Install Service
    cmd = f"sudo cp {temp_service} /etc/systemd/system/{service.name}"
    subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(cmd)

    cmd = f"sudo systemctl daemon-reload"
    subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(cmd)

    cmd = f"sudo systemctl enable {service.name.split('.')[0]}"
    subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(cmd)

    cmd = f"sudo systemctl start {service.name.split('.')[0]}"
    subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(cmd)
