from dataclasses import replace

from models.dictionary import Lesson
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

from ..dals import LessonsDAL
from .base_write_service import BaseWriteService


class LessonWriteService(BaseWriteService[Lesson]):

    def __init__(self, job_ref: JobRef, payload: DBJobPayload):
        super().__init__(job_ref, payload, dal=LessonsDAL)

    @BaseWriteService.emit_db_response
    def insert_one(self, payload):
        lesson = payload.data.data
        id = self.dal.insert_one(lesson)
        lesson = replace(lesson, id=id)
        return DBResponse(ok=True, data=InsertOneResponse(data=lesson))

    @BaseWriteService.emit_db_response
    def insert_many(self, payload):
        lessons = payload.data.data

        id_lessons: list[Lesson] = []
        for lesson in lessons:
            id = self.dal.insert_one(lesson)
            lesson_with_id = replace(lesson, id=id)
            id_lessons.append(lesson_with_id)

        return DBResponse(ok=True, data=InsertManyResponse(data=id_lessons))

    @BaseWriteService.emit_db_response
    def update_one(self, payload):
        update = payload.data.data
        id = payload.data.id
        count, lesson = self.dal.update_one(id, update)
        success = count > 0
        updated_lesson = None

        if lesson:
            updated_lesson = Lesson(
                id=lesson[0],
                provider=lesson[1],
                lesson_id=lesson[2],
                title=lesson[3],
                level=lesson[4],
                url=lesson[5],
                slug=lesson[6],
                status=lesson[7],
                task=lesson[8],
                hash_code=lesson[9],
                storage_path=lesson[10],
                created_at=lesson[11],
                updated_at=lesson[12],
            )
        return DBResponse(
            ok=success, data=UpdateOneResponse(data=updated_lesson, count=count)
        )

    @BaseWriteService.emit_db_response
    def update_many(self, payload):
        updates = payload.data.data
        total_count = 0
        lessons: list[Lesson] = []
        for i, item in enumerate(updates):
            commit = True if i == len(updates) - 1 else False
            count, lesson = self.dal.update_one(item.id, item.data, commit=commit)
            total_count += count
            if lesson:
                lessons.append(
                    Lesson(
                        id=lesson[0],
                        provider=lesson[1],
                        lesson_id=lesson[2],
                        title=lesson[3],
                        level=lesson[4],
                        url=lesson[5],
                        slug=lesson[6],
                        status=lesson[7],
                        task=lesson[8],
                        hash_code=lesson[9],
                        storage_path=lesson[10],
                        created_at=lesson[11],
                        updated_at=lesson[12],
                    )
                )

        return DBResponse(
            ok=True, data=UpdateManyResponse(data=lessons, count=total_count)
        )

    @BaseWriteService.emit_db_response
    def delete_one(self, payload):
        id = payload.data.id
        count, lesson = self.dal.delete_one_by_id(id)
        if lesson:
            lesson = Lesson(
                id=lesson[0],
                provider=lesson[1],
                lesson_id=lesson[2],
                title=lesson[3],
                level=lesson[4],
                url=lesson[5],
                slug=lesson[6],
                status=lesson[7],
                task=lesson[8],
                hash_code=lesson[9],
                storage_path=lesson[10],
                created_at=lesson[11],
                updated_at=lesson[12],
            )

        return DBResponse(
            ok=True,
            data=DeleteOneResponse(id=id, count=count, data=lesson),
        )

    @BaseWriteService.emit_db_response
    def delete_many(self, payload):
        ids = [item.id for item in payload.data.data]
        count, rows = self.dal.delete_many_by_id(ids)
        deleted_ids: list[int] = []
        deleted_lessons: list[DeleteOneResponse[Lesson]] = []
        for lesson in rows:
            del_word = DeleteOneResponse(
                id=lesson[0],
                count=1,
                data=Lesson(
                    id=lesson[0],
                    provider=lesson[1],
                    lesson_id=lesson[2],
                    title=lesson[3],
                    level=lesson[4],
                    url=lesson[5],
                    slug=lesson[6],
                    status=lesson[7],
                    task=lesson[8],
                    hash_code=lesson[9],
                    storage_path=lesson[10],
                    created_at=lesson[11],
                    updated_at=lesson[12],
                ),
            )
            deleted_ids.append(lesson[0])
            deleted_lessons.append(del_word)

        return DBResponse(
            ok=True,
            data=DeleteManyResponse(ids=deleted_ids, count=count, data=deleted_lessons),
        )
