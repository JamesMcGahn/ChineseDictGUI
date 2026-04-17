from dataclasses import replace
from typing import Any

from models.dictionary import Lesson
from models.services import JobRequest

from ..dals import LessonsDAL
from ..models import DBJobPayload
from .base_write_service import BaseWriteService


class LessonWriteService(BaseWriteService[Lesson]):

    def __init__(self, job: JobRequest[DBJobPayload[Any]]):
        super().__init__(job=job, dal=LessonsDAL)

    @BaseWriteService.emit_db_response
    def insert_one(self, payload):
        lesson = payload.data.data
        id = self.dal.insert_one(lesson)
        lesson = replace(lesson, id=id)
        return lesson

    @BaseWriteService.emit_db_response
    def upsert_one(self, payload):
        lesson = payload.data.data
        id = self.dal.upsert_one(lesson)
        lesson = replace(lesson, id=id)
        return lesson

    @BaseWriteService.emit_db_response
    def insert_many(self, payload):
        lessons = payload.data.data

        id_lessons: list[Lesson] = []
        for lesson in lessons:
            id = self.dal.insert_one(lesson)
            lesson_with_id = replace(lesson, id=id)
            id_lessons.append(lesson_with_id)

        return id_lessons

    @BaseWriteService.emit_db_response
    def update_one(self, payload):
        update = payload.data.data
        id = payload.data.id
        count, lesson = self.dal.update_one(id, update)
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
        return updated_lesson

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

        return lessons

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

        return lesson

    @BaseWriteService.emit_db_response
    def delete_many(self, payload):
        ids = [item.id for item in payload.data.data]
        count, rows = self.dal.delete_many_by_id(ids)
        deleted_ids: list[int] = []
        deleted_lessons: list[Lesson] = []
        for lesson in rows:
            del_word = Lesson(
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
            deleted_ids.append(lesson[0])
            deleted_lessons.append(del_word)

        return deleted_lessons
