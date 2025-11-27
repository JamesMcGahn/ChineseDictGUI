import os

from PySide6.QtCore import QObject, Signal, Slot


class RemoveFileWorker(QObject):
    finished = Signal()

    def __init__(self, paths):
        super().__init__()
        self.paths = paths

    @Slot()
    def do_work(self):
        for path in self.paths:
            self.delete_file(path)
        self.finished.emit()

    def delete_file(self, file_path):
        """Deletes a file using os.remove()."""
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
            else:
                print(f"File not found: {file_path}")
        except PermissionError:
            print(f"Permission denied: {file_path}")
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
