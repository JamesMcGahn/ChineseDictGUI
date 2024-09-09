import pickle
from random import randint
from time import sleep, time

import requests
from bs4 import BeautifulSoup
from PySide6.QtCore import QObject

from open_file import OpenFile
from services import Logger
from write_file import WriteFile


class SessionManager(QObject):
    session = requests.Session()

    def __init__(self):
        super().__init__()

    def post(self, url, data=None, json=None, timeout=10):
        return SessionManager.session.post(url, data=data, json=json, timeout=timeout)

    def get(self, url, data=None, json=None, timeout=10):
        return SessionManager.session.get(url, data=data, json=json, timeout=timeout)

    # TODO used in web_scrape - need to remove
    def get_session_url(self):
        return f"{self.ses_url}"

    def load_session(self):
        try:
            Logger().insert("Loading Session...", "INFO")

            cookies = OpenFile.open_pickle("./data/session.pickle")
            expired = False
            for cookie in cookies:
                if cookie.expires and cookie.expires < time():
                    expired = True
            if expired or len(cookies) == 0:
                return False
            else:
                self.set_cookies(cookies)
                Logger().insert("Session Loaded...", "INFO")
                return True
        except ValueError:
            Logger().insert("Error loading session - Filepath doesn't exist", "ERROR")
            return False

    def save_session(self):
        Logger().insert("Saving Session...", "INFO")
        WriteFile.write_file(
            "./data/session.pickle", pickle.dumps(self.get_cookies()), "wb", True, False
        )

    def set_cookies(self, cookies):
        SessionManager.session.cookies = cookies

    def get_cookies(self):
        return SessionManager.session.cookies

    # TODO remove from session
    def get_html(self, url):
        Logger().insert("Getting HTML...", "INFO")
        req = SessionManager.session.get(f"{url}")
        soup = BeautifulSoup(req.text, "html.parser")
        sleep(randint(6, 15))
        return soup
