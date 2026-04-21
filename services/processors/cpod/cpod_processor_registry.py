from base import QObjectBase
from pipelines.enums import PIPELINEJOBTYPE

from .lessons.lesson_processor import LessonProcessor


class CpodProcessorRegistry(QObjectBase):

    def __init__(self):
        super().__init__()

    def get_processor(self, job_type: PIPELINEJOBTYPE):
        if PIPELINEJOBTYPE.LESSONS:
            return LessonProcessor()
        raise NotImplementedError
