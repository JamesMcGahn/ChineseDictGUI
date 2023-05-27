import os
import re
from csv import DictWriter

import logger


class WriteFile:
    @staticmethod
    def path_exists(path, makepath):
        if os.path.exists(path):
            return True
        elif not os.path.exists(path) and makepath:
            os.makedirs(path)
            return True
        else:
            return False

    @staticmethod
    def check_dup(folderpath, filename, ext):
        # if folder path doesnt exist - create it
        WriteFile.path_exists(folderpath, True)
        # remove linux illegal characters
        if isinstance(filename, int):
            filename = str(filename)
        filename = filename.replace("/", "-").replace("\0", "")
        path = f"{folderpath}{filename}{ext}"
        # check if filename exists
        if WriteFile.path_exists(path, False):
            count = 1
            newpath = f"{folderpath}{filename}-({count}){ext}"
            # if filename exists append -(count) to make unique filename
            # check to see if filename already exists - if it does increase count in filename
            while WriteFile.path_exists(newpath, False):
                newpath = f"{folderpath}{filename}-({count}){ext}"
                count += 1
            path = newpath
        return path

    @staticmethod
    def write_to_csv(path, data, overwrite=False):
        if len(data) == 0:
            return False
        match = WriteFile.regex_path(path)
        if not overwrite:
            path = WriteFile.check_dup(match["path"], match["filename"], match["ext"])
        else:
            WriteFile.path_exists(match["path"], True)
        logger.Logger().insert(f"Saving {path}", "INFO")
        with open(path, "w") as file:
            csv_writer = DictWriter(file, fieldnames=data[0].keys())
            csv_writer.writeheader()
            for dat in data:
                csv_writer.writerow(dat)
        return path

    @staticmethod
    def regex_path(path):
        path_reg = re.compile(
            r"^(?P<path>(\.*[\/[\d\w\s-]+\/]*)|\.+\/)(?P<filename>[\d\w\s-]*)(?P<ext>\.[\w]+)$"
        )
        matches = path_reg.search(path)
        return {
            "path": matches.group("path"),
            "filename": matches.group("filename"),
            "ext": matches.group("ext"),
        }

    @staticmethod
    def write_file(path, source, write_type="w", overwrite=False, print_to_user=True):
        logger.Logger().insert(
            "Writing Data to File",
            "INFO",
            print_to_user,
        )
        match = WriteFile.regex_path(path)
        if not overwrite:
            path = WriteFile.check_dup(match["path"], match["filename"], match["ext"])
        else:
            WriteFile.path_exists(match["path"], True)
        with open(path, write_type) as out:
            out.write(source)
            logger.Logger().insert(
                f"Completed Writing {match['filename']}{match['ext']}",
                "INFO",
                print_to_user,
            )
        return path
