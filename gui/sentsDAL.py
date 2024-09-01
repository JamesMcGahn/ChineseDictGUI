class SentsDAL:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def insert_sentence(self, sentence):
        query = "INSERT INTO sentences (chinese, english, pinyin, audio, level) VALUES (?,?,?,?,?)"
        return self.db_manager.execute_query(
            query,
            (
                sentence.chinese,
                sentence.english,
                sentence.pinyin,
                sentence.audio,
                sentence.level,
            ),
        )

    def delete_sentence(self, id):
        query = "DELETE FROM sentences WHERE id = ?"
        return self.db_manager.execute_query(query, (id,))

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
        return self.db_manager.execute_query(query, parameters)

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
