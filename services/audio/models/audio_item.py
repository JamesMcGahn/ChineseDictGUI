from dataclasses import dataclass, field

from ..enums.audio_type import AUDIOTYPE


@dataclass(frozen=True)
class AudioItem:
    ref_id: str
    file_name: str
    target_path: str
    source_url: str | None
    text: str | None
    category: AUDIOTYPE = field(default=AUDIOTYPE.DEFAULT)
    allow_fallback_tts: bool = False
    reuse_lookup_key: str | None = None
