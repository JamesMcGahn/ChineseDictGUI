import math

from PySide6.QtCore import Signal

from models.dictionary import Sentence
from models.services.database import DBResponse
from models.services.database.read import AnkiExport, Exists, PaginationResponse

from ..dals import SentsDAL
from .base_read_service import BaseReadService


class SentsReadService(BaseReadService[Sentence]):
    pagination = Signal(object, int, int, int, bool, bool)
    result = Signal(list)

    def __init__(self, db_manager):
        super().__init__(db_manager=db_manager)
        self.dal = SentsDAL(self.db_manager)

    def exists(self, items):
        sentences_strings = [sentence.chinese for sentence in items]
        rows = self.dal.exists(sentences_strings)
        sentences = [
            Sentence(
                sent[1],
                sent[2],
                sent[3],
                sent[4],
                sent[5],
                sent[0],
                sent[6],
                sent[7],
                sent[8],
                sent[9],
            )
            for sent in rows
        ]
        return DBResponse(ok=True, data=Exists(data=sentences))

    def anki_export(self):
        self.db_manager.connect()
        rows = self.dal.get_anki_export()
        sentences = [
            Sentence(
                sent[1],
                sent[2],
                sent[3],
                sent[4],
                sent[5],
                sent[0],
                sent[6],
                sent[7],
                sent[8],
                sent[9],
            )
            for sent in rows
        ]
        return DBResponse(ok=True, data=AnkiExport(data=sentences))

    def paginate(self, page, limit=25):
        table_count = self.dal.count()
        if table_count is None:
            self.logging(
                "Sentences Table has not been created. Cant Get Pagination.", "ERROR"
            )
            self.db_manager.disconnect()
            return

        total_pages = math.ceil(table_count / limit)
        has_next_page = total_pages > page
        has_prev_page = page > 1
        rows = self.dal.paginate(page, limit)
        sentences = [
            Sentence(
                chinese=sent[1],
                english=sent[2],
                pinyin=sent[3],
                audio=sent[4],
                level=sent[5],
                id=sent[0],
                sent_type=sent[10],
                lesson=sent[11],
            )
            for sent in rows
        ]
        return DBResponse(
            ok=True,
            data=PaginationResponse(
                data=sentences,
                table_count=table_count,
                total_pages=total_pages,
                page=page,
                has_prev_page=has_prev_page,
                has_next_page=has_next_page,
            ),
        )
