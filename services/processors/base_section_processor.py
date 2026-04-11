from base import QObjectBase
from models.core import LessonTaskPayload
from models.dictionary import Lesson
from models.services import ProcessorResponse


class BaseSectionProcessor(QObjectBase):
    def __init__(self):
        super().__init__()

    def apply(self, lesson: Lesson, payload: LessonTaskPayload) -> ProcessorResponse:
        raise NotImplementedError
