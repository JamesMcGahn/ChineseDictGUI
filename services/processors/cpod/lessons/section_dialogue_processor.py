from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....lessons.models import LessonTaskPayload

from base.enums import UIEVENTTYPE
from base.events import SentencesEvent, UIEvent
from models.dictionary import Lesson
from pipelines.actions import EmitUIEventAction, WriteSentencesAction

from ...base_section_processor import BaseSectionProcessor
from ...models import ProcessorResponse


class DialogueProcessor(BaseSectionProcessor):
    def __init__(self):
        super().__init__()

    def apply(self, lesson: Lesson, payload: LessonTaskPayload):
        self.logging("Processing Dialogue...")
        dialogue = payload.sentences
        lesson.lesson_parts.dialogue = dialogue
        lesson.lesson_parts.all_sentences.extend(dialogue)

        return ProcessorResponse(
            actions=[
                EmitUIEventAction(
                    event=UIEvent(
                        event_type=UIEVENTTYPE.DISPLAY,
                        payload=SentencesEvent(
                            sentences=dialogue, check_duplicates=lesson.check_dup_sents
                        ),
                    )
                ),
                WriteSentencesAction(
                    write_path=lesson.storage_path,
                    file_name="dialogue.txt",
                    header="对话:",
                    data=dialogue,
                ),
            ]
        )
