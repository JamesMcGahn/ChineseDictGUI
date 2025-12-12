from PySide6.QtCore import QObject, QThread, QTimer, Signal, Slot

from core.lingq import LingqCollectionsWorker
from db import DatabaseManager
from keys import keys
from services.logger import Logger
from services.network import NetworkThread, SessionManager, TokenManager
from services.settings import AppSettings


class AppContext(QObject):
    send_logs = Signal(str, str, bool)
    check_token = Signal()

    def __init__(self):
        super().__init__()
        self.logger = Logger()
        self.send_logs.connect(self.logger.insert)
        self.session_manager = SessionManager()
        self.settings = AppSettings()
        self.setup_database()

        self.lingq_courses = []

        self.token_manager = TokenManager()
        self.check_token.connect(self.token_manager.check_token)
        self.setup_session()
        self.check_token.emit()

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

    def setup_database(self):
        db = DatabaseManager("chineseDict.db")
        db.connect()
        db.create_tables_if_not_exist()
        db.create_anki_integration_record()
        db.disconnect()

    def setup_session(self):
        expired, domains = self.session_manager.load_session()
        if "lingq.com" not in domains or domains["lingq.com"]:
            #         print("session expired, getting new session")
            #         # TODO: remove py email and password dict - use keyring
            #         # TODO: check for keyring - if it doesnt exist -> notify user -> send them to settings page

            self.network_thread = NetworkThread(
                "POST",
                "https://www.lingq.com/en/accounts/login/",
                data={
                    "username": keys["email"],
                    "password": keys["lingqpw"],
                    "remember-me": "on",
                },
            )

            self.network_thread.response_sig.connect(self.session_response)
            self.network_thread.error_sig.connect(self.session_error)
            self.network_thread.start()
        else:
            self.lingcollect_thread = QThread()
            self.lingcollect = LingqCollectionsWorker()
            self.lingcollect.moveToThread(self.lingcollect_thread)
            self.lingcollect_thread.started.connect(self.lingcollect.do_work)
            self.lingcollect.send_logs.connect(self.send_logs)
            self.lingcollect.lingq_categories.connect(self.lingq_courses_response)
            self.lingcollect.error.connect(self.lingq_courses_error)
            self.lingcollect.finished.connect(self.lingcollect_thread.quit)
            self.lingcollect_thread.finished.connect(
                self.lingcollect_thread.deleteLater
            )
            self.lingcollect_thread.start()

    def lingq_courses_response(self, collections):
        print("recieved collections", collections)

    def lingq_courses_error(self, status_code):
        if status_code == 401:
            # TODO login in again
            pass

    def session_response(self, status, response):
        # print(response.text)
        print(response.cookies)
        for cookie in response.cookies:
            print(cookie.domain)
            if cookie.name == "csrftoken" and cookie.domain == "www.lingq.com":

                print("cookie HERE")
        self.network_thread.quit()
        self.network_thread.deleteLater()
        self.session_manager.save_session()

    def session_error(self, status, message):
        print(status, message)
        # TODO notify user - error logging them in
        print("There was an error logging you in. ")
