from models.dictionary import AnkiIntegration

from .base_DAL import BaseDAL


class AnkiIntegrationDAL(BaseDAL[AnkiIntegration]):

    def __init__(self, db_manager):
        super().__init__(db_manager=db_manager)

    def get_by_id(self, id) -> tuple[int, int, int, int] | None:
        id = int(id)
        query = "SELECT * FROM anki_integration WHERE id = ?"
        return self.db_manager.fetch_one(query, (id,))

    def update_one(
        self, id, updates, commit=True
    ) -> tuple[int, tuple[int, int, int, int] | None]:
        """
        Dynamically update fields in the 'anki_integration' table.


        :param updates: Anki Integration of column names and their new values.
        """
        set_clause = ", ".join([f"{column} = ?" for column in updates.keys()])
        parameters = list(updates.values()) + [id]

        # trunk-ignore(bandit/B608)
        query = f"UPDATE anki_integration SET {set_clause} WHERE id = ? RETURNING *;"
        cursor = self.db_manager.execute_write_query(query, parameters)
        row = cursor.fetchone()
        if commit:
            self.db_manager.commit_transaction()
        cursor.close()
        count = 1 if row is not None else 0
        return (count, row)
