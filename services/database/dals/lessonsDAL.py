from models.dictionary import Lesson

from .base_DAL import BaseDAL


class LessonsDAL(BaseDAL[Lesson]):

    def __init__(self, db_manager):
        super().__init__(db_manager=db_manager)

    def count(self) -> int | None:
        query = "SELECT COUNT(*) FROM lessons;"
        count = self.db_manager.fetch_one(query)
        return count[0] if count else None

    def exists(self, items):
        placeholders = ",".join(["?"] * len(items))
        # print(placeholders, placeholders)
        # trunk-ignore(bandit/B608)
        query = f"SELECT * FROM lessons WHERE lesson_id IN ({placeholders})"
        rows = self.db_manager.fetch_all(query, tuple(items))
        return rows

    def insert_one(self, item) -> int:
        query = "INSERT INTO lessons (provider,url,slug,status,task,lesson_id, title,level,hash_code, storage_path, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)"
        cursor = self.db_manager.execute_write_query(
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
        row_id = cursor.lastrowid
        self.db_manager.commit_transaction()
        cursor.close()
        return row_id

    def update_one(self, id, updates, commit=True) -> tuple[
        int,
        tuple[int, str, str, str, str, str, str, str, str, str, str, int, int] | None,
    ]:
        """
        Dynamically update fields in the 'lessons' table.

        :param id: ID of the sentence to update.
        :param updates: Dictionary of column names and their new values.
        """
        set_clause = ", ".join([f"{column} = ?" for column in updates.keys()])
        parameters = list(updates.values()) + [id]

        # trunk-ignore(bandit/B608)
        query = f"UPDATE lessons SET {set_clause} WHERE id = ? RETURNING *"
        print(query, parameters)
        cursor = self.db_manager.execute_write_query(query, parameters)
        row = cursor.fetchone()
        if commit:
            self.db_manager.commit_transaction()
        cursor.close()
        count = 1 if row is not None else 0
        return (count, row)

    def delete_one_by_id(self, id) -> tuple[
        int,
        tuple[int, str, str, str, str, str, str, str, str, str, str, int, int] | None,
    ]:
        query = "DELETE FROM lessons WHERE id = ?"
        cursor = self.db_manager.execute_write_query(query, (id,))
        row = cursor.fetchone()
        self.db_manager.commit_transaction()
        cursor.close()
        count = 1 if row is not None else 0
        return (count, row)

    def delete_many_by_id(
        self, ids
    ) -> tuple[
        int, tuple[int, str, str, str, str, str, str, str, str, str, str, int, int]
    ]:
        placeholders = ",".join(["?"] * len(ids))
        # trunk-ignore(bandit/B608)
        query = f"DELETE FROM lessons WHERE id IN ({placeholders})"
        cursor = self.db_manager.execute_write_query(query, tuple(ids))
        rows = cursor.fetchall()
        self.db_manager.commit_transaction()
        cursor.close()
        count = len(rows)
        return (count, rows)

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
