from dataclasses import dataclass, field, fields

from .map_log_settings import LogSettings


@dataclass
class AppSettings:
    log: LogSettings = field(default_factory=LogSettings)

    def get_fields_list(self):
        return [f for f in fields(self)]
