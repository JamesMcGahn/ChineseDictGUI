import time
from dataclasses import dataclass, field

ALLOWED_PROVIDERS = {"cpod"}


@dataclass
class Lesson:
    provider: str
    url: str
    slug: str

    lesson_id: str | None = field(default=None, kw_only=True)
    title: str | None = field(default=None, kw_only=True)
    level: str | None = field(default=None, kw_only=True)

    scraped: bool = field(default=False, kw_only=True)
    scraped_at: int | None = field(default=None, kw_only=True)

    audio_saved: bool = field(default=False, kw_only=True)
    sentences_saved: bool = field(default=False, kw_only=True)
    transcript_saved: bool = field(default=False, kw_only=True)

    storage_path: str | None = field(default=None, kw_only=True)

    created_at: int = field(default_factory=lambda: int(time.time()), kw_only=True)
    updated_at: int | None = field(default=None, kw_only=True)

    def __post_init__(self):
        if self.provider not in ALLOWED_PROVIDERS:
            raise ValueError("Provider must be one of: cpod")
