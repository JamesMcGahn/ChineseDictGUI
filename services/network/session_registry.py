from PySide6.QtCore import Slot

from base import QObjectBase
from base.enums import PROVIDERS

from .provider_session import ProviderSession


class SessionRegistry(QObjectBase):
    def __init__(self):
        self._sessions: dict[PROVIDERS, ProviderSession] = {}

        self.PRE_LOAD = {
            PROVIDERS.CPOD: True,
            PROVIDERS.LINGQ: True,
            PROVIDERS.DEFAULT: True,
        }

    def for_provider(self, provider: PROVIDERS) -> ProviderSession:
        if provider not in self._sessions:
            session = ProviderSession(provider=provider)
            session.load_session()
            self._sessions[provider] = session
        return self._sessions[provider]

    def pre_load_providers(self, providers: list[PROVIDERS]):
        for provider in providers:
            self.for_provider(provider)

    @Slot()
    def save_all(self):
        for provider_session in self._sessions.values():
            provider_session.save_session()
