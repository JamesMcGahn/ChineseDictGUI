from base import QObjectBase
from base.enums import PIPELINEJOBTYPE

from .lessons import CpodLessonProcessor


class CpodProcessorRegistry(QObjectBase):

    def __init__(self):
        super().__init__()

    def get_transformer(self, job_type: PIPELINEJOBTYPE):
        if PIPELINEJOBTYPE.LESSONS:
            return CpodLessonProcessor()
        raise NotImplementedError
