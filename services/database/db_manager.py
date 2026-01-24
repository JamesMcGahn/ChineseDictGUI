import sqlite3

from PySide6.QtCore import QMutexLocker, QObject

from db.db_lock import global_db_mutex


class DatabaseManager(QObject):
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None
        self.mutex = global_db_mutex

    def connect(self):
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_name, timeout=15)

    def disconnect(self):
        """
        Close the connection to the SQLite database.
        """
        if self.connection is not None:
            self.connection.close()

    def execute_query(self, query, params=None):
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            return cursor
        except sqlite3.Error as e:
            print("SQL error ", e)
            raise

    def execute_write_query(self, query, params=None):
        with QMutexLocker(self.mutex):
            try:
                cursor = self.connection.cursor()
                # self.begin_transaction()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                # self.commit_transaction()
                return cursor
            except (
                sqlite3.Error,
                sqlite3.IntegrityError,
                sqlite3.OperationalError,
                sqlite3.DatabaseError,
            ) as _:
                if self.connection.in_transaction:
                    self.rollback_transaction()
                raise

    def begin_transaction(self):
        """Begin a database transaction."""
        self.connection.execute("BEGIN")

    def commit_transaction(self):
        """Commit the current transaction."""
        self.connection.commit()

    def rollback_transaction(self):
        """Rollback the current transaction."""
        self.connection.rollback()

    def fetch_all(self, query, params=None):
        """
        Execute a query and return all results.

        :param query: The SQL query to execute.
        :param params: Optional tuple of parameters to use in the query.
        :return: A list of rows from the result set.
        """
        # print("fetch_all", query, params)
        with sqlite3.connect(self.db_name) as conn:
            return conn.execute(query, params).fetchall()

    def fetch_one(self, query, params=None):
        """
        Execute a query and return a single result.

        :param query: The SQL query to execute.
        :param params: Optional tuple of parameters to use in the query.
        :return: A single row from the result set.
        """
        with sqlite3.connect(self.db_name) as conn:
            return conn.execute(query, params).fetchone()

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
        CREATE TABLE IF NOT EXISTS lessons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        provider TEXT NOT NULL,
        lesson_id TEXT,
        title TEXT,
        level TEXT,
        url TEXT NOT NULL,
        slug TEXT,
        status TEXT,
        task TEXT,
        hash_code TEXT,
        storage_path TEXT,
        created_at INTEGER,
        updated_at INTEGER
        )
        """
        )

        self.execute_query(
            """
            CREATE UNIQUE INDEX idx_lessons_provider_url
            ON lessons(provider, url)
            """
        )
        self.execute_query(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_lessons_provider_lesson_id
            ON lessons(provider, lesson_id)
            WHERE lesson_id IS NOT NULL
            """
        )

        self.execute_query(
            """
        CREATE TABLE IF NOT EXISTS lesson_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lesson_id INTEGER NOT NULL,
            status TEXT NOT NULL CHECK (
                status IN ('pending', 'processing', 'done', 'error')
            ),
            priority INTEGER DEFAULT 0,
            retries INTEGER DEFAULT 0,
            last_error TEXT,

            created_at INTEGER,
            updated_at INTEGER,

            UNIQUE(lesson_id),
            FOREIGN KEY (lesson_id) REFERENCES lessons(id)
        );
        """
        )

        self.execute_query(
            """
            CREATE TABLE IF NOT EXISTS anki_integration (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            anki_update INTEGER,
            local_update INTEGER,
            initial_import_done INTEGER DEFAULT 0
            )
            """
        )
        self.execute_query("COMMIT;")

    def create_anki_integration_record(self):
        result = self.execute_query("SELECT * FROM anki_integration WHERE id = 1")
        result = result.fetchone()

        if result is None:
            self.execute_query("BEGIN;")
            self.execute_query(
                "INSERT INTO anki_integration (anki_update, local_update, initial_import_done) VALUES (?,?,?)",
                (0, 0, 0),
            )
            self.execute_query("COMMIT;")
