import os
import time

from PySide6.QtCore import QObject, Signal, Slot

from base import QSingleton
from base.enums import LOGLEVEL
from services.settings.models import LogSettings
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
        self._settings_loaded = False
        self._logger_started = False
        self.logs_queue_before_start = []

        # SETTINGS Fields
        self.log_file_path = None
        self.log_file_name = None
        self.log_file_max_mbs = None
        self.log_backup_count = None
        self.log_keep_files_days = None
        self.log_level = None
        self.log_print_logs = True

    def start_up(self):
        if not self._settings_loaded:
            return
        path = PathManager.regex_path(self.log_file_path + self.log_file_name)
        if not PathManager.path_exists(path["path"], True):
            self.log_file_path = PathManager.create_folder_in_app_data("logs")
        self.cleanup_old_logs()
        self.start_logging_thread()

    def load_settings(self, settings: LogSettings):
        if self._settings_loaded:
            return
        for field in settings.get_fields_list():
            value = getattr(settings, field.name, None)
            setattr(self, field.name, value)
        self._settings_loaded = True

    def start_logging_thread(self) -> None:
        """
        Starts the log worker thread responsible for handling log file writing and rotation.

        Returns:
            None: This function does not return a value.
        """
        if self._logger_started:
            return
        self.log_worker = LogWorker(
            self.log_file_path,
            self.log_file_name,
            self.log_file_max_mbs,
            self.log_backup_count,
            self.log_keep_files_days,
            self.log_print_logs,
            self.log_level,
        )
        self.log_worker.log_signal.connect(self.send_logs_out)
        self.submit_log.connect(self.log_worker.insert_log)
        self.log_worker.started.connect(lambda: self._log_service_started(True))
        self.log_worker.started.connect(lambda: self.flush_boot_logs())
        self.log_worker.start()

    def _log_service_started(self, status: bool):
        self._logger_started = status

    @Slot(tuple)
    def log_settings_changed(self, settings: LogSettings) -> None:
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
        self._settings_loaded = False
        self.load_settings(settings)
        self.start_up()

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
    def insert(
        self, msg: str, level: str = LOGLEVEL.INFO, print_msg: bool = True
    ) -> None:
        """
        Inserts a log entry into the log worker.

        Args:
            msg (str): The log message to be inserted.
            level (LOGLEVEL): The log level (e.g., "INFO", "ERROR").
            print_msg (bool): Whether to print the log message to the console.

        Returns:
            None: This function does not return a value.
        """
        if self._log_service_started:
            self.submit_log.emit((level, msg, print_msg))
        else:
            self.logs_queue_before_start.append((level, msg, print_msg))

    def flush_boot_logs(self):
        for log in self.logs_queue_before_start:
            level, msg, print_msg = log
            self.insert(level, msg, print_msg)
        self.logs_queue_before_start.clear()

    def cleanup_old_logs(self) -> None:
        """
        Deletes log files older than the specified number of days.

        Returns:
            None: This function does not return a value.
        """
        log_dir = self.log_file_path

        if not PathManager.path_exists(log_dir, True):
            self.logs_queue_before_start.append(
                ("INFO", "log path doesnt exist", self.log_print_logs)
            )
        current_time = time.time()
        self.logs_queue_before_start.append(
            ("INFO", "Checking For Old Log Files to Clean Up", self.log_print_logs)
        )

        for log_file in os.listdir(log_dir):
            file_path = os.path.join(log_dir, log_file)
            if os.path.isfile(file_path):
                file_age = current_time - os.path.getmtime(file_path)
                # Delete files older than 30 days (30 * 24 * 60 * 60 seconds)
                if not isinstance(self.log_keep_files_days, int):
                    self.log_keep_files_days = 30
                if file_age > self.log_keep_files_days * 24 * 60 * 60:
                    os.remove(file_path)
                    self.logs_queue_before_start.append(
                        (
                            LOGLEVEL.INFO,
                            f"Removed old log file {file_path}",
                            LOGLEVEL.INFO,
                            self.log_print_logs,
                        )
                    )

    @Slot()
    def close(self) -> None:
        """
        Closes the log worker thread and shuts down logging.

        Returns:
            None: This function does not return a value.
        """
        self.insert("Shutting down logging", LOGLEVEL.INFO, True)
        self.log_worker.stop()
        self.log_worker.cleanup()
        self.log_worker.quit()
        self.log_worker.wait()
        self._log_service_started = False
