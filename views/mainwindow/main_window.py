import threading

from PySide6.QtCore import QSize, QTimer, Signal, Slot
from PySide6.QtGui import QAction, QCloseEvent, QFont, QFontDatabase, QIcon
from PySide6.QtWidgets import QLabel, QMainWindow, QMenu, QMessageBox, QSystemTrayIcon

import resources_rc as resources_rc
from db import DatabaseManager
from keys import keys
from services.logger import Logger
from services.network import NetworkThread, SessionManager

from ..central_widget import CentralWidget


class MainWindow(QMainWindow):
    appshutdown = Signal()

    def __init__(self, app):
        super().__init__()
        self.session_manager = SessionManager()
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

        # self.setup_session()
        self.setup_database()
        self.prompted_user_for_close = False
        print(
            f"Starting MainWindow in thread: {threading.get_ident()} - {self.thread()}"
        )
        self.logger = Logger()
        self.appshutdown.connect(self.logger.close)
        self.appshutdown.connect(self.centralwidget.notified_app_shutting)

    def setup_database(self):
        db = DatabaseManager("chineseDict.db")
        db.connect()
        db.create_tables_if_not_exist()
        db.create_anki_integration_record()
        db.disconnect()

    # def setup_session(self):
    #     if self.session_manager.load_session():
    #         return
    #     else:
    #         print("session expired, getting new session")
    #         # TODO: remove py email and password dict - use keyring
    #         # TODO: check for keyring - if it doesnt exist -> notify user -> send them to settings page

    #         self.network_thread = NetworkThread(
    #             self.session_manager,
    #             "SESSION",
    #             f"{keys['old_url']}accounts/signin",
    #             data={"email": keys["email"], "password": keys["password"]},
    #         )

    #         self.network_thread.response_sig.connect(self.session_response)
    #         self.network_thread.error_sig.connect(self.session_error)
    #         self.network_thread.start()

    def session_response(self, status, response):
        self.session_manager.save_session()

    def session_error(self, status, message):
        print(status)
        # TODO notify user - error logging them in
        print("There was an error logging you in. ")

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

        Logger().insert("Close Application Button Clicked", "INFO", True)
        result = msg.exec()
        if result == QMessageBox.Yes:

            self.prompted_user_for_close = True
            self.appshutdown.emit()
            QTimer.singleShot(1000, self.close)
        else:
            Logger().insert("Cancelled Closing Application", "INFO", True)

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handle the close event to emit the shutdown signals and ensure the application closes properly.

        Args:
            event (QCloseEvent): The close event triggered when the user attempts to close the window.

        Returns:
            None: This function does not return a value.
        """
        if self.prompted_user_for_close:
            Logger().insert("Closing Application", "INFO", True)
            event.accept()
        else:
            event.ignore()
            self.close_main_window()
