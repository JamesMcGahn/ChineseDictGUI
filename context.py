import os
import subprocess
import sys

import requests
from PySide6.QtCore import QThread, QTimer, Signal, Slot

from base import QObjectBase, QSingleton
from core.lingq import LingqLoginWorker
from keys import keys
from services.logger import Logger
from services.managers import (
    AudioDownloadManager,
    DatabaseServiceManager,
    FFmpegTaskManager,
    LessonWorkFlowManager,
    LingqWorkFlowManager,
)
from services.network import SessionManager, TokenManager
from services.settings import AppSettings
from utils.files import PathManager


class AppContext(QObjectBase, metaclass=QSingleton):
    check_token = Signal()
    lingq_logged_in = Signal(bool)
    appshutdown = Signal()

    def __init__(self):
        super().__init__()
        self.cookie_jar = requests.cookies.RequestsCookieJar()
        self.logger = Logger()
        self.session_manager = SessionManager()
        self.session_manager.bind_context(self)
        self.settings = AppSettings()
        self.session_manager.load_session()
        self.db = DatabaseServiceManager()

        self.ffmpeg_task_manager = FFmpegTaskManager()
        self.audio_download_manager = AudioDownloadManager()
        self.lingq_workflow_manager = LingqWorkFlowManager()
        self.lesson_workflow_manager = LessonWorkFlowManager(
            self.audio_download_manager,
            self.ffmpeg_task_manager,
            self.lingq_workflow_manager,
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

        self.appshutdown.connect(self.db.appshutdown)

    def ensure_playwright_browsers(self, app_data_path):
        env = os.environ.copy()
        env["PLAYWRIGHT_BROWSERS_PATH"] = app_data_path

        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            env=env,
            check=True,
        )

    # TODO Move to own Manager or Token Manager
    def setup_session(self):
        domains = self.session_manager.check_cookies()
        if "lingq.com" not in domains or domains["lingq.com"]:
            #         print("session expired, getting new session")
            #         # TODO: remove py email and password dict - use keyring
            #         # TODO: check for keyring - if it doesnt exist -> notify user -> send them to settings page

            self.lingq_login_thread = QThread()
            self.lingq_login_worker = LingqLoginWorker()
            self.lingq_login_worker.moveToThread(self.lingq_login_thread)
            self.lingq_login_thread.started.connect(self.lingq_logged_in)
            self.lingq_login_worker.lingq_logged_in(self)
            self.lingq_login_thread.start()

    def lingq_logged_in_response(self, logged_in: bool):
        pass
