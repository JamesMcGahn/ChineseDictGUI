import math

from models.dictionary import Word
from models.services.database import DBResponse
from models.services.database.read import AnkiExport, Exists, PaginationResponse

from ..dals import WordsDAL
from .base_read_service import BaseReadService


class WordsReadService(BaseReadService[Word]):
    def __init__(self, db_manager):
        super().__init__(db_manager=db_manager)
        self.dal = WordsDAL(self.db_manager)

    @BaseReadService.catch_sql_error
    def exists(self, items):
        word_strings = [word.chinese for word in items]
        rows = self.dal.exists(word_strings)
        words = [
            Word(
                word[1],
                word[3],
                word[2],
                word[4],
                word[5],
                word[0],
                word[6],
                word[7],
                word[8],
                word[9],
            )
            for word in rows
        ]
        return DBResponse(ok=True, data=Exists(data=words))

    @BaseReadService.catch_sql_error
    def anki_export(self):
        rows = self.dal.get_anki_export()
        words = [
            Word(
                word[1],
                word[3],
                word[2],
                word[4],
                word[5],
                word[0],
                word[6],
                word[7],
                word[8],
                word[9],
            )
            for word in rows
        ]
        return DBResponse(ok=True, data=AnkiExport(data=words))

    @BaseReadService.catch_sql_error
    def paginate(self, page, limit=25):
        table_count = self.dal.count()
        if table_count is None:
            self.logging(
                "Words Table has not been created. Cant Get Pagination.", "ERROR"
            )
            return DBResponse(
                ok=False,
                data=None,
                error="Words Table has not been created. Cant Get Pagination.",
            )
        total_pages = math.ceil(table_count / limit)
        has_next_page = total_pages > page
        has_prev_page = page > 1
        rows = self.dal.paginate(page, limit)

        words = [
            Word(word[1], word[3], word[2], word[4], word[5], word[0]) for word in rows
        ]

        return DBResponse(
            ok=True,
            data=PaginationResponse(
                data=words,
                table_count=table_count,
                total_pages=total_pages,
                page=page,
                has_prev_page=has_prev_page,
                has_next_page=has_next_page,
            ),
        )
