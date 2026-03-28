from models.core import LessonTaskPayload
from models.dictionary import Lesson


class CPodLessonVocabProcessor:
    def apply(self, lesson: Lesson, payload: LessonTaskPayload):
        words = payload.words
        lesson.lesson_parts.vocab = words
