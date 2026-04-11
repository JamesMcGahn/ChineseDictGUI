from base.enums import PROVIDERS

from ..network.session.base_provider_session import BaseProviderSession


class CpodProviderSession(BaseProviderSession):

    def __init__(self):
        super().__init__()

    class Config:
        provider_name = PROVIDERS.CPOD
        has_token = False
        has_cookies = True
        has_auth_cookies = True
        auth_cookies = {"connect.sid", "cpod.sid", "CPODSESSID"}
        domains = {"chinesepod.com"}
