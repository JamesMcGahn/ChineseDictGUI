import threading

from PySide6.QtCore import QSize, QThread, QTimer, Signal, Slot
from PySide6.QtGui import QAction, QCloseEvent, QFont, QFontDatabase, QIcon
from PySide6.QtWidgets import QLabel, QMainWindow, QMenu, QMessageBox, QSystemTrayIcon

from base.enums import LOGLEVEL
from context import AppContext
from keys import keys

# trunk-ignore(ruff/F401)
from resources import resources_rc
from services.logger import Logger

from ..central_widget import CentralWidget


class MainWindow(QMainWindow):
    appshutdown = Signal()
    check_token = Signal()
    send_logs = Signal(str, str, bool)

    def __init__(self, app):
        super().__init__()
        self.ctx = AppContext()

        self.app = app
        self.setWindowTitle("Custom MainWindow")
        self.setObjectName("MainWindow")
        self.resize(1286, 985)
        self.setMaximumSize(QSize(16777215, 16777215))
        font = QFont()
        font.setFamilies([".AppleSystemUIFont"])
        self.setFont(font)
        with open("./styles/main_window.css", "r") as ss:
            self.setStyleSheet(ss.read())
        self.centralwidget = CentralWidget()

        self.label = QLabel(self)
        self.setCentralWidget(self.centralwidget)

        self.prompted_user_for_close = False
        print(
            f"Starting MainWindow in thread: {threading.get_ident()} - {self.thread()}"
        )
        self.send_logs.connect(self.ctx.logging)
        self.logger = Logger()

        self.appshutdown.connect(self.logger.close)
        self.appshutdown.connect(self.centralwidget.notified_app_shutting)
        self.appshutdown.connect(self.ctx.appshutdown)

    @Slot()
    def close_main_window(self) -> None:
        """
        Slot that shows QMessageBox to ask user to confirm they want to quit the application.

        Returns:
            None: This function does not return a value.
        """
        msg = QMessageBox(self)
        msg.setWindowTitle("Confirm Shutdown")
        msg.setText("Do you want to shut down?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        msg.setDefaultButton(QMessageBox.Cancel)

        self.send_logs.emit("Close Application Button Clicked", "INFO", True)
        result = msg.exec()
        if result == QMessageBox.Yes:

            self.prompted_user_for_close = True
            self.appshutdown.emit()
            QTimer.singleShot(1000, self.close)
        else:
            self.send_logs.emit("Cancelled Closing Application", "INFO", True)

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handle the close event to emit the shutdown signals and ensure the application closes properly.

        Args:
            event (QCloseEvent): The close event triggered when the user attempts to close the window.

        Returns:
            None: This function does not return a value.
        """
        if self.prompted_user_for_close:
            self.send_logs.emit("Closing Application", LOGLEVEL.INFO, True)
            event.accept()
        else:
            event.ignore()
            self.close_main_window()
