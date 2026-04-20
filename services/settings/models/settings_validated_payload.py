from dataclasses import dataclass

from ..enums import SETTINGSCATEGORIES


@dataclass
class SettingValidatedPayload:
    category: SETTINGSCATEGORIES
    field: str
    is_valid: bool
