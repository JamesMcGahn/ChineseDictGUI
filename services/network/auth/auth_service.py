from PySide6.QtCore import Signal

from base import QObjectBase
from base.enums import AUTHVALIDATIONSTATUS, PROVIDERS
from models.services.network import AuthValidationResponse

from ...cpod.cpod_auth_service import CpodAuthService
from ...lingq.lingq_auth_service import LingqAuthService
from ..session.session_registry import SessionRegistry
from .base_auth_service import BaseAuthService


class AuthService(QObjectBase):
    validation_status = Signal(str, str)

    def __init__(self, session_registry: SessionRegistry):
        super().__init__()
        self._providers: dict[PROVIDERS, BaseAuthService] = {
            PROVIDERS.CPOD: CpodAuthService(session_registry, PROVIDERS.CPOD),
            PROVIDERS.LINGQ: LingqAuthService(session_registry, PROVIDERS.LINGQ),
        }

        self._providers[PROVIDERS.CPOD].validation_status.connect(
            self.validation_status
        )
        self._providers[PROVIDERS.LINGQ].validation_status.connect(
            self.validation_status
        )

    def validate(self, provider) -> AuthValidationResponse:
        service = self._providers.get(provider)
        if not service:
            self.validation_status.emit(provider, AUTHVALIDATIONSTATUS.UNSUPPORTED)
            return AUTHVALIDATIONSTATUS.UNSUPPORTED
        return service.validate()

    def ensure_authenticated(self, provider) -> None:
        service = self._providers.get(provider)
        if not service:
            raise NotImplementedError(f"{provider} not implemented")
        return service.ensure_authenticated()
