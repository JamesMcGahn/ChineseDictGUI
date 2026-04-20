from dataclasses import dataclass
from typing import Any

from services.settings.enums import FIELDSTATESTATUS, SETTINGSCATEGORIES


@dataclass
class SettingsValidateResponse:
    category: SETTINGSCATEGORIES
    field: str
    value: Any
    status: FIELDSTATESTATUS
    message: str | None = None
