from models.dictionary import Sentence

from .base_DAL import BaseDAL


class SentsDAL(BaseDAL[Sentence]):

    def __init__(self, db_manager):
        super().__init__(db_manager=db_manager)

    def count(self) -> int | None:
        query = "SELECT COUNT(*) FROM sentences;"
        count = self.db_manager.fetch_one(query)
        return count[0] if count else None

    def exists(
        self, items
    ) -> list[tuple[int, str, str, str, str, str, str, int, int, int]]:
        placeholders = ",".join(["?"] * len(items))
        # print(placeholders, placeholders)
        # trunk-ignore(bandit/B608)
        query = f"SELECT * FROM sentences WHERE chinese IN ({placeholders})"
        rows = self.db_manager.fetch_all(query, tuple(items))
        return rows

    def insert_one(self, item) -> int:
        query = "INSERT INTO sentences (chinese, english, pinyin, audio, level,anki_audio, anki_id, anki_update,local_update,sent_type, lesson) VALUES (?,?,?,?,?,?,?,?,?,?,?)"
        result = self.db_manager.execute_write_query(
            query,
            (
                item.chinese,
                item.english,
                item.pinyin,
                item.audio,
                item.level,
                item.anki_audio,
                item.anki_id,
                item.anki_update,
                item.local_update,
                item.sent_type,
                item.lesson,
            ),
        )
        return result.lastrowid

    def update_one(
        self, id, updates
    ) -> tuple[int, tuple[int, str, str, str, str, str, str, int, int, int] | None]:
        """
        Dynamically update fields in the 'sentences' table.

        :param id: ID of the sentence to update.
        :param updates: Dictionary of column names and their new values.
        """
        set_clause = ", ".join([f"{column} = ?" for column in updates.keys()])
        parameters = list(updates.values()) + [id]

        # trunk-ignore(bandit/B608)
        query = f"UPDATE sentences SET {set_clause} WHERE id = ? RETURNING *"
        cursor = self.db_manager.execute_write_query(query, parameters)
        row = cursor.fetchone()
        count = 1 if row is not None else 0
        return (count, row)

    def delete_one_by_id(
        self, id
    ) -> tuple[int, tuple[int, str, str, str, str, str, str, int, int, int] | None]:
        query = "DELETE FROM sentences WHERE id = ?"
        cursor = self.db_manager.execute_write_query(query, (id,))
        row = cursor.fetchone()
        count = 1 if row is not None else 0
        return (count, row)

    def delete_many_by_id(
        self, ids
    ) -> tuple[int, tuple[int, str, str, str, str, str, str, int, int, int]]:
        placeholders = ",".join(["?"] * len(ids))
        # trunk-ignore(bandit/B608)
        query = f"DELETE FROM sentences WHERE anki_id IN ({placeholders})"
        cursor = self.db_manager.execute_write_query(query, tuple(ids))
        rows = cursor.fetchall()
        count = len(rows)
        return (count, rows)

    def paginate(self, page, limit=25):
        offset = (page - 1) * limit
        query = "SELECT * FROM sentences LIMIT ? OFFSET ?"
        return self.db_manager.fetch_all(
            query,
            (
                limit,
                offset,
            ),
        )

    def get_anki_export(
        self,
    ) -> tuple[int, str, str, str, str, str, str, int, int, int]:
        query = "SELECT * FROM sentences WHERE anki_id IS NULL OR local_update > anki_update"
        return self.db_manager.fetch_all(query)

    def get_by_anki_id(
        self, anki_id
    ) -> tuple[int, str, str, str, str, str, str, int, int, int] | None:
        query = "SELECT * FROM sentences WHERE anki_id = ?"
        return self.db_manager.fetch_one(query, (anki_id,))

    def get_anki_ids(self) -> tuple[int, str, str, str, str, str, str, int, int, int]:
        query = "SELECT anki_id FROM sentences where anki_id not null"
        return self.db_manager.fetch_all(query)
