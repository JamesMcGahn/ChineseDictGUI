from dataclasses import replace
from typing import Any

from models.services import JobRequest
from services.sentences.models import Sentence

from ..dals import SentsDAL
from ..models import DBJobPayload
from .base_write_service import BaseWriteService


class SentsWriteService(BaseWriteService[Sentence]):

    def __init__(self, job: JobRequest[DBJobPayload[Any]]):
        super().__init__(job=job, dal=SentsDAL)

    @BaseWriteService.emit_db_response
    def insert_one(self, payload):
        sentence = payload.data.data
        id = self.dal.insert_one(sentence)
        sentence = replace(sentence, id=id)
        return sentence

    @BaseWriteService.emit_db_response
    def insert_many(self, payload):
        sentences = payload.data.data

        id_sentences: list[Sentence] = []
        for sentence in sentences:
            id = self.dal.insert_one(sentence)
            sents_with_id = replace(sentence, id=id)
            id_sentences.append(sents_with_id)

        return id_sentences

    @BaseWriteService.emit_db_response
    def update_one(self, payload):
        update = payload.data.data
        id = payload.data.id
        count, sent = self.dal.update_one(id, update)
        updated_sent = None

        if sent:
            updated_sent = Sentence(
                chinese=sent[1],
                english=sent[2],
                pinyin=sent[3],
                audio_link=sent[4],
                level=sent[5],
                id=sent[0],
                anki_audio=sent[6],
                anki_id=sent[7],
                anki_update=sent[8],
                local_update=sent[9],
                sent_type=sent[10],
                lesson=sent[11],
                runtime_id=sent[12],
                staging_path=sent[13],
                storage_path=sent[14],
            )
        return updated_sent

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
                        chinese=sent[1],
                        english=sent[2],
                        pinyin=sent[3],
                        audio_link=sent[4],
                        level=sent[5],
                        id=sent[0],
                        anki_audio=sent[6],
                        anki_id=sent[7],
                        anki_update=sent[8],
                        local_update=sent[9],
                        sent_type=sent[10],
                        lesson=sent[11],
                        runtime_id=sent[12],
                        staging_path=sent[13],
                        storage_path=sent[14],
                    )
                )

        return sentences

    @BaseWriteService.emit_db_response
    def delete_one(self, payload):
        id = payload.data.id
        count, sent = self.dal.delete_one_by_id(id)
        if sent:
            sent = Sentence(
                chinese=sent[1],
                english=sent[2],
                pinyin=sent[3],
                audio_link=sent[4],
                level=sent[5],
                id=sent[0],
                anki_audio=sent[6],
                anki_id=sent[7],
                anki_update=sent[8],
                local_update=sent[9],
                sent_type=sent[10],
                lesson=sent[11],
                runtime_id=sent[12],
                staging_path=sent[13],
                storage_path=sent[14],
            )

        return sent

    @BaseWriteService.emit_db_response
    def delete_many(self, payload):
        ids = [item.id for item in payload.data.data]
        count, rows = self.dal.delete_many_by_id(ids)
        deleted_ids: list[int] = []
        deleted_sents: list[Sentence] = []
        for sent in rows:
            del_word = Sentence(
                chinese=sent[1],
                english=sent[2],
                pinyin=sent[3],
                audio_link=sent[4],
                level=sent[5],
                id=sent[0],
                anki_audio=sent[6],
                anki_id=sent[7],
                anki_update=sent[8],
                local_update=sent[9],
                sent_type=sent[10],
                lesson=sent[11],
                runtime_id=sent[12],
                staging_path=sent[13],
                storage_path=sent[14],
            )

            deleted_ids.append(sent[0])
            deleted_sents.append(del_word)

        return deleted_sents
