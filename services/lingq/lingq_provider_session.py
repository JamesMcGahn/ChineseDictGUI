from base.enums import PROVIDERS

from ..network.session.base_provider_session import BaseProviderSession


class LingqProviderSession(BaseProviderSession):

    def __init__(self):
        super().__init__()

    class Config:
        provider_name = PROVIDERS.LINGQ
        has_token = False
        has_cookies = True
        has_auth_cookies = True
        auth_cookies = {"wwwlingqcomsa", "csrftoken"}
        domains = {"lingq.com"}
