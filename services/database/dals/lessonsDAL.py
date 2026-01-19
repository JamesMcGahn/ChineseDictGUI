from models.dictionary import Lesson

from .base_DAL import BaseDAL


class LessonsDAL(BaseDAL[Lesson]):

    def __init__(self, db_manager):
        super().__init__(db_manager=db_manager)

    def exists(self, items):
        placeholders = ",".join(["?"] * len(items))
        # print(placeholders, placeholders)
        # trunk-ignore(bandit/B608)
        query = f"SELECT * FROM lessons WHERE lesson_id IN ({placeholders})"
        rows = self.db_manager.fetch_all(query, tuple(items))
        return rows

    def insert_one(self, item):
        query = "INSERT INTO lessons (provider,url,slug,status,task,lesson_id, title,level,hash_code, storage_path, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)"
        return self.db_manager.execute_write_query(
            query,
            (
                item.provider,
                item.url,
                item.slug,
                item.status,
                item.task,
                item.lesson_id,
                item.title,
                item.level,
                item.hash_code,
                item.storage_path,
                item.created_at,
                item.updated_at,
            ),
        )

    def paginate(self, page, limit=25):
        offset = (page - 1) * limit
        query = "SELECT * FROM lessons LIMIT ? OFFSET ?"
        return self.db_manager.fetch_all(
            query,
            (
                limit,
                offset,
            ),
        )
