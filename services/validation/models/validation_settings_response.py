from dataclasses import dataclass

from services.settings.enums import SETTINGSCATEGORIES


@dataclass
class SettingsValidateResponse:
    category: SETTINGSCATEGORIES
    field: str
    is_valid: bool
