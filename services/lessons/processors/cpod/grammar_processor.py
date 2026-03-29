from models.core import LessonTaskPayload
from models.dictionary import Lesson

from ..base_lesson_processor import BaseLessonProcessor


class CPodLessonGrammarProcessor(BaseLessonProcessor):
    def apply(self, lesson: Lesson, payload: LessonTaskPayload):
        grammar_points = payload.grammar
        sentences = payload.sentences
        lesson.lesson_parts.grammar = grammar_points
        lesson.lesson_parts.all_sentences.extend(sentences)
