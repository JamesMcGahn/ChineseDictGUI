import math

from PySide6.QtCore import Signal

from base import QObjectBase
from models.dictionary import Word

from ..dals import WordsDAL


class WordsReadService(QObjectBase):
    pagination = Signal(object, int, int, int, bool, bool)
    result = Signal(list)

    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.dalw = WordsDAL(self.db_manager)

    def check_for_duplicates(self, words: list[Word]):
        self.db_manager.connect()
        word_strings = [word.chinese for word in words]
        rows = self.dalw.check_for_duplicate(word_strings)
        existing_words = [row[0] for row in rows] if rows else []
        self.result.emit(existing_words)
        self.db_manager.disconnect()
        return existing_words

    def anki_for_export(self):
        self.db_manager.connect()
        result = self.dalw.get_anki_export_words()
        words = []
        if result is not None:
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
                for word in result.fetchall()
            ]

        self.result.emit(words)
        self.db_manager.disconnect()
        return words

    def handle_pagination(self, page, limit):
        self.db_manager.connect()
        table_count_result = self.dalw.get_words_table_count()
        if table_count_result is None:
            self.logging(
                "Words Table has not been created. Cant Get Pagination.", "ERROR"
            )
            self.db_manager.disconnect()
            return

        table_count_result = table_count_result.fetchone()[0]
        total_pages = math.ceil(table_count_result / limit)
        hasNextPage = total_pages > page
        hasPrevPage = page > 1
        result = self.dalw.get_words_paginate(page, limit)
        if result is not None:
            words = [
                Word(word[1], word[3], word[2], word[4], word[5], word[0])
                for word in result.fetchall()
            ]
            self.pagination.emit(
                words,
                table_count_result,
                total_pages,
                page,
                hasPrevPage,
                hasNextPage,
            )
        else:
            self.pagination.emit(
                None,
                table_count_result,
                total_pages,
                page,
                hasPrevPage,
                hasNextPage,
            )
        self.db_manager.disconnect()
