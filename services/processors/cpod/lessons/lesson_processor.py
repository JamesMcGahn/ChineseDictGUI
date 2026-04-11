from base.enums import LESSONTASK

from ...base_lesson_processor import BaseLessonProcessor
from ...base_section_processor import BaseSectionProcessor
from .section_check_processor import CheckProcessor
from .section_dialogue_processor import DialogueProcessor
from .section_expansion_processor import ExpansionProcessor
from .section_grammar_processor import GrammarProcessor
from .section_info_processor import InfoProcessor
from .section_vocab_processor import VocabProcessor


class LessonProcessor(BaseLessonProcessor):

    def __init__(self):
        super().__init__()
        self.task_map: dict[LESSONTASK, BaseSectionProcessor] = {
            LESSONTASK.INFO: InfoProcessor(),
            LESSONTASK.DIALOGUE: DialogueProcessor(),
            LESSONTASK.EXPANSION: ExpansionProcessor(),
            LESSONTASK.VOCAB: VocabProcessor(),
            LESSONTASK.GRAMMAR: GrammarProcessor(),
            LESSONTASK.CHECK: CheckProcessor(),
        }
