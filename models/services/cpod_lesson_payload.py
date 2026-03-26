from dataclasses import dataclass, field


@dataclass
class CPodLessonPayload:
    url: str
    slug: str | None = field(default=None)
