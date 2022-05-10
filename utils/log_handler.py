from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
import coloredlogs
import logging
import os


MODULE = coloredlogs.find_program_name()
LOG_PATH = Path(__file__).parents[1].joinpath("logs")
LOG_FILE = str(LOG_PATH.joinpath(Path(MODULE).stem)) + '.log'
field_styles = {
    'asctime': {'color': 221, 'bright': True},
    'programname': {'color': 45, 'faint': True},
    'funcName': {'color': 177, 'normal': True},
    'lineno': {'color': 'cyan', 'bright': True}
}
level_styles = {
    "debug": {'color': 'green', 'bright': True},
    "info": {'color': 'white', 'bright': True},
    "warning": {'color': "yellow", 'normal': True},
    "error": {'color': "red", 'bright': True},
    "critical": {'color': 'red', 'bold': True, 'background': 'red'}
}
log_format = "%(asctime)s: [%(programname)s: %(funcName)s();%(lineno)s] %(message)s"


def getFileHandler():
    Path(LOG_FILE).touch()
    log_file_formatter = coloredlogs.ColoredFormatter(log_format, field_styles=field_styles, level_styles=level_styles)
    log_file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')
    log_file_handler.addFilter(coloredlogs.ProgramNameFilter())
    log_file_handler.setFormatter(log_file_formatter)
    return log_file_handler


def getLogger():
    # -- CREATE LOGGER -- #
    logger = logging.getLogger(MODULE)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(getFileHandler())
    coloredlogs.install(level='DEBUG', fmt=log_format, field_styles=field_styles, level_styles=level_styles)
    return logger

