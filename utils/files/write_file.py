from csv import DictWriter
from os.path import join as join_path

import services.logger.logger

from .path_manager import PathManager


class WriteFile:
    @staticmethod
    def write_to_csv(path, data, overwrite=False):
        if len(data) == 0:
            return False
        match = PathManager.regex_path(path)
        if not overwrite:
            path = PathManager.check_dup(match["path"], match["filename"], match["ext"])
        else:
            PathManager.path_exists(match["path"], True)
        services.logger.logger.Logger().insert(f"Saving {path}", "INFO")
        with open(path, "w") as file:
            csv_writer = DictWriter(file, fieldnames=data[0].keys())
            csv_writer.writeheader()
            for dat in data:
                csv_writer.writerow(dat)
        return path

    @staticmethod
    def write_file(path, source, write_type="w", overwrite=False, print_to_user=True):
        services.logger.logger.Logger().insert(
            "Writing Data to File",
            "INFO",
            print_to_user,
        )
        match = PathManager.regex_path(path)
        PathManager.path_exists(match["path"], True)

        if not overwrite:
            path = PathManager.check_dup(match["path"], match["filename"], match["ext"])

        else:
            path = join_path(match["path"], match["filename"] + match["ext"])

        print(path)
        with open(path, write_type) as out:
            out.write(source)
            services.logger.logger.Logger().insert(
                f"Completed Writing {match['filename']}{match['ext']}",
                "INFO",
                print_to_user,
            )
        return path
