from PySide6.QtCore import Slot

from base import QObjectBase
from base.enums import PROVIDERS

from ...cpod.cpod_provider_session import CpodProviderSession
from ...lingq.lingq_provider_session import LingqProviderSession
from .base_provider_session import BaseProviderSession


class SessionRegistry(QObjectBase):
    def __init__(self):
        super().__init__()
        self._sessions: dict[PROVIDERS, BaseProviderSession] = {}

        self.providers = {
            PROVIDERS.CPOD: CpodProviderSession,
            PROVIDERS.LINGQ: LingqProviderSession,
        }

    def for_provider(self, provider: PROVIDERS) -> BaseProviderSession:
        if provider not in self._sessions:
            provider_session = self.providers.get(provider, BaseProviderSession)
            session = provider_session()
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
