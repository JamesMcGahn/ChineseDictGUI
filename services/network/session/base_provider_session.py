import json
from pathlib import Path
from time import time

import requests
from PySide6.QtCore import QMutex, QMutexLocker

from base import QObjectBase
from base.enums import PROVIDERS
from utils.files import PathManager


class BaseProviderSession(QObjectBase):

    def __init__(self):
        super().__init__()
        self.loaded_session = False
        self.cookie_lock = QMutex()
        self.cookie_jar = requests.cookies.RequestsCookieJar()
        self.session = None
        self._token = None

    class Config:
        provider_name = PROVIDERS.DEFAULT
        has_token = False
        has_cookies = False
        has_auth_cookies = False
        auth_cookies = set()
        domains = set()

    @property
    def has_domains(self) -> set:
        return getattr(self.Config, "domains", False)

    @property
    def has_token(self) -> bool:
        return getattr(self.Config, "has_token", False)

    @property
    def provider_name(self) -> str:
        return getattr(self.Config, "provider_name", PROVIDERS.DEFAULT)

    @property
    def has_auth_cookies(self) -> str:
        return getattr(self.Config, "has_auth_cookies", False)

    @property
    def has_cookies(self) -> str:
        return getattr(self.Config, "has_cookies", False)

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, new_token):
        self._token = new_token

    def load_token(self):
        if not self.has_token:
            return

        self.logging(f"{self.provider_name.upper()} checking for a stored token.")
        path = PathManager.create_folder_in_app_data(f"session/{self.provider_name}")
        file = Path(path) / "token.json"
        token = None
        if file.exists():
            with open(file, "r") as file:
                token = json.loads(file.read())

        if token and token.get("token"):
            self.token = token["token"]
            self.logging(
                f"{self.provider_name.upper()} Token Loaded Successfully...", "INFO"
            )
            return True
        else:
            self.token = None
            self.logging(f"{self.provider_name.upper()} No Token Found", "WARN")
            return False

    def save_token(self):
        if not self.has_token:
            return

        if self.token is None:
            self.logging(
                f"{self.provider_name.upper()} skipping saving token. Token is None.",
                "INFO",
            )
            return

        self.logging(f"{self.provider_name.upper()} saving token...", "INFO")
        path = PathManager.create_folder_in_app_data(f"session/{self.provider_name}")

        with open(f"{path}/token.json", "w") as f:
            f.write(
                json.dumps(
                    {"token": self.token},
                    indent=2,
                )
            )
        self.logging(f"{self.provider_name.upper()} token saved successfully.", "INFO")

    def _copy_cookie_jar(self, session):
        with QMutexLocker(self.cookie_lock):
            for cookie in self.cookie_jar:
                session.cookies.set(
                    cookie.name,
                    cookie.value,
                    domain=cookie.domain,
                    path=cookie.path,
                    secure=cookie.secure,
                    expires=cookie.expires,
                    rest=cookie._rest,
                )
        return session

    def _update_cookie_jar(self, cookies):
        with QMutexLocker(self.cookie_lock):
            for cookie in cookies:
                self._delete_cookie_from_jar(cookie)

                self.cookie_jar.set(
                    cookie.name,
                    cookie.value,
                    domain=cookie.domain,
                    path=cookie.path,
                    secure=cookie.secure,
                    expires=cookie.expires,
                    rest=cookie._rest,
                )
        self.logging(f"{self.provider_name.upper()} updated session.")

    def filter_cookies_by_domain(self, cookies, domains: set[str] | None = None):
        domain_filter = domains or self.has_domains
        if not domain_filter:
            return cookies

        filtered_cookies = []
        for cookie in cookies:
            domain = cookie.get("domain")
            if not domain:
                continue
            domain = domain.removeprefix(".").removeprefix("www.")
            if any(domain == d or domain.endswith(f".{d}") for d in domain_filter):
                filtered_cookies.append(cookie)
        return filtered_cookies

    def _delete_cookie_from_jar(self, cookie):
        try:
            self.cookie_jar.clear(
                domain=cookie.domain,
                path=cookie.path,
                name=cookie.name,
            )
        except KeyError:
            pass

    def convert_cookies_to_jar(
        self, cookies: list
    ) -> requests.cookies.RequestsCookieJar:
        jar = requests.cookies.RequestsCookieJar()
        for cookie in cookies:
            jar.set(
                cookie["name"],
                cookie["value"],
                domain=cookie.get("domain"),
                path=cookie.get("path", "/"),
                expires=cookie.get("expires"),
            )
        return jar

    def convert_jar_to_cookie_list(self):
        cookies_list = []

        for c in self.cookie_jar:
            cookie = {
                "name": c.name,
                "value": c.value,
                "domain": c.domain,
                "path": c.path,
                "secure": c.secure,
                "httpOnly": c._rest.get("HttpOnly") or c._rest.get("httponly", False),
            }

            if c.expires and c.expires > 0:
                try:
                    cookie["expires"] = int(c.expires)
                except (TypeError, ValueError):
                    pass
            cookies_list.append(cookie)
        return cookies_list

    def load_cookies(self):
        if not self.has_cookies:
            return
        self.logging(
            f"{self.provider_name.upper()} Try to Load Cookies From File", "INFO"
        )
        path = PathManager.create_folder_in_app_data(f"session/{self.provider_name}")
        cookies = []
        file = Path(path) / "session.json"

        if file.exists():
            with open(file, "r") as file:
                cookie_json = file.read()
                cookies = json.loads(cookie_json)
        cookies = self.filter_cookies_by_domain(cookies)
        jar = self.convert_cookies_to_jar(cookies)
        self._update_cookie_jar(jar)

        self.loaded_session = True
        self.logging(
            f"{self.provider_name.upper()} Session Loaded Successfully...", "INFO"
        )

    def save_cookies(self):
        if not self.has_cookies:
            return
        self.logging(f"{self.provider_name.upper()} saving cookies...", "INFO")
        path = PathManager.create_folder_in_app_data(f"session/{self.provider_name}")
        cookies = self.convert_jar_to_cookie_list()
        cookies = self.filter_cookies_by_domain(cookies)

        with open(f"{path}/session.json", "w") as f:
            f.write(
                json.dumps(
                    cookies,
                    indent=2,
                )
            )
        self.logging(
            f"{self.provider_name.upper()} cookies saved successfully.", "INFO"
        )

    def build_session(self):
        session = requests.Session()
        session = self._copy_cookie_jar(session)
        return session

    def update_cookies_from_list(self, cookie_list):
        jar = self.convert_cookies_to_jar(cookie_list)
        self._update_cookie_jar(jar)

    def update_cookies_from_res(self, res: requests.Response):
        if res and res.cookies:
            cookies = res.cookies
            self._update_cookie_jar(cookies)

    def load_session(self):
        if self.loaded_session:
            self.logging(f"{self.provider_name.upper()} Session Already Loaded", "INFO")
            return

        self.logging(
            f"{self.provider_name.upper()} Try to Load Session From File", "INFO"
        )
        self.load_cookies()
        self.load_token()

    def save_session(self):
        self.logging(f"{self.provider_name.upper()} saving session...", "INFO")
        self.save_cookies()
        self.save_token()
        self.logging(
            f"{self.provider_name.upper()} session saved successfully.", "INFO"
        )

    def get_auth_cookies(self):
        return [
            cookie
            for cookie in self.cookie_jar
            if cookie.name in self.Config.auth_cookies
        ]

    def has_valid_auth_cookies(self):
        self.logging(
            f"{self.provider_name.upper()} checking auth cookies for expiration."
        )
        auth_cookies = self.get_auth_cookies()
        if not auth_cookies:
            return False

        auth_cookie_names = {cookie.name for cookie in auth_cookies}
        if not self.Config.auth_cookies.issubset(auth_cookie_names):
            return False

        for cookie in auth_cookies:
            if cookie.expires and cookie.expires > 0 and cookie.expires < time():
                return False
        return True
