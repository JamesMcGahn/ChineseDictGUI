from dataclasses import dataclass, field

from .audio_item import AudioItem


@dataclass(frozen=True)
class AudioDownloadPayload:
    audio_urls: list[AudioItem] = field(default_factory=list)
    export_path: str = field(default="./")
    project_name: str = field(default=None)
    update_db: bool = field(default=False, kw_only=True)
