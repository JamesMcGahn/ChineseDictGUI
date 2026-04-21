from base import QObjectBase
from models.dictionary import Lesson

from ..lessons.models import LessonTaskPayload
from .models import ProcessorResponse


class BaseSectionProcessor(QObjectBase):
    def __init__(self):
        super().__init__()

    def apply(self, lesson: Lesson, payload: LessonTaskPayload) -> ProcessorResponse:
        raise NotImplementedError
