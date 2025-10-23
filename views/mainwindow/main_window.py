import threading
import time

import jwt
from PySide6.QtCore import QSize, QTimer, Signal, Slot
from PySide6.QtGui import QAction, QCloseEvent, QFont, QFontDatabase, QIcon
from PySide6.QtWidgets import QLabel, QMainWindow, QMenu, QMessageBox, QSystemTrayIcon

import resources_rc as resources_rc
from core.scrapers.cpod import GetTokenThread
from db import DatabaseManager
from keys import keys
from services.logger import Logger
from services.network import NetworkThread, SessionManager
from services.settings import AppSettings

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
        self.settings = AppSettings()
        self.appshutdown.connect(self.logger.close)
        self.appshutdown.connect(self.centralwidget.notified_app_shutting)
        self.check_token()

    def setup_database(self):
        db = DatabaseManager("chineseDict.db")
        db.connect()
        db.create_tables_if_not_exist()
        db.create_anki_integration_record()
        db.disconnect()

    def check_token(self):
        token = self.settings.get_value("cpod_token")
        print("TOKEN FROM SETTINGS", token)
        if token:
            try:
                token = (
                    token.split("Bearer ")[1] if token.startswith("Bearer ") else token
                )
                decoded = jwt.decode(token, options={"verify_signature": False})
                expire_timestamp = decoded.get("exp")
                now_timestamp = int(time.time())
                time_left = expire_timestamp - now_timestamp
                if time_left <= 3600:
                    self.settings.set_value("cpod_token", None)
                    self.logger.insert(
                        "Cpod token going to expire. Trying to get a new token"
                    )
                    self.get_token()
                else:
                    minutes_left = time_left // 60
                    hours_left = minutes_left // 60
                    self.logger.insert(f"Token still valid for {hours_left} hours.")
                    fetch_new_token = max((minutes_left - 60) * 60000, 0)
                    QTimer.singleShot(fetch_new_token, self.get_token)
            except Exception as e:
                print(e)
                self.settings.set_value("cpod_token", None)
                self.logger.insert(
                    "Error decoding Token. Trying to get a new token.", "ERROR"
                )
                self.get_token()
        else:
            self.get_token()

    def get_token(self):
        self.token_thread = GetTokenThread()
        self.token_thread.send_token.connect(self.receive_token)
        self.token_thread.finished.connect(self.token_thread.quit)
        self.token_thread.finished.connect(self.token_thread.deleteLater)
        self.token_thread.start()

    @Slot(str, bool)
    def receive_token(self, token, wasRecieved):
        if wasRecieved:
            print(token)
            self.logger.insert(
                "Cpod Token was Recieved.",
            )
            if token.startswith("Bearer "):
                token = (
                    token.split("Bearer ")[1] if token.startswith("Bearer ") else token
                )

            self.settings.set_value("cpod_token", token)
        else:
            self.logger.insert("Failed to Receive Cpod Token.", "ERROR")

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
