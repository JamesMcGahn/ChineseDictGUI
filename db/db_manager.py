import sqlite3

from PySide6.QtCore import QMutex, QMutexLocker, QObject


class DatabaseManager(QObject):
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None
        self.mutex = QMutex()

    def connect(self):
        self.connection = sqlite3.connect(self.db_name, check_same_thread=False)

    def execute_query(self, query, params=None):
        with QMutexLocker(self.mutex):
            try:
                cursor = self.connection.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                return cursor
            except sqlite3.Error as e:
                # TODO: do something with error
                print(e)
                return None

    def begin_transaction(self):
        """Begin a database transaction."""
        self.execute_query("BEGIN;")

    def commit_transaction(self):
        """Commit the current transaction."""
        self.execute_query("COMMIT;")

    def rollback_transaction(self):
        """Rollback the current transaction."""
        self.execute_query("ROLLBACK;")

    def disconnect(self):
        """
        Close the connection to the SQLite database.
        """
        if self.connection is not None:
            self.connection.close()

    def fetch_all(self, query, params=None):
        """
        Execute a query and return all results.

        :param query: The SQL query to execute.
        :param params: Optional tuple of parameters to use in the query.
        :return: A list of rows from the result set.
        """
        cursor = self.execute_query(query, params)
        return cursor.fetchall() if cursor else []

    def fetch_one(self, query, params=None):
        """
        Execute a query and return a single result.

        :param query: The SQL query to execute.
        :param params: Optional tuple of parameters to use in the query.
        :return: A single row from the result set.
        """
        cursor = self.execute_query(query, params)
        return cursor.fetchone() if cursor else None

    def create_tables_if_not_exist(self):
        self.execute_query("BEGIN;")
        self.execute_query(
            """
            CREATE TABLE IF NOT EXISTS words (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             chinese TEXT NOT NULL,
             pinyin TEXT NOT NULL,
             definition TEXT NOT NULL,
             audio TEXT,
             level TEXT,
             anki_audio TEXT,
             anki_id INTEGER,
             anki_update INTEGER,
             local_update INTEGER)
            """
        )
        self.execute_query(
            """
            CREATE TABLE IF NOT EXISTS sentences (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             chinese TEXT NOT NULL,
             english TEXT NOT NULL,
             pinyin TEXT NOT NULL,
             audio TEXT,
             level TEXT,
             anki_audio TEXT,
             anki_id INTEGER,
             anki_update INTEGER,
             local_update INTEGER
             )
            """
        )

        self.execute_query(
            """
            CREATE TABLE IF NOT EXISTS anki_integration (
            id TEXT PRIMARY KEY,
            anki_update INTEGER,
            local_update INTEGER)
             """
        )
        self.execute_query("COMMIT;")
