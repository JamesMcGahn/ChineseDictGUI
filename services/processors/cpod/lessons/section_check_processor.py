from models.core import LessonTaskPayload
from models.dictionary import Lesson
from models.pipelines import WriteLessonPartsAction
from models.services import ProcessorResponse

from ...base_section_processor import BaseSectionProcessor


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
