from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.settings.models import LogSettings

from PySide6.QtCore import Signal, Slot

from base import QWidgetBase
from models.settings import AppSettingsModel, LogSettingsModel
from services.settings.enums import SETTINGSCATEGORIES

from ...settings_ui_helper import SettingsUIHelper
from ...verify_settings import VerifySettings
from .tab_log_settings_ui import TabLogSettingsUI


class TabLogSettings(QWidgetBase):
    settings_field_updated = Signal(str, str, object)
    log_page_settings = Signal(str, bool, str, bool)
    save_log_settings_model = Signal(str, str, int, int, int, bool, str)

    def __init__(self, settings: LogSettings):
        super().__init__()
        self.tab_id = SETTINGSCATEGORIES.LOG
        self.settings_model = AppSettingsModel()
        self.settings_model.get_settings()
        self.log_settings = LogSettingsModel()

        self.sui = SettingsUIHelper()
        self.view = TabLogSettingsUI(self.tab_id, settings, self.sui)
        self.layout.addWidget(self.view)

        self.verify_settings = VerifySettings()

        # SIGNAL CONNECTIONS
        self.sui.send_to_verify.connect(self.verify_settings.verify_settings)
        self.sui.settings_field_updated.connect(self.settings_field_updated)

        self.save_log_settings_model.connect(self.log_settings.save_log_settings)
        self.verify_settings.verify_response_update_sui.connect(
            self.sui.verify_response_update
        )
        self.verify_settings.send_settings_update.connect(self.send_settings_update)
        self.verify_settings.change_verify_btn_disable.connect(
            self.sui.set_verify_btn_disable
        )

    @Slot(str, str)
    def send_settings_update(self, tab, key):
        if key in [
            "log_file_path",
            "log_file_name",
            "log_backup_count",
            "log_file_max_mbs",
            "log_keep_files_days",
            "log_level",
        ]:
            self.send_logs_page_setting()

    def send_logs_page_setting(self):
        log_file_path, lfp_verifed = self.settings_model.get_setting(
            self.tab_id, "log_file_path"
        )
        log_file_name, lfn_verifed = self.settings_model.get_setting(
            self.tab_id, "log_file_name"
        )
        log_file_max_mbs, _ = self.settings_model.get_setting(
            self.tab_id, "log_file_max_mbs"
        )
        log_backup_count, _ = self.settings_model.get_setting(
            self.tab_id, "log_backup_count"
        )
        log_keep_files_days, _ = self.settings_model.get_setting(
            self.tab_id, "log_keep_files_days"
        )
        log_level, _ = self.settings_model.get_setting(self.tab_id, "log_level")

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
            log_level,
        )
