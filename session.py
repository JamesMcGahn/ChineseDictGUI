import pickle
from random import randint
from time import sleep, time

import requests
from bs4 import BeautifulSoup
from logger import Logger
from open_file import OpenFile
from write_file import WriteFile


class Session:
    session = requests.Session()

    def __init__(self, ses_url, email, password):
        self.ses_url = ses_url
        self.payload = {"email": email, "password": password}

    def __repr__(self):
        return f"session for {self.ses_url}"

    def get_session_url(self):
        return f"{self.ses_url}"

    def get_session(self):
        try:
            Logger().insert("Getting New Session...", "INFO")
            ses = Session.session.post(self.ses_url, data=self.payload)

            if not any(c.name == "lang" for c in ses.cookies):
                raise requests.exceptions.RequestException

            return self.session
        except requests.exceptions.RequestException as e:
            print(e)

    def load_session(self):
        try:
            Logger().insert("Loading Session...", "INFO")

            cookies = OpenFile.open_pickle("./data/session.pickle")
            expired = False
            for cookie in cookies:
                if cookie.expires and cookie.expires < time():
                    expired = True
            if expired or len(cookies) == 0:
                return self.get_session()
            else:
                self.set_cookies(cookies)
        except ValueError:
            Logger().insert("Error loading session", "ERROR")
            return self.get_session()

    def save_session(self):
        Logger().insert("Saving Session...", "INFO")
        WriteFile.write_file(
            "./data/session.pickle", pickle.dumps(self.get_cookies()), "wb", True, False
        )

    def set_cookies(self, cookies):
        self.session.cookies = cookies

    def get_cookies(self):
        return self.session.cookies

    def get_html(self, url):
        Logger().insert("Getting HTML...", "INFO")
        req = Session.session.get(f"{url}")
        soup = BeautifulSoup(req.text, "html.parser")
        sleep(randint(6, 15))
        return soup
