from models.core import LessonTaskPayload
from models.dictionary import Lesson

from ..base_lesson_processor import BaseLessonProcessor


class CPodLessonExpansionProcessor(BaseLessonProcessor):
    def apply(self, lesson: Lesson, payload: LessonTaskPayload):
        expansion = payload.sentences
        lesson.lesson_parts.expansion = expansion
        lesson.lesson_parts.all_sentences.extend(expansion)
