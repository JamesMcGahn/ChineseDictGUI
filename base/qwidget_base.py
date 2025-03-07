from typing import Optional

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QWidget

from components.toasts import QToast


class QWidgetBase(QWidget):
    """
    A base class for QWidgets that provides common logging functionality and signals.

    This class can be subclassed by QWidgets to inherit common signals such as `send_logs`,
    `appshutdown`, and provides methods to log messages, display toasts, and notify application shutdown.

    Signals:
        send_logs (Signal): Signal to emit log messages (message, log level, whether to print the message).
        appshutdown (Signal): Signal emitted when application is shutting down.
    """

    send_logs = Signal(str, str, bool)
    appshutdown = Signal()

    def __init__(self):
        """Initialize the base class."""
        super().__init__()
        from services.logger import Logger

        self.logger = Logger()
        self.send_logs.connect(self.logger.insert)

    @Slot(str, str, bool)
    def logging(self, msg, level="INFO", print_msg=True) -> None:
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

    @Slot()
    def notified_app_shutting(self) -> None:
        """Emits the appshutdown signal to notify other components."""
        self.appshutdown.emit()

    @Slot()
    def log_with_toast(
        self,
        toast_title: str,
        msg: str,
        log_level: str = "INFO",
        toast_level: str = "INFO",
        print_msg: bool = True,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Logs a message with the specified log level and shows toast message.

        This method send logs to Logger with a message, log level, and
        an optional flag to print the message. It shows a toast message with parent, toast level, title and message

        Args:
            toast_title (str): Title of toast message
            msg (str): The message to be logged and displayed in toast message
            level (str, optional): The log level (e.g., "INFO", "WARN", "ERROR"). Defaults to "INFO".
            toast_level (str, optional): The log level (e.g., "SUCCESS","INFO", "WARN", "ERROR", "CLOSE"). Defaults to "INFO".
            print_msg (bool, optional): Flag to determine whether to print the log message. Defaults to True.
            parent (QWidget, optional): Parent widget for toast message. Defaults to None.
        Returns:
            None
        """
        self.logging(msg, log_level, print_msg)
        if not parent:
            parent = self
        QToast(parent, toast_level, toast_title, msg)
