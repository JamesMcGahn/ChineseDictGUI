from dataclasses import dataclass, field

from ..enums import AUDIODLPROVIDER
from .audio_item import AudioItem


@dataclass(frozen=True)
class AudioDownloadPayload:
    provider: AUDIODLPROVIDER = field(default=AUDIODLPROVIDER.HTTP)
    audio_urls: list[AudioItem] = field(default_factory=list)
    project_name: str = field(default=None)
