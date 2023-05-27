import os
import pickle
from csv import DictReader

from logger import Logger


class OpenFile:
    @staticmethod
    def check_file(filepath):
        if os.path.exists(filepath):
            return True
        else:
            Logger().insert("Filepath does not exist", "WARN")
            raise ValueError("Filepath does not exist")

    def open_pickle(path):
        if OpenFile.check_file(path):
            with open(path, "rb") as infile:
                dill = pickle.load(infile)
            return dill

    @staticmethod
    def open_file(filepath, csv=False, split=False):
        Logger().insert(f"Opening {filepath}", "INFO")
        if OpenFile.check_file(filepath):
            with open(filepath, "r", encoding="utf-8-sig") as file:
                if csv:
                    csv_reader = DictReader(file)
                    return list(csv_reader)
                elif split:
                    data = file.read().split(split)
                    Logger().insert(f"List: {data}", "INFO")
                    return data
                else:
                    return file
