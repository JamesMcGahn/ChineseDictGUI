from models.core import LessonTaskPayload
from models.dictionary import Lesson

from ..base_lesson_processor import BaseLessonProcessor


class CPodLessonVocabProcessor(BaseLessonProcessor):
    def apply(self, lesson: Lesson, payload: LessonTaskPayload):
        words = payload.words
        lesson.lesson_parts.vocab = words
