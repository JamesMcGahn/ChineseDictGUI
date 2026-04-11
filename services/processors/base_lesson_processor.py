from base import QObjectBase
from base.enums import LESSONTASK
from models.core import LessonTaskPayload
from models.dictionary import Lesson
from models.services import ProcessorResponse

from .base_section_processor import BaseSectionProcessor


class BaseLessonProcessor(QObjectBase):

    def __init__(self):
        super().__init__()
        self.task_map: dict[LESSONTASK, BaseSectionProcessor] = {}

    def apply(
        self, task: LESSONTASK, lesson: Lesson, payload: LessonTaskPayload
    ) -> ProcessorResponse:
        processor = self.task_map.get(task, None)
        if not processor:
            msg = f"Processor for {task} is not implemented"
            self.logging(msg, "ERROR")
            raise NotImplementedError(msg)
        return processor.apply(lesson, payload)
