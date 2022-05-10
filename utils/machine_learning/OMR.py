from pathlib import Path
from configparser import ConfigParser
import shutil


if __name__ == '__main__':
    config = ConfigParser()
    config.read(Path.home().joinpath(".pianists", "config.ini"))
