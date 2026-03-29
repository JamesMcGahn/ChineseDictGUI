from models.core import LessonTaskPayload
from models.dictionary import Lesson


class BaseLessonProcessor:
    def apply(self, lesson: Lesson, payload: LessonTaskPayload):
        raise NotImplementedError
