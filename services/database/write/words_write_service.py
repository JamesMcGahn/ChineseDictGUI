from dataclasses import replace

from models.dictionary import Word
from models.services.database import DBResponse
from models.services.database.write import (
    DeleteManyResponse,
    DeleteOneResponse,
    InsertManyResponse,
    InsertOneResponse,
    UpdateManyResponse,
    UpdateOneResponse,
)

from ..dals import WordsDAL
from .base_write_service import BaseWriteService


class WordsWriteService(BaseWriteService[Word]):

    def __init__(self):
        super().__init__()
        self.dal = WordsDAL()

    @BaseWriteService.emit_db_response
    def insert_one(self, payload):
        word = payload.data.data
        id = self.dal.insert_one(word)
        word = replace(word, id=id)
        return DBResponse(ok=True, data=InsertOneResponse(data=word))

    @BaseWriteService.emit_db_response
    def insert_many(self, payload):
        words = payload.data.data

        id_words = []
        for word in words:
            id = self.dal.insert_one(word)
            word_with_id = replace(word, id=id)
            id_words.append(word_with_id)

        return DBResponse(ok=True, data=InsertManyResponse(data=id_words))

    @BaseWriteService.emit_db_response
    def update_one(self, payload):
        update = payload.data.data
        id = payload.data.id
        count, word = self.dal.update_one(id, update)
        success = count > 0
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
        return DBResponse(
            ok=success, data=UpdateOneResponse(data=updated_word, count=count)
        )

    @BaseWriteService.emit_db_response
    def update_many(self, payload):
        updates = payload.data.data
        total_count = 0
        words = []
        self.db_manager.begin_transaction()
        for item in updates:
            count, word = self.dal.update_one(item.id, item.data)
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
        self.db_manager.commit_transaction()
        return DBResponse(
            ok=True, data=UpdateManyResponse(data=words, count=total_count)
        )

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

        return DBResponse(
            ok=True,
            data=DeleteOneResponse(id=id, count=count, data=word),
        )

    @BaseWriteService.emit_db_response
    def delete_many(self, payload):
        ids = [item.id for item in payload.data.data]
        count, rows = self.dal.delete_many_by_id(ids)
        deleted_ids: list[int] = []
        deleted_words: list[DeleteOneResponse[Word]] = []
        for word in rows:
            del_word = DeleteOneResponse(
                id=word[0],
                count=1,
                data=Word(
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
            deleted_ids.append(word[0])
            deleted_words.append(del_word)

        return DBResponse(
            ok=True,
            data=DeleteManyResponse(ids=deleted_ids, count=count, data=deleted_words),
        )
