import pickle
from random import randint
from time import sleep, time

import requests
from bs4 import BeautifulSoup
from PySide6.QtCore import QMutex, QMutexLocker, QObject

from base import QSingleton
from services import Logger
from utils.files import OpenFile, WriteFile


class SessionManager(QObject, metaclass=QSingleton):

    def __init__(self):
        super().__init__()
        self.cookie_jar = requests.cookies.RequestsCookieJar()
        self.cookie_lock = QMutex()

    def build_session(self):
        session = requests.Session()
        session.cookies = self.get_cookies()
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

    def update_cookie_jar(self, session):
        with QMutexLocker(self.cookie_lock):
            for cookie in session.cookies:
                self.cookie_jar.set(
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
            Logger().insert("Loading Session...", "INFO")

            cookies = OpenFile.open_pickle("./data/session.pickle")
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
                    Logger().insert(
                        f"Found an expired cookie for {cookie_domain}", "WARN"
                    )

            if expired or len(cookies) == 0:

                return (False, cookie_domains)
            else:
                self.set_cookies(cookies)
                Logger().insert("Session Loaded...", "INFO")

                return (True, cookie_domains)
        except ValueError:
            Logger().insert("Error loading session - Filepath doesn't exist", "ERROR")
            return False

    def save_session(self):
        Logger().insert("Saving Session...", "INFO")
        WriteFile.write_file(
            "./data/session.pickle", pickle.dumps(self.get_cookies()), "wb", True, False
        )

    def set_cookies(self, cookies):
        self.cookie_jar = cookies

    def get_cookies(self):
        return self.cookie_jar.copy()

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
