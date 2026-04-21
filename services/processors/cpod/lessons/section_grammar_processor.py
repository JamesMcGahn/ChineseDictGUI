from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....lessons.models import LessonTaskPayload

from base.enums import UIEVENTTYPE
from base.events import SentencesEvent, UIEvent
from models.dictionary import Lesson
from pipelines.actions import EmitUIEventAction, WriteGrammarAction

from ...base_section_processor import BaseSectionProcessor
from ...models import ProcessorResponse


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
                        event_type=UIEVENTTYPE.DISPLAY,
                        payload=SentencesEvent(
                            sentences=sentences, check_duplicates=lesson.check_dup_sents
                        ),
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
