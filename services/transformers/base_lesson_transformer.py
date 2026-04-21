from base import QObjectBase
from base.enums import LESSONTASK
from models.dictionary import Lesson
from services.lessons.models import LessonTaskPayload

from .base_section_transformer import BaseSectionTransformer


class BaseLessonTransformer(QObjectBase):

    def __init__(self):
        super().__init__()

        self.task_map: dict[LESSONTASK, BaseSectionTransformer] = {}

    def process(self, task: LESSONTASK, lesson: Lesson, data) -> LessonTaskPayload:
        handler = self.task_map.get(task, None)
        if not handler:
            return NotImplementedError
        return handler.process(lesson, data)
