from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..session.session_registry import SessionRegistry
    from base.enums import PROVIDERS

import time

from PySide6.QtCore import Signal

from base import QObjectBase
from base.enums import AUTHVALIDATIONSTATUS
from models.services.network import AuthValidationResponse


class BaseAuthService(QObjectBase):
    validation_status = Signal(str, str)

    def __init__(self, session_registry: SessionRegistry, provider: PROVIDERS):
        super().__init__()
        self.session = session_registry.for_provider(provider=provider)
        self.provider_name = provider
        self.last_login_attempt = None
        self.login_cooldown_seconds = self.session.login_cool_down

    def send_validation_status(self, status: AUTHVALIDATIONSTATUS):
        self.validation_status.emit(self.provider_name, status)

    def validate(self) -> AuthValidationResponse:
        raise NotImplementedError

    def ensure_authenticated(self) -> None:
        raise NotImplementedError

    def can_attempt_login(self) -> bool:
        if not self.last_login_attempt:
            return True

        elapsed = time.time() - self.last_login_attempt
        return elapsed > self.login_cooldown_seconds
