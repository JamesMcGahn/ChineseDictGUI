import threading

from PySide6.QtCore import QObject, Signal


class QWorkerBase(QObject):
    """
    A base class for workers that provides common logging functionality and signals.

    This class can be subclassed by workers to inherit common signals such as `send_logs`,
    `finished`, and `error`, and provides methods to log messages and track thread execution.

    Signals:
        send_logs (Signal): Signal to emit log messages (message, log level, whether to print the message).
        finished (Signal): Signal emitted when the worker finishes execution.
        error (Signal): Signal emitted when an error occurs in the worker.
    """

    send_logs = Signal(str, str, bool)
    finished = Signal()
    error = Signal()

    def __init__(self):
        """Initialize the worker base class."""
        super().__init__()

    def logging(self, msg, level="INFO", print_msg=True) -> None:
        """
        Emit a log message.

        Args:
            msg (str): The message to log.
            level (str): The log level (e.g., "INFO","WARN", "ERROR"). Defaults to "INFO".
            print_msg (bool): Whether to print the message. Defaults to True.
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
