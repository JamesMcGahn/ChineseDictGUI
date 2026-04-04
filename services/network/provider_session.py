import json
from pathlib import Path
from time import time

import requests
from PySide6.QtCore import QMutex, QMutexLocker, Slot

from base import QObjectBase
from base.enums import PROVIDERS
from utils.files import PathManager


class ProviderSession(QObjectBase):

    def __init__(self, provider: PROVIDERS):
        super().__init__()
        self.provider_name = provider
        self.loaded_session = False
        self.cookie_lock = QMutex()
        self.cookie_jar = requests.cookies.RequestsCookieJar()
        self.session = None

    def _update_cookie_jar(self, cookies):
        with QMutexLocker(self.cookie_lock):
            for cookie in cookies:
                try:
                    self.cookie_jar.clear(
                        domain=cookie.domain,
                        path=cookie.path,
                        name=cookie.name,
                    )
                except KeyError:
                    pass

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

    def load_session(self):
        if self.loaded_session:
            self.logging(f"{self.provider_name.upper()} Session Already Loaded", "INFO")
            return
        self.logging(
            f"{self.provider_name.upper()} Try to Load Session From File", "INFO"
        )
        path = PathManager.create_folder_in_app_data(f"session/{self.provider_name}")
        cookies = []
        file = Path(path) / "session.json"

        if file.exists():
            with open(file, "r") as file:
                cookie_json = file.read()
                cookies = json.loads(cookie_json)

        jar = self.convert_cookies_to_jar(cookies)
        self._update_cookie_jar(jar)

        self.loaded_session = True
        self.logging(
            f"{self.provider_name.upper()} Session Loaded Successfully...", "INFO"
        )

    def build_session(self):
        session = requests.Session()
        self._copy_cookie_jar(session)
        return session

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

    def check_cookies(self):
        self.logging(f"{self.provider_name.upper()} checking cookies for expiration.")
        expired = False
        cookie_domains = {}
        for cookie in self.cookie_jar:
            cookie_domain = cookie.domain
            cookie_domain = cookie_domain.removeprefix(".")
            cookie_domain = cookie_domain.removeprefix("www.")

            if cookie_domain not in cookie_domains:
                cookie_domains[cookie_domain] = False

            if cookie.expires and cookie.expires < time():
                cookie_domains[cookie_domain] = True
                expired = True
                self.logging(
                    f"{self.provider_name.upper()} Found an expired cookie for {cookie_domain}",
                    "WARN",
                )
        if not expired:
            self.logging(f"{self.provider_name.upper()} no expired cookies found")

        return cookie_domains

    def save_session(self):
        self.logging(f"{self.provider_name.upper()} saving session...", "INFO")
        path = PathManager.create_folder_in_app_data(f"session/{self.provider_name}")

        with open(f"{path}/session.json", "w") as f:
            f.write(
                json.dumps(
                    self.jar_to_cookie_list(self.cookie_jar),
                    indent=2,
                )
            )
        self.logging(
            f"{self.provider_name.upper()} session saved successfully.", "INFO"
        )

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

    def jar_to_cookie_list(self, cookie_jar):
        cookies_list = []

        for c in cookie_jar:
            cookies_list.append(
                {
                    "name": c.name,
                    "value": c.value,
                    "domain": c.domain,
                    "path": c.path,
                    "secure": c.secure,
                    "httpOnly": c._rest.get("HttpOnly", False),
                    "expires": c.expires,
                }
            )

        return cookies_list

    @Slot(list)
    def receive_playwright_cookies(self, cookie_list):
        jar = self.convert_cookies_to_jar(cookie_list)
        self._update_cookie_jar(jar)

    def update_cookies_from_res(self, res: requests.Response):
        if res and res.cookies:
            cookies = res.cookies
            self._update_cookie_jar(cookies)
