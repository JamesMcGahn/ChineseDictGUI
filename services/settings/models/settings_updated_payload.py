from dataclasses import dataclass
from typing import Any

from ..enums import SETTINGSCATEGORIES


@dataclass
class SettingUpdatedPayload:
    category: SETTINGSCATEGORIES
    field: str
    value: Any
