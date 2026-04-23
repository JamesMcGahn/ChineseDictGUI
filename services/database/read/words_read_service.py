import math

from services.words.models import Word

from ..dals import WordsDAL
from ..models.read import PaginationResponse
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
                chinese=word[1],
                english=word[3],
                pinyin=word[2],
                audio_link=word[4],
                level=word[5],
                id=word[0],
                anki_audio=word[6],
                anki_id=word[7],
                anki_update=word[8],
                local_update=word[9],
                lesson=word[10],
                runtime_id=word[11],
                staging_path=word[12],
                storage_path=word[13],
            )
            for word in rows
        ]
        return words

    @BaseReadService.catch_sql_error
    def anki_export(self):
        rows = self.dal.get_anki_export()
        words = [
            Word(
                chinese=word[1],
                english=word[3],
                pinyin=word[2],
                audio_link=word[4],
                level=word[5],
                id=word[0],
                anki_audio=word[6],
                anki_id=word[7],
                anki_update=word[8],
                local_update=word[9],
                lesson=word[10],
                runtime_id=word[11],
                staging_path=word[12],
                storage_path=word[13],
            )
            for word in rows
        ]
        return words

    @BaseReadService.catch_sql_error
    def paginate(self, page, limit=25):
        table_count = self.dal.count()
        if table_count is None:
            self.logging(
                "Words Table has not been created. Cant Get Pagination.", "ERROR"
            )
            return None
        total_pages = math.ceil(table_count / limit)
        has_next_page = total_pages > page
        has_prev_page = page > 1
        rows = self.dal.paginate(page, limit)

        words = [
            Word(
                chinese=word[1],
                english=word[3],
                pinyin=word[2],
                audio_link=word[4],
                level=word[5],
                id=word[0],
                anki_audio=word[6],
                anki_id=word[7],
                anki_update=word[8],
                local_update=word[9],
                lesson=word[10],
                runtime_id=word[11],
                staging_path=word[12],
                storage_path=word[13],
            )
            for word in rows
        ]

        return PaginationResponse(
            data=words,
            table_count=table_count,
            total_pages=total_pages,
            page=page,
            has_prev_page=has_prev_page,
            has_next_page=has_next_page,
        )
