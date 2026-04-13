from typing import Tuple

from PySide6.QtCore import QObject, Signal, Slot

from base import QSingleton
from services.settings import AppSettings


# TODO: REMOVE MODEL class -> move to settings service
class LogSettingsModel(QObject, metaclass=QSingleton):
    """
    Manages the log settings for the application, handling initialization, saving,
    and emitting changes when log settings are updated.

    Attributes:
        log_file_path (str): The file path for storing logs.
        log_file_name (str): The name of the log file.
        log_file_max_mbs (int): Maximum size of a log file in megabytes.
        log_backup_count (int): Number of backup log files to retain.
        log_keep_files_days (int): Number of days to keep log files.
        log_turn_off_print (bool): Whether to disable printing logs to the console.
        settings (AppSettings): An instance of AppSettings to persist and retrieve log settings.

    Signals:
        log_setting_changed (Signal): Emitted when log settings are successfully updated.
        success (Signal): Emitted after log settings are saved successfully.
    """

    log_setting_changed = Signal(str, str, int, int, int, bool, str)
    success = Signal()

    def __init__(self):
        """
        Initializes the LogSettingsModel with default values and loads saved settings.
        Loads log configuration from persistent storage if available; otherwise,
        uses the default values.
        """
        super().__init__()
        self.log_file_path = "./logs/"
        self.log_file_name = "file.log"
        self.log_file_max_mbs = 5
        self.log_backup_count = 5
        self.log_keep_files_days = 30
        self.log_turn_off_print = False
        self.log_level = "INFO"

        self.settings = AppSettings()
        self.init_logs_settings()

    def get_log_settings(self) -> Tuple[str, str, int, int, int, bool, str]:
        """
        Retrieves the current log settings as a tuple.

        Returns:
            Tuple: Contains log_file_path, log_file_name, log_file_max_mbs,
                   log_backup_count, log_keep_files_days, and log_turn_off_print.
        """
        return (
            self.log_file_path,
            self.log_file_name,
            self.log_file_max_mbs,
            self.log_backup_count,
            self.log_keep_files_days,
            self.log_turn_off_print,
            self.log_level,
        )

    @Slot(str, str, int, int, int, bool, str)
    def save_log_settings(
        self,
        log_file_path: str,
        log_file_name: str,
        log_file_max_mbs: int,
        log_backup_count: int,
        log_keep_files_days: int,
        log_turn_off_print: bool,
        log_level: str,
    ):
        """
        Saves the provided log settings to persistent storage and updates the model's state.
        Emits log_setting_changed signal when settings are modified and success signal
        once the save operation is complete.

        Args:
            log_file_path (str): The file path for storing logs.
            log_file_name (str): The name of the log file.
            log_file_max_mbs (int): Maximum size of a log file in megabytes.
            log_backup_count (int): Number of backup log files to retain.
            log_keep_files_days (int): Number of days to keep log files.
            log_turn_off_print (bool): Whether to disable printing logs to the console.

        Returns:
            None: This function does not return a value.
        """
        self.log_file_path = log_file_path
        self.log_file_name = log_file_name
        self.log_file_max_mbs = log_file_max_mbs
        self.log_backup_count = log_backup_count
        self.log_keep_files_days = log_keep_files_days
        self.log_turn_off_print = log_turn_off_print
        self.log_level = log_level

        self.settings.begin_group("settings")
        self.settings.set_value("log_settings/log_file_path", log_file_path)
        self.settings.set_value("log_settings/log_file_name", log_file_name)
        self.settings.set_value("log_settings/log_backup_count", log_backup_count)
        self.settings.set_value("log_settings/log_file_max_mbs", log_file_max_mbs)
        self.settings.set_value("log_settings/log_keep_files_days", log_keep_files_days)
        self.settings.set_value("log_settings/log_turn_off_print", log_turn_off_print)
        self.settings.set_value("log_settings/log_level", log_level)
        self.settings.end_group()

        self.log_setting_changed.emit(
            log_file_path,
            log_file_name,
            log_file_max_mbs,
            log_backup_count,
            log_keep_files_days,
            log_turn_off_print,
            log_level,
        )
        self.success.emit()

    def init_logs_settings(self) -> None:
        """
        Initializes log settings by retrieving values from persistent storage.
        If no settings are found, defaults are used. This method ensures that
        the log settings are loaded at startup.
        """
        default_log_file_path = "./logs/"
        default_log_file_name = "file.log"
        default_backup_count = 5
        default_file_max_mbs = 5
        default_keep_files_days = 30
        default_turn_off_print = False
        default_log_level = "INFO"

        settings = [
            ("log_file_path", self.log_file_path, default_log_file_path),
            ("log_file_name", self.log_file_name, default_log_file_name),
            ("log_backup_count", self.log_backup_count, default_backup_count),
            ("log_file_max_mbs", self.log_file_max_mbs, default_file_max_mbs),
            ("log_keep_files_days", self.log_keep_files_days, default_keep_files_days),
            ("log_turn_off_print", self.log_turn_off_print, default_turn_off_print),
            ("log_level", self.log_level, default_log_level),
        ]
        self.settings.begin_group("settings")
        for setting in settings:
            key, self_setting, default = setting
            verified = self.settings.get_value(f"log_settings/{key}-verified", False)
            # trunk-ignore(ruff/F841)
            value = (
                self.settings.get_value(f"log_settings/{key}", default)
                if verified
                else default
            )
            setattr(self, key, value)
        self.settings.end_group()
        self.log_file_path = (
            "./logs/" if self.log_file_path == "/" else self.log_file_path
        )
        self.log_file_name = (
            "file.log" if not self.log_file_path else self.log_file_name
        )
        self.log_turn_off_print = bool(self.log_turn_off_print)
        print(
            ("log_file_path", self.log_file_path, default_log_file_path),
            ("log_file_name", self.log_file_name, default_log_file_name),
            ("log_backup_count", self.log_backup_count, default_backup_count),
            ("log_file_max_mbs", self.log_file_max_mbs, default_file_max_mbs),
            ("log_keep_files_days", self.log_keep_files_days, default_keep_files_days),
            ("log_turn_off_print", self.log_turn_off_print, default_turn_off_print),
            ("log_level", self.log_level, default_log_level),
        )
