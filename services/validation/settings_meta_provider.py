from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from settings.enums import SETTINGSCATEGORIES
    from settings.models import SettingsFieldMeta


class SettingsMetaProvider(Protocol):
    def get_field_meta(
        self, category: SETTINGSCATEGORIES, field: str
    ) -> SettingsFieldMeta: ...
