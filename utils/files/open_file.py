import pickle
from csv import DictReader

import services.logger.logger

from .path_manager import PathManager


class OpenFile:
    def open_pickle(path):
        if PathManager.path_exists(path, makepath=False, raiseError=True):
            with open(path, "rb") as infile:
                dill = pickle.load(infile)
            return dill

    @staticmethod
    def open_file(filepath, csv=False, split=False):
        log = services.logger.logger.Logger()
        log.insert(f"Opening {filepath}", "INFO")
        if PathManager.path_exists(filepath, makepath=False, raiseError=True):
            with open(filepath, "r", encoding="utf-8-sig") as file:
                if csv:
                    csv_reader = DictReader(file)
                    return list(csv_reader)
                elif split:
                    data = file.read().split(split)
                    log.insert(f"List: {data}", "INFO")
                    return data
                else:
                    return file
