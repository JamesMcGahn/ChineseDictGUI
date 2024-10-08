import logging

from utils import Singleton
from utils.files import PathManager


class Logger(Singleton):
    def __init__(self, filename="./logs/file.log"):
        self.filename = filename
        self.format = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    def insert(self, msg, level="INFO", print_msg=True):
        path = PathManager.regex_path(self.filename)
        if not PathManager.path_exists(path["path"], True):
            return
        logfile = logging.FileHandler(self.filename)
        logfile.setFormatter(self.format)
        log = logging.getLogger(self.filename)
        log.setLevel(level)
        if print_msg:
            print(msg)
        if not log.handlers:
            log.addHandler(logfile)
            if level == "INFO":
                log.info(msg)
            if level == "ERROR":
                log.error(msg)
            if level == "WARNING":
                log.warning(msg)

        logfile.close()
        log.removeHandler(logfile)
