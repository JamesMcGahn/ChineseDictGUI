from PySide6.QtCore import Signal

from base import QObjectBase

from ..db_manager import DatabaseManager
from .anki_integration_read_service import AnkiIntegrationReadService
from .lesson_read_service import LessonReadService
from .sents_read_service import SentsReadService
from .words_read_service import WordsReadService


class DBReadService(QObjectBase):
    pagination = Signal(object, int, int, int, bool, bool)
    result = Signal(list)

    def __init__(self, db_name: str = "chineseDict.db"):
        super().__init__()
        self.db_name = db_name

    def _db_manager(self) -> DatabaseManager:
        return DatabaseManager(self.db_name)

    @property
    def words(self) -> WordsReadService:
        return WordsReadService(self._db_manager())

    @property
    def sentences(self) -> SentsReadService:
        return SentsReadService(self._db_manager())

    @property
    def lessons(self) -> LessonReadService:
        return LessonReadService(self._db_manager())

    @property
    def anki_integration(self) -> AnkiIntegrationReadService:
        return AnkiIntegrationReadService(self._db_manager())
