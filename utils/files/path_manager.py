import os
import platform
import re


class PathManager:
    @staticmethod
    def path_exists(path, makepath, raiseError=False):
        if os.path.exists(path):
            return True
        elif not os.path.exists(path) and makepath:
            os.makedirs(path)
            return True
        else:
            if raiseError:
                import services.logger

                log = services.Logger()
                log.insert("Filepath does not exist", "WARN")
                raise ValueError("Filepath does not exist")
            else:
                return False

    @staticmethod
    def regex_path(path):
        directory = os.path.dirname(path)
        filename = os.path.basename(path)
        name, ext = os.path.splitext(filename)

        return {"path": os.path.normpath(directory), "filename": name, "ext": ext}

    @staticmethod
    def check_dup(folderpath, filename, ext):
        # if folder path doesnt exist - create it
        PathManager.path_exists(folderpath, True)
        # remove linux illegal characters
        if isinstance(filename, int):
            filename = str(filename)
        filename = filename.replace("/", "-").replace("\0", "")
        path = os.path.join(folderpath, f"{filename}{ext}")
        # check if filename exists
        if PathManager.path_exists(path, False):
            count = 1
            newpath = os.path.join(folderpath, f"{filename}-({count}){ext}")
            # if filename exists append -(count) to make unique filename
            # check to see if filename already exists - if it does increase count in filename
            while PathManager.path_exists(newpath, False):
                newpath = os.path.join(folderpath, f"{filename}-({count}){ext}")
                count += 1
            path = newpath
        return path

    @staticmethod
    def create_folder_in_app_data(folder_name):
        app_name = "ChineseDictGUI"

        system = platform.system()
        if system == "Darwin":
            base = os.path.expanduser("~/Library/Application Support")
        elif system == "Windows":
            base = os.environ["LOCALAPPDATA"]
        else:
            base = os.path.expanduser("~/.local/share")

        cache_dir = os.path.join(base, app_name, folder_name)
        os.makedirs(cache_dir, exist_ok=True)
        return cache_dir
