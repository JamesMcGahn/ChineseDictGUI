from dataclasses import dataclass

from ..enums import LESSONPROVIDERS


@dataclass(frozen=True)
class LessonWorkFlowRequest:
    provider: LESSONPROVIDERS
    url: str
    slug: str | None
    check_dup_sents: bool
    check_dup_words: bool
    transcribe_lesson: bool
