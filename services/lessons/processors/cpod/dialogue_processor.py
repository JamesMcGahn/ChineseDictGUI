from models.core import LessonTaskPayload
from models.dictionary import Lesson

from ..base_lesson_processor import BaseLessonProcessor


class CPodLessonDialogueProcessor(BaseLessonProcessor):
    def apply(self, lesson: Lesson, payload: LessonTaskPayload):
        dialogue = payload.sentences
        if not dialogue:
            return
        lesson.lesson_parts.dialogue = dialogue
        lesson.lesson_parts.all_sentences.extend(dialogue)
