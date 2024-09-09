from csv import DictWriter

import services.logger
from utils import PathManager


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
        services.logger.Logger().insert(f"Saving {path}", "INFO")
        with open(path, "w") as file:
            csv_writer = DictWriter(file, fieldnames=data[0].keys())
            csv_writer.writeheader()
            for dat in data:
                csv_writer.writerow(dat)
        return path

    @staticmethod
    def write_file(path, source, write_type="w", overwrite=False, print_to_user=True):
        services.logger.Logger().insert(
            "Writing Data to File",
            "INFO",
            print_to_user,
        )
        match = PathManager.regex_path(path)
        if not overwrite:
            path = PathManager.check_dup(match["path"], match["filename"], match["ext"])
        else:
            PathManager.path_exists(match["path"], True)
        with open(path, write_type) as out:
            out.write(source)
            services.logger.Logger().insert(
                f"Completed Writing {match['filename']}{match['ext']}",
                "INFO",
                print_to_user,
            )
        return path
