from dataclasses import dataclass

from ..enums import FIELDSTATESTATUS, SETTINGSCATEGORIES


@dataclass
class FieldStateEvent:
    category: SETTINGSCATEGORIES
    field: str
    status: FIELDSTATESTATUS
    message: str | None
