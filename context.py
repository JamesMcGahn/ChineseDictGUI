import os
import subprocess
import sys

import requests
from PySide6.QtCore import QThread, QTimer, Signal, Slot

from base import QObjectBase, QSingleton
from core.cpod.token_worker import TokenWorker
from core.lingq import LingqCollectionsWorker, LingqLessonWorker
from db import DatabaseManager
from keys import keys
from services.logger import Logger
from services.managers import (
    AudioDownloadManager,
    FFmpegTaskManager,
    LessonWorkFlowManager,
)
from services.network import NetworkThread, SessionManager, TokenManager
from services.settings import AppSettings
from utils.files import PathManager


class AppContext(QObjectBase, metaclass=QSingleton):
    check_token = Signal()

    def __init__(self):
        super().__init__()
        self.cookie_jar = requests.cookies.RequestsCookieJar()
        self.logger = Logger()
        self.session_manager = SessionManager()
        self.session_manager.bind_context(self)
        self.settings = AppSettings()
        self.setup_database()

        self.lingq_courses = []
        self.ffmpeg_task_manager = FFmpegTaskManager()
        self.audio_download_manager = AudioDownloadManager()
        self.lesson_workflow_manager = LessonWorkFlowManager(
            self.audio_download_manager, self.ffmpeg_task_manager
        )
        self.ffmpeg_task_manager.task_complete.connect(
            self.lesson_workflow_manager.on_task_completed
        )
        self.audio_download_manager.task_complete.connect(
            self.lesson_workflow_manager.on_task_completed
        )

        folder = PathManager.create_folder_in_app_data("playwright")
        self.ensure_playwright_browsers(folder)

        self.token_manager = TokenManager()
        self.token_manager.send_cookies.connect(
            self.session_manager.receive_playwright_cookies
        )
        self.check_token.connect(self.token_manager.check_token)
        self.setup_session()
        self.check_token.emit()

    def ensure_playwright_browsers(self, app_data_path):
        env = os.environ.copy()
        env["PLAYWRIGHT_BROWSERS_PATH"] = app_data_path

        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            env=env,
            check=True,
        )

    def setup_database(self):
        db = DatabaseManager("chineseDict.db")
        db.connect()
        db.create_tables_if_not_exist()
        db.create_anki_integration_record()
        db.disconnect()

    def setup_session(self):
        expired, domains = self.session_manager.load_session()
        if "lingq.com" not in domains or domains["lingq.com"]:
            #         print("session expired, getting new session")
            #         # TODO: remove py email and password dict - use keyring
            #         # TODO: check for keyring - if it doesnt exist -> notify user -> send them to settings page

            self.network_thread = NetworkThread(
                "POST",
                "https://www.lingq.com/en/accounts/login/",
                data={
                    "username": keys["email"],
                    "password": keys["lingqpw"],
                    "remember-me": "on",
                },
            )

            self.network_thread.response_sig.connect(self.session_response)
            self.network_thread.error_sig.connect(self.session_error)
            self.network_thread.start()
        else:
            pass
            # self.lingcollect_thread = QThread()
            # self.lingcollect = LingqLessonWorker()
            # self.lingcollect.moveToThread(self.lingcollect_thread)
            # self.lingcollect_thread.started.connect(self.lingcollect.do_work)
            # self.lingcollect.lingq_categories.connect(self.lingq_courses_response)
            # self.lingcollect.error.connect(self.lingq_courses_error)
            # self.lingcollect.finished.connect(self.lingcollect_thread.quit)
            # self.lingcollect_thread.finished.connect(
            #     self.lingcollect_thread.deleteLater
            # )
            # self.lingcollect_thread.start()

    def lingq_courses_response(self, collections):
        self.logging(f"Received {len(collections)} Courses from Lingq")
        print("recieved collections", collections)

    def lingq_courses_error(self, status_code):
        if status_code == 401:
            # TODO login in again
            pass

    def session_response(self, status, response):
        # print(response.text)
        print(response.cookies)
        lingq_logged = False
        for cookie in response.cookies:
            print(cookie.domain)
            if cookie.name == "csrftoken" and cookie.domain == "www.lingq.com":
                lingq_logged = True
                # TODO
        self.network_thread.quit()
        self.network_thread.deleteLater()

    def session_error(self, status, message):
        print(status, message)
        # TODO notify user - error logging them in
        print("There was an error logging you in. ")
