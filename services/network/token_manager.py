import time

import jwt
from PySide6.QtCore import QObject, QThread, QTimer, Signal, Slot

from base import QSingleton, ThreadCleanUpManager
from core.cpod import TokenWorker

from ..logger import Logger
from ..settings import AppSettings


class TokenManager(QObject, metaclass=QSingleton):
    send_token = Signal(str)
    send_cookies = Signal(list)

    def __init__(self):
        super().__init__()
        self.settings = AppSettings()
        self.logger = Logger()
        self._token = None
        self.token_fetch_in_progress = False
        self.token_tries = 0
        self.token_threads = {}
        self.cleanup_manager = ThreadCleanUpManager()

    @Slot()
    def request_token(self):
        print("token is ", self.token)
        if self.token:
            self.send_token.emit(self.token)
        else:
            self.get_token()

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, new_token):
        self._token = new_token
        self.settings.set_value("cpod_token", new_token)
        self.send_token.emit(new_token)

    def remove_bearer(self, token):
        return token.split("Bearer ")[1] if token.startswith("Bearer ") else token

    def is_token_valid(self, token):
        decoded = jwt.decode(self.token, options={"verify_signature": False})
        expire_timestamp = decoded.get("exp")
        now_timestamp = int(time.time())
        time_left = expire_timestamp - now_timestamp
        return time_left > 3600, time_left

    @Slot()
    def check_token(self):
        self.logger.insert("Checking For a Stored Cpod token.")
        self.token = self.settings.get_value("cpod_token")

        if self.token:
            try:
                self.token = self.remove_bearer(self.token)
                valid, time_left = self.is_token_valid(self.token)
                if not valid:
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
                    self.logger.insert(
                        f"Scheduling a new token request in {minutes_left} minutes."
                    )
            except Exception as e:
                print(e)

                self.logger.insert(
                    "Error decoding Cpod token. Trying to get a new token.", "ERROR"
                )
                self.get_token()
        else:
            self.get_token()

    def get_token(self):

        if self.token_fetch_in_progress:
            return

        if self.token_tries == 2:
            self.logger.insert(
                "Tried two times to get a cpod token. Failed to get token.", "ERROR"
            )
            return
        self.token_fetch_in_progress = True

        task_id = f"token_fetch_{self.token_tries}"
        token_thread = QThread()
        token_worker = TokenWorker()
        token_worker.moveToThread(token_thread)
        token_worker.send_token.connect(self.receive_token)
        token_worker.send_cookies.connect(self.send_cookies)
        token_worker.finished.connect(
            lambda: self.cleanup_manager.cleanup_task(task_id, False)
        )
        token_thread.finished.connect(
            lambda: self.cleanup_manager.cleanup_task(task_id, True)
        )
        token_thread.started.connect(token_worker.run)
        token_thread.start()
        self.cleanup_manager.add_task(task_id, token_thread, token_worker)
        self.token_tries += 1

    @Slot(str, bool)
    def receive_token(self, token, wasReceived):
        self._clear_fetch_flag()
        if wasReceived:
            self.logger.insert("Cpod Token was Recieved.")
            self.token = self.remove_bearer(token)
            self.check_token()
            self.send_token.emit(self.token)

        else:
            self.logger.insert("Failed to Receive Cpod Token.", "ERROR")
            # TODO retry one time
            self.token = None

    def _clear_fetch_flag(self):
        self.token_fetch_in_progress = False
