from __future__ import annotations

import pickle
from random import randint
from time import sleep, time
from typing import TYPE_CHECKING

import requests
from bs4 import BeautifulSoup
from PySide6.QtCore import QMutex, QMutexLocker

from base import QObjectBase, QSingleton
from services import Logger
from utils.files import OpenFile, PathManager, WriteFile

if TYPE_CHECKING:
    from context import AppContext


class SessionManager(QObjectBase, metaclass=QSingleton):
    _ctx: AppContext | None = None

    def __init__(self):
        super().__init__()
        self.cookie_lock = QMutex()

    def bind_context(self, ctx: AppContext):
        if self._ctx is not None:
            return  # or raise if you want strictness
        self._ctx = ctx

    def build_session(self):
        session = requests.Session()
        self._copy_cookie_jar(session)
        return session

    def post(self, url, data=None, json=None, timeout=10, headers=None):
        session = self.build_session()
        response = session.post(
            url, data=data, json=json, timeout=timeout, headers=headers
        )
        self.update_cookie_jar(session)
        return response

    def get(self, url, data=None, json=None, timeout=10, headers=None):
        session = self.build_session()
        response = session.get(
            url, data=data, json=json, timeout=timeout, headers=headers
        )
        self.update_cookie_jar(session)
        return response

    def _copy_cookie_jar(self, session):
        with QMutexLocker(self.cookie_lock):
            for cookie in self._ctx.cookie_jar:
                session.cookies.set(
                    cookie.name,
                    cookie.value,
                    domain=cookie.domain,
                    path=cookie.path,
                    secure=cookie.secure,
                    expires=cookie.expires,
                    rest=cookie._rest,
                )

    def update_cookie_jar(self, session):
        with QMutexLocker(self.cookie_lock):

            session_domains = {cookie.domain for cookie in session.cookies}
            cookies_to_remove = [
                c for c in self._ctx.cookie_jar if c.domain in session_domains
            ]
            for cookie in cookies_to_remove:
                self._ctx.cookie_jar.clear(
                    domain=cookie.domain,
                    path=cookie.path,
                    name=cookie.name,
                )

            for cookie in session.cookies:
                self._ctx.cookie_jar.set(
                    cookie.name,
                    cookie.value,
                    domain=cookie.domain,
                    path=cookie.path,
                    secure=cookie.secure,
                    expires=cookie.expires,
                    rest=cookie._rest,
                )

    # TODO used in web_scrape - need to remove
    def get_session_url(self):
        return f"{self.ses_url}"

    def load_session(self):
        try:
            self.logging("Try to Load Session From File", "INFO")
            path = PathManager.create_folder_in_app_data("session")
            cookies = OpenFile.open_pickle(f"{path}/session.pickle")
            expired = False
            cookie_domains = {}
            for cookie in cookies:
                cookie_domain = cookie.domain
                cookie_domain = cookie_domain.removeprefix(".")
                cookie_domain = cookie_domain.removeprefix("www.")

                if cookie_domain not in cookie_domains:
                    cookie_domains[cookie_domain] = False

                if cookie.expires and cookie.expires < time():
                    cookie_domains[cookie_domain] = True
                    expired = True
                    self.logging(f"Found an expired cookie for {cookie_domain}", "WARN")

            if expired or len(cookies) == 0:

                return (False, cookie_domains)
            else:
                self._ctx.cookie_jar = cookies
                self.logging("Session Loaded Successfully...", "INFO")

                return (True, cookie_domains)
        except ValueError:
            self.logging("Error loading session - Filepath doesn't exist", "ERROR")
            return (False, {})

    def save_session(self):
        self.logging("Saving Session...", "INFO")
        path = PathManager.create_folder_in_app_data("session")
        WriteFile.write_file(
            f"{path}/session.pickle",
            pickle.dumps(self._ctx.cookie_jar),
            "wb",
            True,
            False,
        )

    # TODO remove from session
    def get_html(self, url):
        Logger().insert("Getting HTML...", "INFO")
        req = self.build_session().get(f"{url}")
        soup = BeautifulSoup(req.text, "html.parser")
        sleep(randint(6, 15))
        return soup

    def convert_cookies(self, cookies: list) -> requests.cookies.RequestsCookieJar:
        jar = requests.cookies.RequestsCookieJar()
        for cookie in cookies:
            jar.set(
                cookie["name"],
                cookie["value"],
                domain=cookie.get("domain"),
                path=cookie.get("path", "/"),
            )
        return jar

    def jar_to_selenium_list(self, allowed_domains=None):
        cookies_list = []
        for c in self.cookie_jar:
            if allowed_domains and c.domain not in allowed_domains:
                continue

            cookies_list.append(
                {
                    "name": c.name,
                    "value": c.value,
                    "domain": c.domain,
                    "path": c.path,
                    "secure": c.secure,
                    "httpOnly": c._rest.get("HttpOnly", False),
                    "expiry": c.expires,
                }
            )
        return cookies_list
