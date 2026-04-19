from dataclasses import dataclass, field, fields

from .map_log_settings import LogSettings
from .map_whisper_settings import WhisperSettings


@dataclass
class AppSettings:
    log: LogSettings = field(default_factory=LogSettings)
    whisper: WhisperSettings = field(default_factory=WhisperSettings)

    def get_fields_list(self):
        return [f for f in fields(self)]
