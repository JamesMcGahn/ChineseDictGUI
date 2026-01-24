from models.dictionary import Word

from .base_DAL import BaseDAL


class WordsDAL(BaseDAL[Word]):
    def __init__(self, db_manager):
        super().__init__(db_manager=db_manager)

    def count(self) -> int | None:
        query = "SELECT COUNT(*) FROM words;"
        count = self.db_manager.fetch_one(query)
        return count[0] if count else None

    def exists(
        self, items
    ) -> list[tuple[int, str, str, str, str, str, str, int, int, int]]:
        placeholders = ",".join(["?"] * len(items))
        # print(placeholders, placeholders)
        # trunk-ignore(bandit/B608)
        query = f"SELECT * FROM words WHERE chinese IN ({placeholders})"
        rows = self.db_manager.fetch_all(query, tuple(items))
        return rows

    def insert_one(self, item) -> int:
        query = "INSERT INTO words (chinese, pinyin, definition, audio, level, anki_audio, anki_id, anki_update,local_update) VALUES (?,?,?,?,?,?,?,?,?)"

        cursor = self.db_manager.execute_write_query(
            query,
            (
                item.chinese,
                item.pinyin,
                item.definition,
                item.audio,
                item.level,
                item.anki_audio,
                item.anki_id,
                item.anki_update,
                item.local_update,
            ),
        )
        row_id = cursor.lastrowid
        self.db_manager.commit_transaction()
        cursor.close()
        return row_id

    def update_one(
        self, id, updates, commit=True
    ) -> tuple[int, tuple[int, str, str, str, str, str, str, int, int, int] | None]:
        """
        Dynamically update fields in the 'words' table.

        :param id: ID of the word to update.
        :param updates: Dictionary of column names and their new values.
        """
        set_clause = ", ".join([f"{column} = ?" for column in updates.keys()])
        parameters = list(updates.values()) + [id]

        # trunk-ignore(bandit/B608)
        query = f"UPDATE words SET {set_clause} WHERE id = ? RETURNING *;"
        cursor = self.db_manager.execute_write_query(query, parameters)
        row = cursor.fetchone()
        if commit:
            self.db_manager.commit_transaction()
        cursor.close()
        count = 1 if row is not None else 0
        return (count, row)

    def delete_one_by_id(
        self, id
    ) -> tuple[int, tuple[int, str, str, str, str, str, str, int, int, int] | None]:
        query = "DELETE FROM words WHERE id = ? RETURNING *;"
        cursor = self.db_manager.execute_write_query(query, (id,))
        row = cursor.fetchone()
        self.db_manager.commit_transaction()
        cursor.close()
        count = 1 if row is not None else 0
        return (count, row)

    def delete_many_by_id(
        self, ids
    ) -> tuple[int, tuple[int, str, str, str, str, str, str, int, int, int]]:
        placeholders = ",".join(["?"] * len(ids))
        # trunk-ignore(bandit/B608)
        query = f"DELETE FROM words WHERE id IN ({placeholders}) RETURNING *;"
        cursor = self.db_manager.execute_write_query(query, tuple(ids))
        rows = cursor.fetchall()
        self.db_manager.commit_transaction()
        cursor.close()
        count = len(rows)
        return (count, rows)

    def paginate(
        self, page, limit=25
    ) -> tuple[int, str, str, str, str, str, str, int, int, int]:
        offset = (page - 1) * limit
        query = "SELECT * FROM words LIMIT ? OFFSET ?"
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
        query = (
            "SELECT * FROM words WHERE anki_id IS NULL OR local_update > anki_update"
        )
        return self.db_manager.fetch_all(query)

    def get_by_anki_id(
        self, anki_id
    ) -> tuple[int, str, str, str, str, str, str, int, int, int] | None:
        query = "SELECT * FROM words WHERE anki_id = ?"
        return self.db_manager.fetch_one(query, (anki_id,))

    def get_anki_ids(self) -> tuple[int, str, str, str, str, str, str, int, int, int]:
        query = "SELECT anki_id FROM words where anki_id not null"
        return self.db_manager.fetch_all(query)
