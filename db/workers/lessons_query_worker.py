import math
import sqlite3
import time

from PySide6.QtCore import QObject, Signal, Slot

from models.dictionary import Lesson

from ..dals import LessonsDAL
from ..db_manager import DatabaseManager


class LessonsQueryWorker(QObject):
    finished = Signal()
    pagination = Signal(object, int, int, int, bool, bool)
    error_occurred = Signal(str)
    message = Signal(str)
    result = Signal(list)

    def __init__(self, operation, **kwargs):
        super().__init__()
        self.db_manager = DatabaseManager("chineseDict.db")
        self.operation = operation
        self.kwargs = kwargs
        self.retry_pagination = 0

    @Slot()
    def do_work(self):
        self.db_manager.connect()
        self.dall = LessonsDAL(self.db_manager)
        try:
            match (self.operation):
                case "insert_lesson":
                    self.handle_insert_lesson()

        except sqlite3.OperationalError as e:
            if "no such table" in str(e):
                if (
                    self.operation == "get_pagination_words"
                    and self.retry_pagination < 2
                ):
                    time.sleep(10)
                    self.handle_pagination()
                    self.retry_pagination += 1
                else:
                    self.error_occurred.emit(f"An error occurred: {e}")

        except sqlite3.Error as e:
            self.db_manager.rollback_transaction()
            self.error_occurred.emit(f"An error occurred: {e}")
        except Exception as e:
            self.db_manager.rollback_transaction()
            self.error_occurred.emit(f"An error occurred: {e}")
        finally:
            self.db_manager.disconnect()
            self.finished.emit()

    def handle_insert_lesson(self):
        lesson = self.kwargs.get("lesson", None)
        if lesson is None:
            raise ValueError("word must be specified as kwarg")

        result = self.dall.insert_word(lesson)
        id = result.lastrowid
        lesson.id = id

        self.result.emit([lesson])
