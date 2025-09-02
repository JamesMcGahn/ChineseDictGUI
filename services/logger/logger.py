import os
import time

from PySide6.QtCore import QObject, Signal, Slot

from base import QSingleton
from models.settings import LogSettingsModel
from utils.files import PathManager

from .log_worker import LogWorker


class Logger(QObject, metaclass=QSingleton):
    """
    Logger class responsible for managing log file creation, rotation, and cleanup.
    It interacts with a background worker thread to handle logging asynchronously.

    Attributes:
        log_file_path (str): The directory path where logs are stored.
        log_file_name (str): The name of the log file.
        log_file_max_mbs (int): The maximum size of a log file in megabytes.
        log_backup_count (int): The number of backup log files to keep.
        log_keep_files_days (int): The number of days to keep old log files before deletion.
        log_turn_off_print (bool): Whether to disable printing log messages to the console.
        settings (LogSettingsModel): The settings model for managing logging configurations.
        log_worker (LogWorker): The worker thread responsible for handling log file operations.

    Signals:
        send_log (Signal[str]): Signal emitted when a log message is sent out.
        submit_log (Signal[tuple]): Signal emitted when a log entry needs to be inserted.

    """

    send_log = Signal(str)
    submit_log = Signal(tuple)

    def __init__(self):
        """
        Initialize the logger by loading settings, starting the logging thread, and cleaning up old logs.
        """
        super().__init__()
        self.log_file_path = "./logs/"
        self.log_file_name = "file.log"
        self.log_file_max_mbs = 5
        self.log_backup_count = 5
        self.log_keep_files_days = 30
        self.log_turn_off_print = False
        self.settings = LogSettingsModel()
        self.init_logging_settings()

        self.settings.log_setting_changed.connect(self.log_settings_changed)

        path = PathManager.regex_path(self.log_file_path + self.log_file_name)
        if not PathManager.path_exists(path["path"], True):
            return
            # TODO Notify user the path is bad

        self.start_logging_thread()

        # Perform initial cleanup of old logs
        self.cleanup_old_logs()

    def start_logging_thread(self) -> None:
        """
        Starts the log worker thread responsible for handling log file writing and rotation.

        Returns:
            None: This function does not return a value.
        """
        self.log_worker = LogWorker(
            self.log_file_path,
            self.log_file_name,
            self.log_file_max_mbs,
            self.log_backup_count,
            self.log_keep_files_days,
            self.log_turn_off_print,
        )
        self.log_worker.log_signal.connect(self.send_logs_out)
        self.submit_log.connect(self.log_worker.insert_log)
        self.log_worker.start()

    def init_logging_settings(self) -> None:
        """
        Initializes the logger settings from the LogSettingsModel.

        Returns:
            None: This function does not return a value.
        """
        (
            log_file_path,
            log_file_name,
            log_file_max_mbs,
            log_backup_count,
            log_keep_files_days,
            log_turn_off_print,
        ) = self.settings.get_log_settings()

        self.log_file_path = log_file_path
        self.log_file_name = log_file_name
        self.log_file_max_mbs = log_file_max_mbs
        self.log_backup_count = log_backup_count
        self.log_keep_files_days = log_keep_files_days
        self.log_turn_off_print = log_turn_off_print

    @Slot(tuple)
    def log_settings_changed(self, settings: tuple) -> None:
        """
        Slot to handle when the logging settings change. It restarts the logger to apply new settings.

        Args:
            settings (tuple): A tuple containing the new logging settings.

        Returns:
            None: This function does not return a value.
        """
        self.insert(
            "Logging settings changed. Restarting Logger to Apply Settings.", "INFO"
        )
        self.close()
        self.init_logging_settings()
        self.start_logging_thread()

    @Slot()
    def turn_off_print_msg(self, switch: bool) -> None:
        """
        Slot to turn off the printing of log messages to the console.

        Args:
            switch (bool): If True, disable printing log messages to the console.

        Returns:
            None: This function does not return a value.
        """
        self.turn_off_print = switch

    def send_logs_out(self, msg: str) -> None:
        """
        Emits the send_log signal with the given log message.

        Args:
            msg (str): The log message to be emitted.

        Returns:
            None: This function does not return a value.
        """
        self.send_log.emit(msg)

    @Slot(str, str, bool)
    def insert(self, msg: str, level: str = "INFO", print_msg: bool = True) -> None:
        """
        Inserts a log entry into the log worker.

        Args:
            msg (str): The log message to be inserted.
            level (str): The log level (e.g., "INFO", "ERROR").
            print_msg (bool): Whether to print the log message to the console.

        Returns:
            None: This function does not return a value.
        """

        self.submit_log.emit((level, msg, print_msg))

    def cleanup_old_logs(self) -> None:
        """
        Deletes log files older than the specified number of days.

        Returns:
            None: This function does not return a value.
        """
        path = PathManager.regex_path(self.log_file_path + self.log_file_name)
        log_dir = path["path"]
        if not PathManager.path_exists(log_dir, True):
            return

        # Get current time
        current_time = time.time()
        self.insert("Checking For Old Log Files to Clean Up", "INFO")
        # Iterate through log files in the directory
        for log_file in os.listdir(log_dir):
            # TODO Add Check if file is the current log --> skip
            file_path = os.path.join(log_dir, log_file)
            # Check if it's a file
            if os.path.isfile(file_path):
                # Get the file's last modification time
                file_age = current_time - os.path.getmtime(file_path)
                # Delete files older than 30 days (30 * 24 * 60 * 60 seconds)
                if not isinstance(self.log_keep_files_days, int):
                    self.log_keep_files_days = 30
                if file_age > self.log_keep_files_days * 24 * 60 * 60:
                    os.remove(file_path)
                    self.insert(f"Removing old log file {file_path}", "INFO")

    @Slot()
    def close(self) -> None:
        """
        Closes the log worker thread and shuts down logging.

        Returns:
            None: This function does not return a value.
        """
        self.insert("Shutting down logging", "INFO", True)
        self.log_worker.stop()
        self.log_worker.cleanup()
        self.log_worker.quit()
        self.log_worker.wait()
