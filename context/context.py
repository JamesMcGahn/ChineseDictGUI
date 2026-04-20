import os
import subprocess
import sys

import requests
from PySide6.QtCore import QThread, QTimer, Signal, Slot

from base import QObjectBase, QSingleton
from base.enums import PROVIDERS
from controllers import SettingsController
from core.lingq import LingqLoginWorker
from keys import keys
from models.pipelines import PipelineServiceContainer
from services.logger import Logger
from services.managers import (
    AudioDownloadManager,
    CpodServiceManager,
    DatabaseServiceManager,
    FFmpegTaskManager,
    LessonPipelineManager,
    LingqWorkFlowManager,
)
from services.network import SessionManager
from services.network.auth import AuthService
from services.network.session import SessionRegistry
from services.settings import (
    AppSettings,
    SecureCredentials,
    SettingsRepository,
    SettingsService,
)
from services.settings.enums import SETTINGSCATEGORIES
from services.validation import ValidationService
from utils.files import PathManager

# TODO Connect Logger settings changes


class AppContext(QObjectBase, metaclass=QSingleton):
    check_token = Signal()
    lingq_logged_in = Signal(bool)
    appshutdown = Signal()
    task_complete = Signal(object)
    add_to_db_write_queue = Signal(object, object)

    setting_updated = Signal(object)

    def __init__(self):
        super().__init__()
        self.cookie_jar = requests.cookies.RequestsCookieJar()
        self.logger = Logger()
        self.settings = AppSettings()
        self.secure_settings = SecureCredentials()
        self.settings_repo = SettingsRepository(self.settings, self.secure_settings)
        self.settings_manager = SettingsService(repo=self.settings_repo)

        log_settings = self.settings_manager.get_category(SETTINGSCATEGORIES.LOG)
        self.logger.load_settings(log_settings)
        self.logger.start_up()
        # TODO: Remove when Migration is Completed
        self.session_manager = SessionManager()
        self.session_manager.bind_context(self)

        self.session_manager.load_session()
        self.db = DatabaseServiceManager()

        self.validation_service = ValidationService(
            settings_meta_provider=self.settings_manager
        )
        self.session_registry = SessionRegistry()
        self.auth_service = AuthService(session_registry=self.session_registry)
        self.ffmpeg_task_manager = FFmpegTaskManager()
        self.audio_download_manager = AudioDownloadManager()
        self.lingq_workflow_manager = LingqWorkFlowManager(
            session_registry=self.session_registry
        )
        self.cpod_lesson_manager = CpodServiceManager(
            session_registry=self.session_registry
        )
        self.lesson_pipeline_manager = LessonPipelineManager(
            service_cont=PipelineServiceContainer(
                db=self.db,
                audio=self.audio_download_manager,
                ffmpeg=self.ffmpeg_task_manager,
                lingq=self.lingq_workflow_manager,
                session=self.session_registry,
                cpod_lesson=self.cpod_lesson_manager,
            )
        )

        ## Controllers
        self.settings_controller = SettingsController(
            settings_service=self.settings_manager,
            validation_service=self.validation_service,
        )

        folder = PathManager.create_folder_in_app_data("playwright")
        self.ensure_playwright_browsers(folder)

        self.session_registry.pre_load_providers([PROVIDERS.CPOD])
        self.auth_service.validation_status.connect(self.validate_status_result)
        # TODO remove from here
        self.auth_service.ensure_authenticated(PROVIDERS.CPOD)
        self.auth_service.ensure_authenticated(PROVIDERS.LINGQ)

        self.appshutdown.connect(self.db.appshutdown)
        self.appshutdown.connect(self.session_registry.save_all)
        self.appshutdown.connect(self.settings_manager.save_settings)

        # CONNECTIONS
        ## SETTINGS
        self.settings_controller.setting_updated.connect(self.setting_updated)
        self.setting_updated.connect(self.logger.received_settings_change)
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
