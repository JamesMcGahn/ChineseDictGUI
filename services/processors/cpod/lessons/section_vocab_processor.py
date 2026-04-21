from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....lessons.models import LessonTaskPayload

from base.enums import UIEVENTTYPE
from base.events import UIEvent, WordsEvent
from models.dictionary import Lesson
from pipelines.actions import EmitUIEventAction, WriteWordsAction

from ...base_section_processor import BaseSectionProcessor
from ...models import ProcessorResponse


class VocabProcessor(BaseSectionProcessor):

    def __init__(self):
        super().__init__()

    def apply(self, lesson: Lesson, payload: LessonTaskPayload):
        self.logging("Processing Vocab...")
        words = payload.words
        lesson.lesson_parts.vocab = words

        return ProcessorResponse(
            actions=[
                EmitUIEventAction(
                    event=UIEvent(
                        event_type=UIEVENTTYPE.DISPLAY,
                        payload=WordsEvent(
                            words=words, check_duplicates=lesson.check_dup_words
                        ),
                    )
                ),
                WriteWordsAction(
                    write_path=lesson.storage_path,
                    file_name="vocab.txt",
                    header="词汇:",
                    data=words,
                ),
            ]
        )
