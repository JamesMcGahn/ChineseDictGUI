from PySide6.QtCore import QSize
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QMainWindow

import resources_rc as resources_rc
from db.db_manager import DatabaseManager
from keys import keys
from services.network import NetworkThread
from session_manager import SessionManger

from ..central_widget import CentralWidget


class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.session_manager = SessionManger()
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

        self.setup_session()
        self.setup_database()

    def setup_database(self):
        db = DatabaseManager("chineseDict.db")
        db.connect()
        db.create_tables_if_not_exist()
        db.disconnect()

    def setup_session(self):
        if self.session_manager.load_session():
            return
        else:
            # TODO: remove py email and password dict - use keyring
            # TODO: check for keyring - if it doesnt exist -> notify user -> send them to settings page

            self.network_thread = NetworkThread(
                self.session_manager,
                "SESSION",
                f"{keys['url']}accounts/signin",
                data={"email": keys["email"], "password": keys["password"]},
            )
            self.network_thread.response_sig.connect(self.session_response)
            self.network_thread.error_sig.connect(self.session_error)
            self.network_thread.start()

    def session_response(self, status, response):
        print(response)
        self.session_manager.save_session()

        print("cook", self.session_manager.get_cookies())
        self.session2 = SessionManger()
        print("cook2", self.session2.get_cookies())

    def session_error(self, status, message):
        print(status)
        # TODO notify user - error logging them in
        print("There was an error logging you in. ")
