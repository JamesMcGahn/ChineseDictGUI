import os

from PySide6.QtCore import QTimer, Signal, Slot

from base import QWidgetBase
from models.settings import AppSettingsModel, LogSettingsModel

from .field_registry import FieldRegistry
from .page_settings_ui import PageSettingsUI
from .settings_ui_helper import SettingsUIHelper
from .verify_settings import VerifySettings


class PageSettings(QWidgetBase):
    main_app_settings = Signal(bool, bool)
    import_page_settings = Signal(str, bool)
    audio_page_settings = Signal(str, bool, str, bool)
    sync_page_settings = Signal(str, bool, str, bool)
    log_page_settings = Signal(str, bool, str, bool)
    define_page_settings = Signal(str, bool)
    save_log_settings_model = Signal(str, str, int, int, int, bool)

    def __init__(self):
        super().__init__()

        self.settings_model = AppSettingsModel()
        self.settings_model.get_settings()
        self.log_settings = LogSettingsModel()

        self.sui = SettingsUIHelper()
        self.view = PageSettingsUI(self.sui)
        self.layout.addWidget(self.view)

        self.verify_settings = VerifySettings()
        self.timers = {}
        self.home_directory = os.path.expanduser("~")
        self.field_registery = FieldRegistry()
        print("home", self.home_directory)
        # self.get_settings("ALL", setText=True)
        self.sui.send_to_verify.connect(self.verify_settings.verify_settings)
        self.save_log_settings_model.connect(self.log_settings.save_log_settings)
        self.verify_settings.verify_response_update_sui.connect(
            self.sui.verify_response_update
        )

        self.verify_settings.send_settings_update.connect(self.send_settings_update)

        self.verify_settings.change_verify_btn_disable.connect(
            self.sui.set_verify_btn_disable
        )

        self.view.secure_setting_change.connect(self.sui.handle_secure_setting_change)

    def send_settings_update(self, tab, key):

        # Import Page settings
        if key in ["apple_note_name"]:
            self.send_import_page_settings()
        elif key in ["audio_path", "google_api_key"]:
            self.send_audio_page_settings()
        elif key in ["anki_deck_name", "anki_model_name"]:
            self.send_sync_page_settings()
        elif key in [
            "log_file_path",
            "log_file_name",
            "log_backup_count",
            "log_file_max_mbs",
            "log_keep_files_days",
        ]:
            self.send_logs_page_setting()
        elif key in ["dictionary_source", "merriam_webster_api_key"]:
            self.send_define_page_settings()
        elif key in ["auto_save_on_close"]:
            self.send_main_app_settings()

    def send_main_app_settings(self):
        auto_save_on_close, auto_save_on_close_verifed = (
            self.settings_model.get_setting("auto_save_on_close")
        )
        self.main_app_settings.emit(auto_save_on_close, auto_save_on_close_verifed)

    def send_define_page_settings(self):
        dictionary_source, dict_source_verifed = self.settings_model.get_setting(
            "dictionary_source"
        )

        self.define_page_settings.emit(
            dictionary_source,
            dict_source_verifed,
        )

    def send_import_page_settings(self):
        apple_note_name, ann_verifed = self.settings_model.get_setting(
            "apple_note_name"
        )
        self.import_page_settings.emit(apple_note_name, ann_verifed)

    def send_audio_page_settings(self):
        google_api_key, gak_verifed = self.settings_model.get_setting("google_api_key")
        anki_audio_path, aap_verifed = self.settings_model.get_setting(
            "anki_audio_path"
        )

        self.audio_page_settings.emit(
            google_api_key,
            gak_verifed,
            anki_audio_path,
            aap_verifed,
        )

    def send_sync_page_settings(self):
        anki_deck_name, adn_verifed = self.settings_model.get_setting("anki_deck_name")
        anki_model_name, amn_verifed = self.settings_model.get_setting(
            "anki_model_name"
        )

        self.sync_page_settings.emit(
            anki_deck_name, adn_verifed, anki_model_name, amn_verifed
        )

    def send_logs_page_setting(self):
        log_file_path, lfp_verifed = self.settings_model.get_setting("log_file_path")
        log_file_name, lfn_verifed = self.settings_model.get_setting("log_file_name")
        log_file_max_mbs, _ = self.settings_model.get_setting("log_file_max_mbs")
        log_backup_count, _ = self.settings_model.get_setting("log_backup_count")
        log_keep_files_days, _ = self.settings_model.get_setting("log_keep_files_days")

        self.log_page_settings.emit(
            log_file_path,
            lfp_verifed,
            log_file_name,
            lfn_verifed,
        )
        self.save_log_settings_model.emit(
            log_file_path,
            log_file_name,
            log_file_max_mbs,
            log_backup_count,
            log_keep_files_days,
            False,
        )

    @Slot()
    def send_all_settings(self):
        print("send all settings")
        self.send_import_page_settings()
        self.send_audio_page_settings()
        self.send_sync_page_settings()
        self.send_logs_page_setting()
        self.send_define_page_settings()
        self.send_main_app_settings()
