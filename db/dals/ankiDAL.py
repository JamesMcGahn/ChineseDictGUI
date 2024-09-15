class AnkiIntegrationDAL:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_anki_integration(self):
        query = "SELECT * FROM anki_integration WHERE id = 1"
        return self.db_manager.execute_query(query)

    def update_anki_integration(self, updates):
        """
        Dynamically update fields in the 'anki_integration' table.


        :param updates: Anki Integration of column names and their new values.
        """
        set_clause = ", ".join([f"{column} = ?" for column in updates.keys()])
        parameters = list(updates.values())

        # trunk-ignore(bandit/B608)
        query = f"UPDATE anki_integration SET {set_clause} WHERE id = 1"
        return self.db_manager.execute_query(query, parameters)
