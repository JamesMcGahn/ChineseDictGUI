import math

from dals import LessonsDAL
from PySide6.QtCore import Signal

from base import QObjectBase
from models.dictionary import Lesson


class LessonReadService(QObjectBase):
    pagination = Signal(object, int, int, int, bool, bool)
    result = Signal(list)

    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.dal_l = LessonsDAL(self.db_manager)
