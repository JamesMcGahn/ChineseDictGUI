from PySide6.QtCore import Signal

from base import QObjectBase

from ..db_manager import DatabaseManager
from .lesson_read_service import LessonReadService
from .sents_read_service import SentsReadService
from .words_read_service import WordsReadService


class DBReadService(QObjectBase):
    pagination = Signal(object, int, int, int, bool, bool)
    result = Signal(list)

    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager("chineseDict.db")
        self.words_read_serv = WordsReadService(self.db_manager)
        self.sents_read_serv = SentsReadService(self.db_manager)
        self.lesson_read_serv = LessonReadService(self.db_manager)

        # CONNECTIONS
        self.words_read_serv.result.connect(self.result)
        self.words_read_serv.pagination.connect(self.pagination)
        self.sents_read_serv.result.connect(self.result)
        self.sents_read_serv.pagination.connect(self.pagination)
        self.lesson_read_serv.result.connect(self.result)
        self.lesson_read_serv.pagination.connect(self.pagination)

    @property
    def words(self) -> WordsReadService:
        return self.words_read_serv

    @property
    def sentences(self) -> SentsReadService:
        return self.sents_read_serv

    @property
    def lessons(self) -> LessonReadService:
        return self.lesson_read_serv
