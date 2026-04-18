from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .settings import AppSettings
    from .secure_settings import SecureCredentials
    from .models.settings_field_meta import SettingsFieldMeta


from dataclasses import fields


class SettingsRepository:

    def __init__(
        self, settings_storage: AppSettings, secure_storage: SecureCredentials
    ):
        self.settings = settings_storage
        self.secure_settings = secure_storage

    def load_section(self, section_dc):

        values = {}
        validated = {}
        self.settings.begin_group("settings")
        try:
            for field in fields(section_dc):
                meta: SettingsFieldMeta = field.metadata["meta"]

                key = f"{meta.category}/{meta.key}"
                validated_key = f"{meta.category}/{meta.key}-validated"

                if meta.secure:
                    value = self.secure_settings.get_creds(
                        "chinese-dict-secure-settings", key
                    )
                else:
                    value = self.settings.get_value(
                        key, default=field.default, type=field.type
                    )
                is_validated = self.settings.get_value(
                    validated_key, default=False, type=bool
                )

                if value is None:
                    value = field.default

                validated[field.name] = is_validated
                values[field.name] = value
        finally:
            self.settings.end_group()

        return section_dc(**values), validated

    def save_section(self, section_dc, section_validated: dict[str, bool]):
        try:
            self.settings.begin_group("settings")
            for field in fields(section_dc):
                meta: SettingsFieldMeta = field.metadata["meta"]

                key = f"{meta.category}/{meta.key}"
                validated_key = f"{meta.category}/{meta.key}-validated"

                is_validated = section_validated.get(field.name, False)
                value = getattr(section_dc, field.name)
                if meta.secure:
                    self.secure_settings.save_creds(
                        "chinese-dict-secure-settings", key, value
                    )
                else:
                    self.settings.set_value(key, value)

                self.settings.set_value(validated_key, is_validated)
        finally:
            self.settings.end_group()
