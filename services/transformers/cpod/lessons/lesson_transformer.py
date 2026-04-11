from base.enums import LESSONTASK
from models.dictionary import Lesson

from ...base_lesson_transformer import BaseLessonTransformer
from ...base_section_transformer import BaseSectionTransformer
from .section_dialogue_transformer import DialogueTransformer
from .section_expansion_transformer import ExpansionTransformer
from .section_grammar_transformer import GrammarTransformer
from .section_lesson_info_transformer import LessonInfoTransformer
from .section_vocab_transformer import VocabTransformer


class LessonTransformer(BaseLessonTransformer):

    def __init__(self):
        super().__init__()

        self.task_map: dict[LESSONTASK, BaseSectionTransformer] = {
            LESSONTASK.INFO: LessonInfoTransformer(),
            LESSONTASK.GRAMMAR: GrammarTransformer(),
            LESSONTASK.DIALOGUE: DialogueTransformer(),
            LESSONTASK.VOCAB: VocabTransformer(),
            LESSONTASK.EXPANSION: ExpansionTransformer(),
        }

    def process(self, task: LESSONTASK, lesson: Lesson, data):
        handler = self.task_map.get(task, None)
        if not handler:
            return NotImplementedError
        return handler.process(lesson, data)
