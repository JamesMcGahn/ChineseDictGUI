from dataclasses import dataclass


@dataclass
class Word:
    chinese: str
    definition: str
    pinyin: str
    audio: str
    level: str | None = None
    id: int = 0
    anki_audio: str | None = None
    anki_id: str | None = None
    anki_update: str | None = None
    local_update: str | None = None
