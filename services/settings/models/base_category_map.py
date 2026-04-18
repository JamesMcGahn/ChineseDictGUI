from dataclasses import dataclass, fields

from .settings_field_meta import SettingsFieldMeta


@dataclass
class SettingsCategoryBase:
    def __post_init__(self):
        self._meta_index = {
            f.name: f.metadata["meta"] for f in fields(self) if "meta" in f.metadata
        }

    def get_field_meta(self, field: str) -> SettingsFieldMeta:
        return self._meta_index.get(field)
