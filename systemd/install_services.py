#!/usr/bin/env python3
from configparser import ConfigParser
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from pathlib import Path
import subprocess
import plistlib
import shutil
import sys
import pip
import os


# Attempt to Import Dependencies, Otherwise Install ###########################
for pkg in ["watchdog", "git", "rich", "paramiko", "scp", "coloredlogs"]:
    try:
        exec(f'import {pkg}')
    except ImportError:
        pip.main(["install", "-U", pkg])

from rich import print
py_file = Path(__file__)
pwd = py_file.parent.parent


def installLinuxDaemon():
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



def installMacDaemon():
    # Extract Current User Info Running This Script ###############################
    c = Console()
    py_file = Path.cwd().joinpath("install_daemon_and_watchdog_LINUX.py")

    text = Text.assemble(
        ("Configure Setup: ", "magenta"),
        ("(press enter to select default value)", "green"),
        justify="center",
    )
    c.print(Panel(text, width=80))

    # default = os.environ.get("USER")
    # USER = Prompt.ask("[yellow]USER[/]", default=default)
    UID = os.getuid()

    default = "com.pianists.watchdog"
    SERVICE_NAME = Prompt.ask("[yellow]SERVICE_NAME[/]", default=default)

    default = str(Path.home().joinpath("temp", "incoming_sheet_music"))
    WATCH_PATH = Prompt.ask("[yellow]WATCH_PATH[/]", default=default)
    Path(WATCH_PATH).mkdir(exist_ok=True)

    default = sys.executable
    PYTHON_EXE = Prompt.ask("[yellow]PYTHON_EXE[/]", default=default)

    default = str(py_file.parent.joinpath("monitor_MAC.py"))
    WATCH_DOG = Prompt.ask("[yellow]WATCH_DOG[/]", default=default)

    default = str(py_file.parent.parent.joinpath("utils", "machine_learning", "OMR.py"))
    ML_SCRIPT = Prompt.ask("[yellow]ML_SCRIPT[/]", default=default)

    WORK_DIR = str(Path(ML_SCRIPT).parent)
    print("\n")

    plist = dict(
        Label=SERVICE_NAME,
        ProgramArguments=[PYTHON_EXE, WATCH_DOG, WATCH_PATH],
        WorkingDirector=WORK_DIR,
        RunAtLoad=True,
        ProcessType="LowPriorityBackgroundIO",
    )

    print("\nExporting LaunchAgent Daemon!")
    print(plistlib.dumps(plist).decode())
    SERVICE_PATH = str(Path.home().joinpath("Library", "LaunchAgents", f"{SERVICE_NAME}"))
    with open(f"{SERVICE_PATH}.plist", 'w') as f:
        plistlib.dump(plist, f)

    cmd = f"launchctl bootstrap gui/{UID} {SERVICE_PATH}.plist"
    subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(cmd)

    cmd = f"launchctl kickstart -kp gui/{UID}/{SERVICE_NAME}"
    subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(cmd)


if __name__ =='__main__':
    if sys.platform == 'linux':
        installLinuxDaemon()
    elif sys.platform == 'darwin':
        installMacDaemon()
