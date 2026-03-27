from dataclasses import dataclass

ALLOWED_PROVIDERS = {"cpod"}


@dataclass(frozen=True)
class LessonWorkFlowRequest:
    provider: str
    url: str
    slug: str | None
    check_dup_sents: bool
    transcribe_lesson: bool

    def __post_init__(self):
        if self.provider not in ALLOWED_PROVIDERS:
            raise ValueError("Provider must be one of: cpod")
