from models.core import LessonTaskPayload
from models.dictionary import Lesson
from models.pipelines import WriteLessonPartsAction
from models.services import ProcessorResponse

from ..base_lesson_processor import BaseLessonProcessor


class CPodLessonCheckProcessor(BaseLessonProcessor):
    def apply(self, lesson: Lesson, payload: LessonTaskPayload):
        lesson_parts = lesson.lesson_parts
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
