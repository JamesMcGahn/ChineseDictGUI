from dataclasses import replace

from models.dictionary import Sentence
from models.services import JobRef
from models.services.database import DBJobPayload, DBResponse
from models.services.database.write import (
    DeleteManyResponse,
    DeleteOneResponse,
    InsertManyResponse,
    InsertOneResponse,
    UpdateManyResponse,
    UpdateOneResponse,
)

from ..dals import SentsDAL
from .base_write_service import BaseWriteService


class SentsWriteService(BaseWriteService[Sentence]):

    def __init__(self, job_ref: JobRef, payload: DBJobPayload):
        super().__init__(job_ref, payload, dal=SentsDAL)

    @BaseWriteService.emit_db_response
    def insert_one(self, payload):
        sentence = payload.data.data
        id = self.dal.insert_one(sentence)
        sentence = replace(sentence, id=id)
        return DBResponse(ok=True, data=InsertOneResponse(data=sentence))

    @BaseWriteService.emit_db_response
    def insert_many(self, payload):
        sentences = payload.data.data

        id_sentences: list[Sentence] = []
        for sentence in sentences:
            id = self.dal.insert_one(sentence)
            sents_with_id = replace(sentence, id=id)
            id_sentences.append(sents_with_id)

        return DBResponse(ok=True, data=InsertManyResponse(data=id_sentences))

    @BaseWriteService.emit_db_response
    def update_one(self, payload):
        update = payload.data.data
        id = payload.data.id
        count, sent = self.dal.update_one(id, update)
        success = count > 0
        updated_sent = None

        if sent:
            updated_sent = Sentence(
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
        return DBResponse(
            ok=success, data=UpdateOneResponse(data=updated_sent, count=count)
        )

    @BaseWriteService.emit_db_response
    def update_many(self, payload):
        updates = payload.data.data
        total_count = 0
        sentences: list[Sentence] = []

        for i, item in enumerate(updates):
            commit = True if i == len(updates) - 1 else False
            count, sent = self.dal.update_one(item.id, item.data, commit=commit)
            total_count += count
            if sent:
                sentences.append(
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
                )

        return DBResponse(
            ok=True, data=UpdateManyResponse(data=sentences, count=total_count)
        )

    @BaseWriteService.emit_db_response
    def delete_one(self, payload):
        id = payload.data.id
        count, sent = self.dal.delete_one_by_id(id)
        if sent:
            sent = Sentence(
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

        return DBResponse(
            ok=True,
            data=DeleteOneResponse(id=id, count=count, data=sent),
        )

    @BaseWriteService.emit_db_response
    def delete_many(self, payload):
        ids = [item.id for item in payload.data.data]
        count, rows = self.dal.delete_many_by_id(ids)
        deleted_ids: list[int] = []
        deleted_sents: list[DeleteOneResponse[Sentence]] = []
        for sent in rows:
            del_word = DeleteOneResponse(
                id=sent[0],
                count=1,
                data=Sentence(
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
                ),
            )
            deleted_ids.append(sent[0])
            deleted_sents.append(del_word)

        return DBResponse(
            ok=True,
            data=DeleteManyResponse(ids=deleted_ids, count=count, data=deleted_sents),
        )
