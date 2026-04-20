from dataclasses import dataclass

from ..models import SettingUpdatedPayload


@dataclass
class SettingUpdatedEvent(SettingUpdatedPayload): ...
