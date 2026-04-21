from dataclasses import dataclass

from services.lessons.enums import LESSONPROVIDERS


@dataclass(frozen=True)
class LessonPipelinePayload:
    queue_id: str
    provider: LESSONPROVIDERS
    url: str
    check_dup_sents: bool
    check_dup_words: bool
    transcribe_lesson: bool
    create_lingq_lessons: bool
