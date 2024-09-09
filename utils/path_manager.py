import os
import re


class PathManager:
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
    def check_dup(folderpath, filename, ext):
        # if folder path doesnt exist - create it
        PathManager.path_exists(folderpath, True)
        # remove linux illegal characters
        if isinstance(filename, int):
            filename = str(filename)
        filename = filename.replace("/", "-").replace("\0", "")
        path = f"{folderpath}{filename}{ext}"
        # check if filename exists
        if PathManager.path_exists(path, False):
            count = 1
            newpath = f"{folderpath}{filename}-({count}){ext}"
            # if filename exists append -(count) to make unique filename
            # check to see if filename already exists - if it does increase count in filename
            while PathManager.path_exists(newpath, False):
                newpath = f"{folderpath}{filename}-({count}){ext}"
                count += 1
            path = newpath
        return path
