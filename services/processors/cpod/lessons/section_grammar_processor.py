from base.enums import UIEVENTTYPE
from models.core import LessonTaskPayload, UIEvent
from models.dictionary import Lesson
from models.pipelines import EmitUIEventAction, WriteGrammarAction
from models.services import ProcessorResponse

from ...base_section_processor import BaseSectionProcessor


class GrammarProcessor(BaseSectionProcessor):
    def __init__(self):
        super().__init__()

    def apply(self, lesson: Lesson, payload: LessonTaskPayload):
        self.logging("Processing Grammar...")
        grammar_points = payload.grammar
        sentences = payload.sentences
        lesson.lesson_parts.grammar = grammar_points
        lesson.lesson_parts.all_sentences.extend(sentences)
        return ProcessorResponse(
            actions=[
                EmitUIEventAction(
                    event=UIEvent(
                        event_type=UIEVENTTYPE.SENTENCES,
                        data=sentences,
                        check_duplicates=lesson.check_dup_sents,
                    )
                ),
                WriteGrammarAction(
                    write_path=lesson.storage_path,
                    file_name="grammar.txt",
                    header="语法:",
                    data=grammar_points,
                ),
            ]
        )
