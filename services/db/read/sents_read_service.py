import math

from dals import SentsDAL
from PySide6.QtCore import Signal

from base import QObjectBase
from models.dictionary import Sentence


class SentsReadService(QObjectBase):
    pagination = Signal(object, int, int, int, bool, bool)
    result = Signal(list)

    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.dals = SentsDAL(self.db_manager)

    def check_for_duplicates(self, sentences: list[Sentence]):
        self.db_manager.connect()
        sentences_strings = [sentence.chinese for sentence in sentences]
        rows = self.dals.check_for_duplicate(sentences_strings)
        existing_sentences = [row[0] for row in rows] if rows else []
        self.result.emit(existing_sentences)
        self.db_manager.disconnect()
        return existing_sentences

    def anki_for_export(self):
        self.db_manager.connect()
        result = self.dals.get_anki_export_sentences()
        sentences = []
        if result is not None:
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
                for sent in result.fetchall()
            ]

        self.result.emit(sentences)
        self.db_manager.disconnect()
        return sentences

    def handle_pagination(self, page, limit):
        self.db_manager.connect()
        table_count_result = self.dals.get_sentences_table_count()
        if table_count_result is None:
            self.logging(
                "Sentences Table has not been created. Cant Get Pagination.", "ERROR"
            )
            self.db_manager.disconnect()
            return

        table_count_result = table_count_result.fetchone()[0]
        total_pages = math.ceil(table_count_result / limit)
        hasNextPage = total_pages > page
        hasPrevPage = page > 1
        result = self.dals.get_sentences_paginate(page, limit)
        if result is not None:
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
                for sent in result.fetchall()
            ]
            self.pagination.emit(
                sentences,
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
