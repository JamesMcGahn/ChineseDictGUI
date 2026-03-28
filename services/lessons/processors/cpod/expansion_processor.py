from models.core import LessonTaskPayload
from models.dictionary import Lesson


class CPodLessonExpansionProcessor:
    def apply(self, lesson: Lesson, payload: LessonTaskPayload):
        expansion = payload.sentences
        lesson.lesson_parts.expansion = expansion
        lesson.lesson_parts.all_sentences.extend(expansion)
