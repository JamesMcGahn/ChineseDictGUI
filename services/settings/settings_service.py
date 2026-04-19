from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .settings_repository import SettingsRepository

from copy import deepcopy

from PySide6.QtCore import Signal, Slot

from base import QObjectBase

from .enums import SETTINGSCATEGORIES
from .models import AppSettings
from .models.base_category_map import SettingsCategoryBase
from .models.map_app_settings import AppSettings as AppSettingsMap
from .models.map_log_settings import LogSettings
from .models.map_whisper_settings import WhisperSettings


class SettingsService(QObjectBase):
    setting_changed = Signal(str, str, object)
    validation_changed = Signal(str, str, bool)

    def __init__(self, repo: SettingsRepository):
        super().__init__()
        self._repo = repo
        self._settings: AppSettingsMap = None
        self._validated: dict[SETTINGSCATEGORIES, dict[str, bool]] = {}
        self.sections: dict[SETTINGSCATEGORIES, SettingsCategoryBase] = {
            SETTINGSCATEGORIES.LOG: LogSettings,
            SETTINGSCATEGORIES.WHISPER: WhisperSettings,
        }
        self._settings_loaded = False

        self.load_settings()
        # REMOVE AFTER TESTING
        # self.get()
        # print(self.get_category(SETTINGSCATEGORIES.LOG))

    def load_settings(self):
        if self._settings_loaded:
            return

        self._settings = AppSettings()
        self._validated = {}
        self.logging("Loading Settings from Repository")
        for category, dc in self.sections.items():
            self.logging(f"Loading {dc} settings.", "DEBUG")
            cat_settings, validated = self._repo.load_section(dc)
            attr = category.value
            setattr(self._settings, attr, cat_settings)
            self._validated[category] = validated
        self.logging("Successfully Loaded Settings from Repository")
        self._settings_loaded = True

    @Slot()
    def save_settings(self):
        self.logging("Saving Settings.")
        for category, dc in self.sections.items():
            validated = self._validated.get(category, {})
            self.logging(f"Saving {dc} settings.", "DEBUG")
            section = getattr(self._settings, category)
            self._repo.save_section(section, validated)
        self.logging("Settings save sucessfully.")

    def get_settings(self) -> AppSettingsMap:
        print(self._settings)
        return deepcopy(self._settings)

    def get_validations(self) -> dict[SETTINGSCATEGORIES, dict[str, bool]]:
        return deepcopy(self._validated)

    def update_setting(self, category: SETTINGSCATEGORIES, field: str, value: Any):
        section = getattr(self._settings, category)
        setattr(section, field, value)
        self._validated.setdefault(category, {})
        self._validated[category][field] = False
        self.setting_changed.emit(category, field, value)

    def set_validated(self, category, field, is_valid):
        self._validated[category][field] = is_valid
        self.validation_changed.emit(category, field, is_valid)

    def is_validated(self, section: str, field: str) -> bool:
        return self._validated.get(section, {}).get(field, False)

    def get_category(self, category: SETTINGSCATEGORIES) -> SettingsCategoryBase:
        # attr = category.value
        cat = getattr(self._settings, category, None)
        if not cat:
            msg = f"Cannot Find Category: {category}"
            self.logging(msg)
            raise ValueError(msg)
        return cat

    def get_field_meta(self, category: SETTINGSCATEGORIES, field: str):
        field_category = self.get_category(category)
        meta = field_category.get_field_meta(field)
        if not meta:
            msg = f"Cannot find {field} in {category} meta dictionary"
            self.logging(msg, "ERROR")
            raise ValueError(msg)
        return meta
