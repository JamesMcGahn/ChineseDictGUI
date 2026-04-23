from dataclasses import dataclass, field
from uuid import uuid4

from ..enums import SENTTYPE


@dataclass
class Sentence:
    chinese: str = field(kw_only=True)
    pinyin: str = field(kw_only=True)
    english: str = field(kw_only=True)
    audio_link: str = field(kw_only=True)
    level: str | None = field(kw_only=True, default=None)
    id: int = field(kw_only=True, default=0)
    anki_audio: str | None = field(kw_only=True, default=None)
    anki_id: int | None = field(kw_only=True, default=None)
    anki_update: int | None = field(kw_only=True, default=None)
    local_update: int | None = field(kw_only=True, default=None)
    sent_type: SENTTYPE = field(kw_only=True, default=SENTTYPE.OTHER)
    lesson: str | None = field(kw_only=True, default=None)

    runtime_id: str = field(default_factory=lambda: str(uuid4()))
    staging_path: str | None = field(kw_only=True, default=None)
    storage_path: str | None = field(kw_only=True, default=None)
