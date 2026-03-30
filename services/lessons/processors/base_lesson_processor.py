from models.core import LessonTaskPayload
from models.dictionary import Lesson
from models.services import ProcessorResponse


class BaseLessonProcessor:

    def apply(self, lesson: Lesson, payload: LessonTaskPayload) -> ProcessorResponse:
        raise NotImplementedError
