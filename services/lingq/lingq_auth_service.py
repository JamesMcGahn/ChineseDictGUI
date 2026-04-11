from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..network.session.session_registry import SessionRegistry
    from base.enums import PROVIDERS

import time

from PySide6.QtCore import QThread, Slot

from base import ThreadCleanUpManager
from base.enums import AUTHVALIDATIONSTATUS
from core.lingq import LingqLoginWorker
from models.services.network import AuthValidationResponse

from ..network.auth.base_auth_service import BaseAuthService


class LingqAuthService(BaseAuthService):

    def __init__(self, session_registry: SessionRegistry, provider: PROVIDERS):
        super().__init__(session_registry=session_registry, provider=provider)
        self.login_attempted = False
        self.clean_up_manager = ThreadCleanUpManager()
        self._busy = False

    def validate(self):
        self.logging("Validating auth session credentials...")
        has_valid_cookies = self.session.has_valid_auth_cookies()
        return AuthValidationResponse(
            cookies_valid=has_valid_cookies, token_valid=False
        )

    def ensure_authenticated(self):
        if self._busy:
            self.logging("Auth already in progress")
            self.send_validation_status(AUTHVALIDATIONSTATUS.BUSY)
            return

        result = self.validate()
        if result.cookies_valid:
            self.logging("Cookies valid")
            self.send_validation_status(AUTHVALIDATIONSTATUS.VALID)
            return

        self.logging("Cookies invalid. Logging in")
        self.login()
        self.send_validation_status(AUTHVALIDATIONSTATUS.STARTED)

    def login(self):
        if not self.can_attempt_login():
            self.logging("Login already attempted. Wait to try again", "WARN")
            self.send_validation_status(AUTHVALIDATIONSTATUS.COOLDOWN)
            return

        task_id = f"{self.provider_name}-login"
        login_worker = LingqLoginWorker(session=self.session)
        login_thread = QThread()
        login_worker.moveToThread(login_thread)
        login_worker.lingq_logged_in.connect(self.receive_login)
        login_thread.started.connect(login_worker.do_work)
        self.clean_up_manager.add_task(
            task_id=task_id, thread=login_thread, worker=login_worker
        )
        login_worker.done.connect(lambda: self.clean_up_manager.cleanup_task(task_id))
        login_thread.finished.connect(
            lambda: self.clean_up_manager.cleanup_task(task_id, True)
        )
        self.last_login_attempt = time.time()
        self._busy = True
        self.send_validation_status(AUTHVALIDATIONSTATUS.BUSY)
        login_thread.start()

    @Slot(bool)
    def receive_login(self, logged_in: bool):
        self._busy = False
        if logged_in:
            self.logging("Log in Succeed", "INFO")
            self.send_validation_status(AUTHVALIDATIONSTATUS.VALID)
            return
        else:
            self.logging("Log in Failed", "WARN")
            self.send_validation_status(AUTHVALIDATIONSTATUS.FAILED)
            return
