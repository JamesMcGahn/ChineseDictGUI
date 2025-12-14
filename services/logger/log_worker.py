import logging
import queue
import threading
import time
from logging.handlers import RotatingFileHandler

from PySide6.QtCore import QMutex, QMutexLocker, QThread, Signal, Slot

from base.enums import LOGLEVEL


class LogWorker(QThread):
    """
    Worker thread responsible for managing logging operations, including writing log messages
    to a file and emitting log signals. It handles logging asynchronously and supports log rotation.

    Attributes:
        log_queue (queue.Queue): Queue for storing log messages before writing.
        log_file_path (str): Path where log files are stored.
        log_file_name (str): Name of the log file.
        log_file_max_mbs (int): Maximum size of the log file in megabytes.
        log_backup_count (int): Number of backup log files to retain.
        log_keep_files_days (int): Number of days to retain log files.
        log_turn_off_print (bool): Flag to control whether log messages should be printed to the console.
        stop_event (bool): Flag to stop the logging thread.
        mutex (QMutex): Mutex to ensure thread-safe logging operations.
        logger (logging.Logger): Logger instance for handling log file writing.

    Signals:
        log_signal (Signal[str]): Signal emitted with log messages after they are written to the log file.
    """

    log_signal = Signal(str)

    def __init__(
        self,
        log_file_path: str,
        log_file_name: str,
        log_file_max_mbs: int,
        log_backup_count: int,
        log_keep_files_days: int,
        log_turn_off_print: bool,
    ):
        """
        Initializes the LogWorker with the provided logging parameters.

        Args:
            log_file_path (str): Path where log files are stored.
            log_file_name (str): Name of the log file.
            log_file_max_mbs (int): Maximum size of the log file in megabytes.
            log_backup_count (int): Number of backup log files to retain.
            log_keep_files_days (int): Number of days to retain log files.
            log_turn_off_print (bool): Flag to control whether log messages should be printed to the console.
        """
        super().__init__()
        self.log_queue = queue.Queue()
        self.log_file_path = log_file_path
        self.log_file_name = log_file_name
        self.log_file_max_mbs = log_file_max_mbs
        self.log_backup_count = log_backup_count
        self.log_keep_files_days = log_keep_files_days
        self.log_turn_off_print = log_turn_off_print

        self.stop_event = False
        self.mutex = QMutex()
        self.setup_logging()

    def setup_logging(self) -> None:
        """
        Sets up the logger with a rotating file handler and formatter.

        Returns:
            None: This function does not return a value.
        """
        complete_path = self.log_file_path + self.log_file_name
        self.logger = logging.getLogger(complete_path)
        self.logger.setLevel(logging.INFO)
        if not isinstance(self.log_file_max_mbs, int):
            self.log_file_max_mbs = 5
        if not isinstance(self.log_backup_count, int):
            self.log_file_max_mbs = 5

        if not self.logger.handlers:
            logfile = RotatingFileHandler(
                complete_path,
                maxBytes=self.log_file_max_mbs * 1024 * 1024,
                backupCount=self.log_backup_count,
            )
            logfile.setFormatter(
                logging.Formatter("%(asctime)s %(levelname)s %(message)s")
            )
            self.logger.addHandler(logfile)
            self.insert_log(
                (
                    LOGLEVEL.INFO,
                    f"Starting LogWorker Thread: {threading.get_ident()} - {self.thread()}",
                    True,
                )
            )

    @Slot(tuple)
    def insert_log(self, log: tuple) -> None:
        """
        Inserts a log message into the log queue for processing.

        Args:
            log (tuple): A tuple containing the log level, message, and whether to print the message.

        Returns:
            None: This function does not return a value.
        """
        level, msg, print_msg = log

        if level not in LOGLEVEL:
            level = LOGLEVEL.INFO

        if print_msg and not self.log_turn_off_print:
            print(f"{level} - {msg}")

        self.log_queue.put((level, msg))

    def run(self) -> None:
        """
        Processes the log queue and writes log messages to the file asynchronously.
        Emits a signal with the log message after it is written.

        Returns:
            None: This function does not return a value.
        """
        while not self.stop_event or not self.log_queue.empty():
            try:
                current_time_str = time.asctime(time.localtime())
                level, msg = self.log_queue.get(timeout=1)
                with QMutexLocker(self.mutex):
                    if level == LOGLEVEL.INFO:
                        self.logger.info(msg)
                    elif level == LOGLEVEL.ERROR:
                        self.logger.error(msg)
                    elif level == LOGLEVEL.WARN:
                        self.logger.warning(msg)
                    self.log_signal.emit(f"{current_time_str} - {level} - {msg}")
                self.log_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Logging error: {e}")

    def stop(self) -> None:
        """
        Stops the logging thread by setting the stop event.

        Returns:
            None: This function does not return a value.
        """
        self.stop_event = True

    def cleanup(self) -> None:
        """
        Cleans up the logger by closing all handlers.

        Returns:
            None: This function does not return a value.
        """
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)
