import math

from PySide6.QtCore import Signal

from models.dictionary import Lesson
from models.services.database import DBResponse
from models.services.database.read import Exists, PaginationResponse

from ..dals import LessonsDAL
from .base_service import BaseService


class LessonReadService(BaseService[Lesson]):
    pagination = Signal(object, int, int, int, bool, bool)
    result = Signal(list)

    def __init__(self, db_manager):
        super().__init__(db_manager=db_manager)
        self.dal = LessonsDAL(self.db_manager)

    def exists(self, items):
        lesson_ids = [lesson.lesson_id for lesson in items]
        rows = self.dal.exists(lesson_ids)
        lessons = [
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
            for lesson in rows
        ]
        return DBResponse(ok=True, data=Exists(data=lessons))

    def paginate(self, page, limit=25):
        table_count_result = self.dal.count()
        if table_count_result is None:
            self.logging(
                "Lesson Table has not been created. Cant Get Pagination.", "ERROR"
            )
            return DBResponse(
                ok=False,
                data=None,
                error="Lesson Table has not been created. Cant Get Pagination.",
            )

        table_count = table_count_result[0]
        total_pages = math.ceil(table_count / limit)
        has_next_page = total_pages > page
        has_prev_page = page > 1
        rows = self.dal.paginate(page, limit)

        lessons = [
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
            for lesson in rows
        ]

        return DBResponse(
            ok=True,
            data=PaginationResponse(
                data=lessons,
                table_count=table_count,
                total_pages=total_pages,
                page=page,
                has_prev_page=has_prev_page,
                has_next_page=has_next_page,
            ),
        )
