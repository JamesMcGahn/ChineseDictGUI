from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..session import BaseProviderSession

import time

import jwt
from PySide6.QtCore import QThread, QTimer, Signal, Slot

from base import QObjectBase, ThreadCleanUpManager
from base.enums import AUTHVALIDATIONSTATUS
from core.cpod import TokenWorker


class CpodTokenManager(QObjectBase):
    token_status = Signal(str)

    def __init__(self, session: BaseProviderSession):
        super().__init__()
        self.session = session
        self.token_fetch_in_progress = False
        self.token_tries = 0
        self.token_threads = {}
        self.cleanup_manager = ThreadCleanUpManager()
        self.refresh_timer = QTimer(self)
        self.refresh_timer.setSingleShot(True)
        self.refresh_timer.timeout.connect(self.get_token)

    def remove_bearer(self, token):
        if token is None:
            return None
        return token.split("Bearer ")[1] if token.startswith("Bearer ") else token

    def is_token_valid(self, token) -> tuple[bool, int]:
        if token is None:
            return False, 0
        decoded = jwt.decode(token, options={"verify_signature": False})
        expire_timestamp = decoded.get("exp")
        now_timestamp = int(time.time())
        time_left = expire_timestamp - now_timestamp
        return time_left > 3600, time_left

    def check_token(self, token) -> bool:
        try:
            token = self.remove_bearer(token)
            valid, time_left = self.is_token_valid(token)

            if not valid:
                self.logging("Cpod token going to expire. Trying to get a new token")
                return False
            else:
                self.schedule_token(token)
                return True

        except Exception as e:
            self.logging(f"{e}", "ERROR")
            self.logging(
                "Error decoding Cpod token. Trying to get a new token.",
                "ERROR",
            )
            self.token_status.emit(AUTHVALIDATIONSTATUS.FAILED)
            return False

    def schedule_token(self, token):
        try:
            token = self.remove_bearer(token)
            valid, time_left = self.is_token_valid(token)
            minutes_left = time_left // 60
            hours_left = minutes_left // 60
            display_minutes = minutes_left % 60

            self.logging(
                f"Cpod token is still valid for {hours_left} hours and {display_minutes} minutes."
            )
            fetch_new_token = max((minutes_left - 60) * 60000, 0)
            self.refresh_timer.stop()  # cancel previous
            self.refresh_timer.start(fetch_new_token)
            self.logging(
                f"Scheduling a new token request in {minutes_left -60} minutes."
            )
            return True
        except Exception as e:
            self.logging(f"Error scheduling token. {e}")
            return False

    def get_token(self):
        if self.token_fetch_in_progress:
            return

        if self.token_tries == 3:
            self.logging(
                "Tried three times to get a cpod token. Failed to get token.",
                "ERROR",
            )
            self.token_status.emit(AUTHVALIDATIONSTATUS.FAILED)
            return
        self.token_fetch_in_progress = True
        self.token_status.emit(AUTHVALIDATIONSTATUS.BUSY)
        task_id = f"token_fetch_{self.token_tries}"
        token_thread = QThread()
        token_worker = TokenWorker(session=self.session)
        token_worker.moveToThread(token_thread)
        token_worker.send_token.connect(self.receive_token)
        token_worker.done.connect(
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

        if wasReceived and self.check_token(token):
            self.logging("Cpod Token was Recieved.")
            self.session.token = token

        else:
            self.logging("Failed to Receive Cpod Token.", "ERROR")
            self.session.token = None
            if self.token_tries < 3:
                wait_time = self.token_tries * 30000
                self.logging(
                    f"Waiting {int(wait_time/1000)} seconds before reattempting getting Cpod Token ",
                    "INFO",
                )
            else:
                wait_time = 0
            QTimer.singleShot(wait_time, self.get_token)

    def _clear_fetch_flag(self):
        self.token_fetch_in_progress = False
