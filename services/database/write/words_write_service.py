from dataclasses import replace
from typing import Any

from models.dictionary import Word
from models.services import JobRequest
from models.services.database import DBJobPayload

from ..dals import WordsDAL
from .base_write_service import BaseWriteService


class WordsWriteService(BaseWriteService[Word]):

    def __init__(self, job: JobRequest[DBJobPayload[Any]]):
        super().__init__(job, dal=WordsDAL)

    @BaseWriteService.emit_db_response
    def insert_one(self, payload):
        word = payload.data.data
        id = self.dal.insert_one(word)
        word = replace(word, id=id)
        return word

    @BaseWriteService.emit_db_response
    def insert_many(self, payload):
        words = payload.data.data

        id_words: list[Word] = []
        for word in words:
            id = self.dal.insert_one(word)
            word_with_id = replace(word, id=id)
            id_words.append(word_with_id)

        return id_words

    @BaseWriteService.emit_db_response
    def update_one(self, payload):
        update = payload.data.data
        id = payload.data.id
        count, word = self.dal.update_one(id, update)
        updated_word = None

        if word:
            updated_word = Word(
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
        return updated_word

    @BaseWriteService.emit_db_response
    def update_many(self, payload):
        updates = payload.data.data
        total_count = 0
        words: list[Word] = []

        for i, item in enumerate(updates):
            commit = True if i == len(updates) - 1 else False
            count, word = self.dal.update_one(item.id, item.data, commit=commit)
            total_count += count
            if word:
                words.append(
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
                )

        return words

    @BaseWriteService.emit_db_response
    def delete_one(self, payload):
        id = payload.data.id
        count, word = self.dal.delete_one_by_id(id)
        if word:
            word = (
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
                ),
            )

        return word

    @BaseWriteService.emit_db_response
    def delete_many(self, payload):
        ids = [item.id for item in payload.data.data]
        count, rows = self.dal.delete_many_by_id(ids)
        deleted_ids: list[int] = []
        deleted_words: list[Word] = []
        for word in rows:
            del_word = Word(
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
            deleted_ids.append(word[0])
            deleted_words.append(del_word)

        return deleted_words
