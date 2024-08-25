import pickle
from random import randint
from time import sleep, time

import requests
from bs4 import BeautifulSoup
from PySide6.QtCore import QObject

from logger import Logger
from open_file import OpenFile
from write_file import WriteFile


class SessionManger(QObject):
    session = requests.Session()

    def __init__(self):
        super().__init__()

    def post(self, url, data=None, json=None):
        return SessionManger.session.post(url, data=data, json=json)

    def get(self, url):
        return SessionManger.session.get(url)

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
                return True
        except ValueError:
            Logger().insert("Error loading session", "ERROR")
            return False

    def save_session(self):
        Logger().insert("Saving Session...", "INFO")
        WriteFile.write_file(
            "./data/session.pickle", pickle.dumps(self.get_cookies()), "wb", True, False
        )

    def set_cookies(self, cookies):
        SessionManger.session.cookies = cookies

    def get_cookies(self):
        return SessionManger.session.cookies

    # TODO remove from session
    def get_html(self, url):
        Logger().insert("Getting HTML...", "INFO")
        req = SessionManger.session.get(f"{url}")
        soup = BeautifulSoup(req.text, "html.parser")
        sleep(randint(6, 15))
        return soup
