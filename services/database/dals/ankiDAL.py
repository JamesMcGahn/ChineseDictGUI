from models.dictionary import AnkiIntegration

from .base_DAL import BaseDAL


class AnkiIntegrationDAL(BaseDAL[AnkiIntegration]):

    def __init__(self, db_manager):
        super().__init__(db_manager=db_manager)

    def get_by_id(self, id):
        id = int(id)
        query = "SELECT * FROM anki_integration WHERE id = ?"
        return self.db_manager.fetch_one(query, (id,))

    def update_one(self, id, updates):
        """
        Dynamically update fields in the 'anki_integration' table.


        :param updates: Anki Integration of column names and their new values.
        """
        set_clause = ", ".join([f"{column} = ?" for column in updates.keys()])
        parameters = list(updates.values()) + [id]

        # trunk-ignore(bandit/B608)
        query = f"UPDATE anki_integration SET {set_clause} WHERE id = ?"
        return self.db_manager.execute_write_query(query, parameters)
