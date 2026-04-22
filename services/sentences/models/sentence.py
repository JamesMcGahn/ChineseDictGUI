from dataclasses import dataclass


@dataclass
class Sentence:
    chinese: str
    english: str
    pinyin: str
    audio: str
    level: str | None = None
    id: int = 0
    anki_audio: str | None = None
    anki_id: int | None = None
    anki_update: int | None = None
    local_update: int | None = None
    sent_type: str | None = None
    lesson: str | None = None
