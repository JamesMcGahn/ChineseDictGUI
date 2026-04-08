from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..session.session_registry import SessionRegistry
    from base.enums import PROVIDERS

from PySide6.QtCore import Signal

from base import QObjectBase
from base.enums import AUTHVALIDATIONSTATUS


class BaseAuthService(QObjectBase):
    validation_status = Signal(str, str)

    def __init__(self, session_registry: SessionRegistry, provider: PROVIDERS):
        super().__init__()
        self.session = session_registry.for_provider(provider=provider)
        self.provider_name = provider

    def send_validation_status(self, status: AUTHVALIDATIONSTATUS):
        self.validation_status.emit(self.provider_name.upper(), status)
        return status

    def validate(self) -> AUTHVALIDATIONSTATUS:
        raise NotImplementedError
