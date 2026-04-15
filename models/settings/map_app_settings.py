from dataclasses import dataclass, field

from .map_log_settings import LogSettings


@dataclass
class AppSettings:
    log: LogSettings = field(default_factory=LogSettings)
