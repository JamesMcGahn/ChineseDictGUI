import sqlite3

from PySide6.QtCore import QThread, Signal
from wordsDAL import WordsDAL


class DatabaseQueryThread(QThread):
    result_ready = Signal(object)
    error_occurred = Signal(str)

    def __init__(self, db_manager, operation, params=None, id=None):
        super().__init__()
        self.db_manager = db_manager
        self.operation = operation
        self.params = params
        self.id = id

    def run(self):
        self.db_manager.connect()
        self.dal = WordsDAL(self.db_manager)
        try:
            self.db_manager.begin_transaction()
            match (self.operation):
                case "insert_word":
                    self.dal.insert_word(self.params)
                    self.db_manager.commit_transaction()

                case "insert_words":
                    for x in self.params:
                        self.dal.insert_word(x)
                    self.db_manager.commit_transaction()

                case "update_word":
                    self.dal.update_word(self.id, self.params)

                case "delete_word":
                    self.dal.delete_word(self.id)

            self.result_ready.emit(True)
        except sqlite3.Error as e:
            self.db_manager.rollback_transaction()
            self.error_occurred.emit(f"An error occurred: {e}")
        finally:
            self.db_manager.disconnect()
