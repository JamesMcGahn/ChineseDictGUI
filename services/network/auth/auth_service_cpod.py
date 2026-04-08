from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..session.session_registry import SessionRegistry
    from base.enums import PROVIDERS

from PySide6.QtCore import Slot

from base.enums import AUTHVALIDATIONSTATUS

from .base_auth_service import BaseAuthService
from .token_manager_cpod import CpodTokenManager


class CpodAuthService(BaseAuthService):

    def __init__(self, session_registry: SessionRegistry, provider: PROVIDERS):
        super().__init__(session_registry=session_registry, provider=provider)
        self.token_manager = CpodTokenManager(session=self.session)
        self.token_manager.token_status.connect(self.token_status)

    def validate(self):
        self.logging("Validating auth session credentials...")
        valid_token = self.token_manager.check_token(self.session.token)
        valid_cookies = self.session.has_valid_auth_cookies()

        if not valid_token or not valid_cookies:

            self.logging(
                f"{self.provider_name.upper()} {"Token" if not valid_token else "Cookies"} expired. Refreshing..."
            )
            self.token_manager.get_token()
            return self.send_validation_status(AUTHVALIDATIONSTATUS.STARTED)
        self.logging(f"{self.provider_name.upper()} auth credentials valid")
        return self.send_validation_status(AUTHVALIDATIONSTATUS.VALID)

    @Slot(str)
    def token_status(self, auth_status: AUTHVALIDATIONSTATUS):
        return self.send_validation_status(auth_status)
