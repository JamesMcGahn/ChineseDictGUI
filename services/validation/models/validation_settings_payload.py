from dataclasses import dataclass

from services.settings.enums import SETTINGSCATEGORIES


@dataclass
class SettingsValidatePayload:
    category: SETTINGSCATEGORIES
    field: str
    value: str | int | float | bool
