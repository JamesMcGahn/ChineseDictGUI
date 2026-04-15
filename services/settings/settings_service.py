from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .settings_repository import SettingsRepository

from PySide6.QtCore import Signal, Slot

from base import QObjectBase

from .enums import SETTINGSCATEGORIES
from .models import AppSettings
from .models.map_log_settings import LogSettings


class SettingsService(QObjectBase):
    setting_changed = Signal(str, str, object)
    validation_changed = Signal(str, str, bool)

    def __init__(self, repo: SettingsRepository):
        super().__init__()
        self._repo = repo
        self._settings = None
        self._validated = {}

        self.sections = {SETTINGSCATEGORIES.LOG: LogSettings}

        self.load_settings()
        # REMOVE AFTER TESTING
        # self.get()
        # print(self.get_category(SETTINGSCATEGORIES.LOG))

    def load_settings(self):
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

    @Slot()
    def save_settings(self):
        self.logging("Saved Settings.")
        for category, dc in self.sections.items():
            validated = self._validated.get(category, {})
            self.logging(f"Saving {dc} settings.", "DEBUG")
            self._repo.save_section(dc, validated)
        self.logging("Saved Settings.")

    def get(self):
        print(self._settings)
        return self._settings

    def update_setting(self, category: SETTINGSCATEGORIES, field: str, value: Any):
        section = getattr(self._settings, category.value)
        setattr(section, field, value)
        self._validated.setdefault(category, {})
        self._validated[category][field] = False
        self.setting_changed.emit(category, field, value)

    def set_validated(self, category, field, is_valid):
        self._validated[category][field] = is_valid
        self.validation_changed.emit(category, field, is_valid)

    def is_validated(self, section: str, field: str) -> bool:
        return self._validated.get(section, {}).get(field, False)

    def get_category(self, category: SETTINGSCATEGORIES):
        attr = category.value
        return getattr(self._settings, attr)
