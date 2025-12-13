import threading

from PySide6.QtCore import QObject, Signal, Slot


class QObjectBase(QObject):
    """
    A base class for QObject that provides common logging functionality and signals.

    This class can be subclassed by QObject to inherit common signals such as `send_logs`
    and provides methods to log messages.

    Signals:
        send_logs (Signal): Signal to emit log messages (message, log level, whether to print the message).

    """

    send_logs = Signal(str, str, bool)

    def __init__(self):
        """Initialize the base class."""
        super().__init__()
        from services.logger import Logger

        self.logger = Logger()
        self.send_logs.connect(self.logger.insert)

    @Slot(str, str, bool)
    def logging(self, msg: str, level: str = "INFO", print_msg: bool = True) -> None:
        """
        Logs a message with the specified log level.

        This method send logs to Logger with a message, log level, and
        an optional flag to print the message.

        Args:
            msg (str): The message to be logged.
            level (str, optional): The log level (e.g., "INFO", "WARN", "ERROR"). Defaults to "INFO".
            print_msg (bool, optional): Flag to determine whether to print the log message. Defaults to True.

        Returns:
            None
        """
        self.send_logs.emit(msg, level, print_msg)

    def log_thread(self) -> None:
        """
        Log the thread information for the worker.

        Logs the name of the current class and the thread identifier.
        """
        self.logging(
            f"Starting {self.__class__.__name__} in thread: {threading.get_ident()} - {self.thread()}",
            "INFO",
        )
