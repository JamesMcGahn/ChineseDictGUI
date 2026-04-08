import os
import subprocess
import sys

import requests
from PySide6.QtCore import QThread, QTimer, Signal, Slot

from base import QObjectBase, QSingleton
from base.enums import PROVIDERS
from core.lingq import LingqLoginWorker
from keys import keys
from models.pipelines import PipelineServiceContainer
from services.logger import Logger
from services.managers import (
    AudioDownloadManager,
    DatabaseServiceManager,
    FFmpegTaskManager,
    LessonPipelineManager,
    LingqWorkFlowManager,
)
from services.network import SessionManager
from services.network.auth import AuthService
from services.network.session import SessionRegistry
from services.settings import AppSettings
from utils.files import PathManager


class AppContext(QObjectBase, metaclass=QSingleton):
    check_token = Signal()
    lingq_logged_in = Signal(bool)
    appshutdown = Signal()
    task_complete = Signal(object)
    add_to_db_write_queue = Signal(object, object)

    def __init__(self):
        super().__init__()
        self.cookie_jar = requests.cookies.RequestsCookieJar()
        self.logger = Logger()
        self.session_manager = SessionManager()
        self.session_manager.bind_context(self)
        self.settings = AppSettings()
        self.session_manager.load_session()
        self.db = DatabaseServiceManager()

        self.session_registry = SessionRegistry()
        self.auth_service = AuthService(session_registry=self.session_registry)
        self.ffmpeg_task_manager = FFmpegTaskManager()
        self.audio_download_manager = AudioDownloadManager()
        self.lingq_workflow_manager = LingqWorkFlowManager(
            session_registry=self.session_registry
        )
        self.lesson_pipeline_manager = LessonPipelineManager(
            service_cont=PipelineServiceContainer(
                db=self.db,
                audio=self.audio_download_manager,
                ffmpeg=self.ffmpeg_task_manager,
                lingq=self.lingq_workflow_manager,
                session=self.session_registry,
            )
        )

        folder = PathManager.create_folder_in_app_data("playwright")
        self.ensure_playwright_browsers(folder)

        self.session_registry.pre_load_providers([PROVIDERS.CPOD])
        self.auth_service.validation_status.connect(self.validate_status_result)
        self.auth_service.validate(PROVIDERS.CPOD)
        self.auth_service.validate(PROVIDERS.LINGQ)

        self.appshutdown.connect(self.db.appshutdown)
        self.appshutdown.connect(self.session_registry.save_all)

        # CONNECTIONS
        ## TASK COMPLETE
        self.ffmpeg_task_manager.task_complete.connect(self.task_complete)
        self.audio_download_manager.task_complete.connect(self.task_complete)
        self.db.task_complete.connect(self.task_complete)
        self.lingq_workflow_manager.task_complete.connect(self.task_complete)
        # self.task_complete.connect(self.lesson_workflow_manager.on_task_completed)

        self.add_to_db_write_queue.connect(self.db.write)

    def ensure_playwright_browsers(self, app_data_path):
        env = os.environ.copy()
        env["PLAYWRIGHT_BROWSERS_PATH"] = app_data_path

        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            env=env,
            check=True,
        )

    def validate_status_result(self, provider, status):
        print(provider, status)

    # TODO Move to own Manager or Token Manager
    def setup_session(self):
        domains = self.session_manager.check_cookies()
        if "lingq.com" not in domains or domains["lingq.com"]:
            #         print("session expired, getting new session")
            #         # TODO: remove py email and password dict - use keyring
            #         # TODO: check for keyring - if it doesnt exist -> notify user -> send them to settings page
            pass
            # self.lingq_login_thread = QThread()
            # self.lingq_login_worker = LingqLoginWorker()
            # self.lingq_login_worker.moveToThread(self.lingq_login_thread)
            # self.lingq_login_thread.started.connect(self.lingq_login_worker.do_work)
            # self.lingq_login_worker.lingq_logged_in.connect(
            #     self.lingq_logged_in_response
            # )
            # self.lingq_login_worker.done.connect(self.deleteLater)
            # self.lingq_login_worker.done.connect(self.lingq_login_thread.quit)
            # self.lingq_login_thread.finished.connect(
            #     self.lingq_login_thread.deleteLater
            # )
            # self.lingq_login_thread.start()

    def lingq_logged_in_response(self, logged_in: bool):
        print(f"logged in lingq: {logged_in}")
