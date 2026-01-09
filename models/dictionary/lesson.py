import time
from dataclasses import dataclass, field

from base.enums import LESSONLEVEL, LESSONSTATUS, LESSONTASK

from .lesson_parts import LessonParts

ALLOWED_PROVIDERS = {"cpod"}


@dataclass
class Lesson:
    provider: str
    url: str
    slug: str
    status: LESSONSTATUS = field(default=LESSONSTATUS.CREATED, kw_only=True)
    task: LESSONTASK | None = field(default=None, kw_only=True)
    lesson_id: str | None = field(default=None, kw_only=True)
    title: str | None = field(default=None, kw_only=True)
    level: LESSONLEVEL | None = field(default=None, kw_only=True)
    hash_code: str | None = field(default=None, kw_only=True)

    storage_path: str | None = field(default=None, kw_only=True)

    created_at: int = field(default_factory=lambda: int(time.time()), kw_only=True)
    updated_at: int | None = field(default=None, kw_only=True)

    # NOT SAVED TO DB
    check_dup_sents: bool = False
    transcribe_lesson: bool = True
    lesson_parts: LessonParts = field(default_factory=LessonParts)
    queue_id: str | None = field(default=None, kw_only=True)

    def __post_init__(self):
        if self.provider not in ALLOWED_PROVIDERS:
            raise ValueError("Provider must be one of: cpod")
