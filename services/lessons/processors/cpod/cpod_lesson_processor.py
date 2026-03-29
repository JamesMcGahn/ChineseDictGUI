from base.enums import LESSONTASK
from models.core import LessonTaskPayload
from models.dictionary import Lesson

from ..base_lesson_processor import BaseLessonProcessor
from .dialogue_processor import CPodLessonDialogueProcessor
from .expansion_processor import CPodLessonExpansionProcessor
from .grammar_processor import CPodLessonGrammarProcessor
from .info_processor import CPodLessonInfoProcessor
from .vocab_processor import CPodLessonVocabProcessor


class CpodLessonProcessor:

    def __init__(self):
        self.task_map: dict[LESSONTASK, BaseLessonProcessor] = {
            LESSONTASK.INFO: CPodLessonInfoProcessor(),
            LESSONTASK.DIALOGUE: CPodLessonDialogueProcessor(),
            LESSONTASK.EXPANSION: CPodLessonExpansionProcessor(),
            LESSONTASK.VOCAB: CPodLessonVocabProcessor(),
            LESSONTASK.GRAMMAR: CPodLessonGrammarProcessor(),
        }

    def apply(self, task: LESSONTASK, lesson: Lesson, payload: LessonTaskPayload):
        processor = self.task_map.get(task, None)
        if processor:
            processor.apply(lesson, payload)
