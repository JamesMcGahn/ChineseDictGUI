from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....lessons.models import LessonTaskPayload

from models.dictionary import Lesson
from pipelines.actions import WriteLessonPartsAction

from ...base_section_processor import BaseSectionProcessor
from ...models import ProcessorResponse


class CheckProcessor(BaseSectionProcessor):
    def __init__(self):
        super().__init__()

    def apply(self, lesson: Lesson, payload: LessonTaskPayload):
        lesson_parts = lesson.lesson_parts
        self.logging("Processing Lesson check...")
        return ProcessorResponse(
            actions=[
                WriteLessonPartsAction(
                    write_path=lesson.storage_path,
                    file_name="sentences.txt",
                    header="",
                    data=lesson_parts,
                ),
            ]
        )
