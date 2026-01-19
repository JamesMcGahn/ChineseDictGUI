from models.dictionary import Word

from .base_DAL import BaseDAL


class WordsDAL(BaseDAL[Word]):
    def __init__(self, db_manager):
        super().__init__(db_manager=db_manager)

    def count(self):
        query = "SELECT COUNT(*) FROM words;"
        return self.db_manager.fetch_one(query)

    def exists(self, items):
        placeholders = ",".join(["?"] * len(items))
        # print(placeholders, placeholders)
        # trunk-ignore(bandit/B608)
        query = f"SELECT * FROM words WHERE chinese IN ({placeholders})"
        rows = self.db_manager.fetch_all(query, tuple(items))
        return rows

    def insert_one(self, item):
        query = "INSERT INTO words (chinese, pinyin, definition, audio, level, anki_audio, anki_id, anki_update,local_update) VALUES (?,?,?,?,?,?,?,?,?)"
        return self.db_manager.execute_write_query(
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

    def update_one(self, id, updates):
        """
        Dynamically update fields in the 'words' table.

        :param id: ID of the word to update.
        :param updates: Dictionary of column names and their new values.
        """
        set_clause = ", ".join([f"{column} = ?" for column in updates.keys()])
        parameters = list(updates.values()) + [id]

        # trunk-ignore(bandit/B608)
        query = f"UPDATE words SET {set_clause} WHERE id = ?"
        return self.db_manager.execute_write_query(query, parameters)

    def delete_one_by_id(self, id):
        query = "DELETE FROM words WHERE id = ?"
        return self.db_manager.execute_write_query(query, (id,))

    def delete_many_by_id(self, ids):
        placeholders = ",".join(["?"] * len(ids))
        # trunk-ignore(bandit/B608)
        query = f"DELETE FROM words WHERE anki_id IN ({placeholders})"
        return self.db_manager.execute_write_query(query, tuple(ids))

    def paginate(self, page, limit=25):
        offset = (page - 1) * limit
        query = "SELECT * FROM words LIMIT ? OFFSET ?"
        return self.db_manager.fetch_all(
            query,
            (
                limit,
                offset,
            ),
        )

    def get_anki_export(self):
        query = (
            "SELECT * FROM words WHERE anki_id IS NULL OR local_update > anki_update"
        )
        return self.db_manager.fetch_all(query)

    def get_by_anki_id(self, anki_id):
        query = "SELECT * FROM words WHERE anki_id = ?"
        return self.db_manager.fetch_one(query, (anki_id,))

    def get_anki_ids(self):
        query = "SELECT anki_id FROM words where anki_id not null"
        return self.db_manager.fetch_all(query)
