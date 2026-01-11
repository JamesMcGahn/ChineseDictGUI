from __future__ import annotations

import json
from random import randint
from time import sleep, time
from typing import TYPE_CHECKING

import requests
from bs4 import BeautifulSoup
from PySide6.QtCore import QMutex, QMutexLocker, Slot

from base import QObjectBase, QSingleton
from services import Logger
from utils.files import OpenFile, PathManager, WriteFile

if TYPE_CHECKING:
    from context import AppContext


class SessionManager(QObjectBase, metaclass=QSingleton):
    _ctx: AppContext | None = None

    def __init__(self):
        super().__init__()
        self.loaded_session = False
        self.cookie_lock = QMutex()

    def bind_context(self, ctx: AppContext):
        if self._ctx is not None:
            return  # or raise if you want strictness
        self._ctx = ctx

    def build_session(self):
        session = requests.Session()
        self._copy_cookie_jar(session)
        return session

    def post(self, url, data=None, json=None, timeout=10, headers=None, files=None):
        session = self.build_session()
        response = session.post(
            url, data=data, json=json, timeout=timeout, headers=headers, files=files
        )
        self.update_cookie_jar(session.cookies)
        return response

    def get(self, url, timeout=10, headers=None):
        session = self.build_session()
        response = session.get(url, timeout=timeout, headers=headers)
        self.update_cookie_jar(session.cookies)
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

    def update_cookie_jar(self, cookies):
        with QMutexLocker(self.cookie_lock):
            for cookie in cookies:
                try:
                    self._ctx.cookie_jar.clear(
                        domain=cookie.domain,
                        path=cookie.path,
                        name=cookie.name,
                    )
                except KeyError:
                    pass

                self._ctx.cookie_jar.set(
                    cookie.name,
                    cookie.value,
                    domain=cookie.domain,
                    path=cookie.path,
                    secure=cookie.secure,
                    expires=cookie.expires,
                    rest=cookie._rest,
                )
            self.save_session()

    def load_session(self):
        if self.loaded_session:
            self.logging("Session Already Loaded", "INFO")
            return
        self.logging("Try to Load Session From File", "INFO")
        path = PathManager.create_folder_in_app_data("session")
        cookies = json.loads(OpenFile.open_file(f"{path}/session.json"))
        jar = self.convert_cookies_to_jar(cookies)
        self.update_cookie_jar(jar)

        self.loaded_session = True
        self.logging("Session Loaded Successfully...", "INFO")

    def check_cookies(self):
        expired = False
        cookie_domains = {}
        for cookie in self._ctx.cookie_jar:
            cookie_domain = cookie.domain
            cookie_domain = cookie_domain.removeprefix(".")
            cookie_domain = cookie_domain.removeprefix("www.")

            if cookie_domain not in cookie_domains:
                cookie_domains[cookie_domain] = False

            if cookie.expires and cookie.expires < time():
                cookie_domains[cookie_domain] = True
                expired = True
                self.logging(f"Found an expired cookie for {cookie_domain}", "WARN")

        if expired or len(self._ctx.cookie_jar) == 0:
            return (False, cookie_domains)
        else:
            return (True, cookie_domains)

    def save_session(self):
        self.logging("Saving Session...", "INFO")
        path = PathManager.create_folder_in_app_data("session")

        print(
            "*** FROM SAVE",
            json.dumps(
                self.jar_to_cookie_list(self._ctx.cookie_jar),
                indent=2,
            ),
        )
        WriteFile.write_file(
            f"{path}/session.json",
            json.dumps(
                self.jar_to_cookie_list(self._ctx.cookie_jar),
                indent=2,
            ),
            "w",
            True,
            False,
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
                    "HttpOnly": c._rest.get("HttpOnly", False),
                    "expires": c.expires,
                }
            )

        return cookies_list

    @Slot(list)
    def receive_playwright_cookies(self, cookie_list):
        print(cookie_list)
        jar = self.convert_cookies_to_jar(cookie_list)
        self.update_cookie_jar(jar)
