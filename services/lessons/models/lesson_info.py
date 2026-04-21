from dataclasses import dataclass, field

from base.enums import LESSONLEVEL


@dataclass
class LessonInfo:
    slug: str
    lesson_id: str | None = field(default=None, kw_only=True)
    title: str | None = field(default=None, kw_only=True)
    level: LESSONLEVEL | None = field(default=None, kw_only=True)
    hash_code: str | None = field(default=None, kw_only=True)
    lesson_audio: str | None = field(default=None, kw_only=True)
    dialogue_audio: str | None = field(default=None, kw_only=True)
