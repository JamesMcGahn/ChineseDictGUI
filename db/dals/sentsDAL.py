class SentsDAL:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def insert_sentence(self, sentence):
        query = "INSERT INTO sentences (chinese, english, pinyin, audio, level,anki_audio, anki_id, anki_update,local_update) VALUES (?,?,?,?,?,?,?,?,?)"
        return self.db_manager.execute_write_query(
            query,
            (
                sentence.chinese,
                sentence.english,
                sentence.pinyin,
                sentence.audio,
                sentence.level,
                sentence.anki_audio,
                sentence.anki_id,
                sentence.anki_update,
                sentence.local_update,
            ),
        )

    def delete_sentence(self, id):
        query = "DELETE FROM sentences WHERE id = ?"
        return self.db_manager.execute_write_query(query, (id,))

    def update_sentence(self, id: int, updates: dict):
        """
        Dynamically update fields in the 'sentences' table.

        :param id: ID of the sentence to update.
        :param updates: Dictionary of column names and their new values.
        """
        set_clause = ", ".join([f"{column} = ?" for column in updates.keys()])
        parameters = list(updates.values()) + [id]

        # trunk-ignore(bandit/B608)
        query = f"UPDATE sentences SET {set_clause} WHERE id = ?"
        return self.db_manager.execute_write_query(query, parameters)

    def get_sentences_paginate(self, page, limit=25):
        offset = (page - 1) * limit
        query = "SELECT * FROM sentences LIMIT ? OFFSET ?"
        return self.db_manager.execute_query(
            query,
            (
                limit,
                offset,
            ),
        )

    def get_sentences_table_count(self):
        query = "SELECT COUNT(*) FROM sentences;"
        return self.db_manager.execute_query(query)

    def get_sentence_by_ankiid(self, anki_id):
        query = "SELECT * FROM sentences WHERE anki_id = ?"
        return self.db_manager.execute_query(query, (anki_id,))

    def get_sentence_all_anki_ids(self):
        query = "SELECT anki_id FROM sentences where anki_id not null"
        return self.db_manager.execute_query(query)

    def delete_sentences(self, ids):
        if not ids:
            return
        placeholders = ",".join(["?"] * len(ids))
        # trunk-ignore(bandit/B608)
        query = f"DELETE FROM sentences WHERE anki_id IN ({placeholders})"
        return self.db_manager.execute_write_query(query, tuple(ids))
