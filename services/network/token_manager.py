import time

import jwt
from PySide6.QtCore import QObject, QTimer, Signal, Slot

from base import QSingleton

from ..logger import Logger
from ..settings import AppSettings
from .get_token_thread import GetTokenThread


class TokenManager(QObject, metaclass=QSingleton):
    token_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self.settings = AppSettings()
        self.logger = Logger()
        self.check_token()
        self._token = None

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, new_token):
        self._token = new_token
        self.settings.set_value("cpod_token", new_token)
        self.token_changed.emit(new_token)

    def remove_bearer(self, token):
        return token.split("Bearer ")[1] if token.startswith("Bearer ") else token

    def check_token(self):
        self.logger.insert("Checking For a Stored Cpod token.")
        self.token = self.settings.get_value("cpod_token")
        if self.token:
            try:
                self.token = self.remove_bearer(self.token)
                decoded = jwt.decode(self.token, options={"verify_signature": False})
                expire_timestamp = decoded.get("exp")
                now_timestamp = int(time.time())
                time_left = expire_timestamp - now_timestamp
                if time_left <= 3600:
                    self.token = None
                    self.logger.insert(
                        "Cpod token going to expire. Trying to get a new token"
                    )
                    self.get_token()
                else:
                    minutes_left = time_left // 60
                    hours_left = minutes_left // 60
                    self.logger.insert(
                        f"Cpod token is still valid for {hours_left} hours."
                    )
                    fetch_new_token = max((minutes_left - 60) * 60000, 0)
                    QTimer.singleShot(fetch_new_token, self.get_token)
            except Exception as e:
                print(e)

                self.logger.insert(
                    "Error decoding Cpod token. Trying to get a new token.", "ERROR"
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
            self.logger.insert(
                "Cpod Token was Recieved.",
            )
            self.token = self.remove_bearer(token)

        else:
            self.logger.insert("Failed to Receive Cpod Token.", "ERROR")
            self.token = None
