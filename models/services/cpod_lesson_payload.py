from dataclasses import dataclass, field


@dataclass
class CPodLessonPayload:
    url: str | None = field(default=None)
    slug: str | None = field(default=None)
    lesson_id: int | None = field(default=None)
