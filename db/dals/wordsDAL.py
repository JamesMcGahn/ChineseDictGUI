class WordsDAL:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def insert_word(self, word):
        query = "INSERT INTO words (chinese, pinyin, definition, audio, level, anki_audio, anki_id, anki_update,local_update) VALUES (?,?,?,?,?,?,?,?,?)"
        return self.db_manager.execute_write_query(
            query,
            (
                word.chinese,
                word.pinyin,
                word.definition,
                word.audio,
                word.level,
                word.anki_audio,
                word.anki_id,
                word.anki_update,
                word.local_update,
            ),
        )

    def check_for_duplicate(self, words):
        placeholders = ",".join(["?"] * len(words))
        # print(placeholders, placeholders)
        # trunk-ignore(bandit/B608)
        query = f"SELECT chinese FROM words WHERE chinese IN ({placeholders})"
        rows = self.db_manager.fetch_all(query, tuple(words))
        return rows

    def delete_word(self, id):
        query = "DELETE FROM words WHERE id = ?"
        return self.db_manager.execute_write_query(query, (id,))

    def update_word(self, id: int, updates: dict):
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

    def get_words_paginate(self, page, limit=25):
        offset = (page - 1) * limit
        query = "SELECT * FROM words LIMIT ? OFFSET ?"
        return self.db_manager.execute_query(
            query,
            (
                limit,
                offset,
            ),
        )

    def get_words_table_count(self):
        query = "SELECT COUNT(*) FROM words;"
        return self.db_manager.execute_query(query)

    def get_word_by_ankiid(self, anki_id):
        query = "SELECT * FROM words WHERE anki_id = ?"
        return self.db_manager.execute_query(query, (anki_id,))

    def get_words_all_anki_ids(self):
        query = "SELECT anki_id FROM words where anki_id not null"
        return self.db_manager.execute_query(query)

    def delete_words(self, ids):
        if not ids:
            return
        placeholders = ",".join(["?"] * len(ids))
        # trunk-ignore(bandit/B608)
        query = f"DELETE FROM words WHERE anki_id IN ({placeholders})"
        return self.db_manager.execute_write_query(query, tuple(ids))

    def get_anki_export_words(self):
        query = (
            "SELECT * FROM words WHERE anki_id IS NULL OR local_update > anki_update"
        )
        return self.db_manager.execute_query(query)
