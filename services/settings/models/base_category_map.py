from abc import ABC
from dataclasses import dataclass, fields
from typing import ClassVar

from .settings_field_meta import SettingsFieldMeta


@dataclass
class SettingsCategoryBase(ABC):
    schema_name: ClassVar[str]
    display_name: ClassVar[str]

    def __post_init__(self):
        self._meta_index = {
            f.name: f.metadata["meta"] for f in fields(self) if "meta" in f.metadata
        }

    def __init_subclass__(cls):
        super().__init_subclass__()

        if cls is SettingsCategoryBase:
            return
        if "schema_name" not in cls.__dict__:
            raise TypeError(f"{cls.__name__} must define schema_name")

        if "display_name" not in cls.__dict__:
            raise TypeError(f"{cls.__name__} must define display_name")

    def get_field_meta(self, field: str) -> SettingsFieldMeta:
        return self._meta_index.get(field)
