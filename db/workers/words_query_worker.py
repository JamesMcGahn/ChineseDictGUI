import math
import sqlite3
import time

from PySide6.QtCore import QObject, Signal, Slot

from models.dictionary import Word

from ..dals import WordsDAL
from ..db_manager import DatabaseManager


class WordsQueryWorker(QObject):
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
        self.dalw = WordsDAL(self.db_manager)
        try:
            match (self.operation):
                case "check_for_duplicate_words":
                    self.handle_check_for_duplicate()

                case "insert_word":
                    self.handle_insert_word()

                case "insert_words":
                    self.handle_insert_words()

                case "update_word":
                    self.handle_update_word()

                case "update_words":
                    self.handle_update_words()

                case "delete_word":
                    self.handle_delete_word()

                case "delete_words":
                    self.handle_delete_words()

                case "get_pagination_words":
                    self.handle_pagination()

                case "get_anki_export_words":
                    self.handle_anki_export()

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

    def handle_check_for_duplicate(self):
        words = self.kwargs.get("words", None)
        if words is None:
            raise ValueError("words must be specified as kwarg")
        word_strings = [word.chinese for word in words]
        # print("word strings", word_strings)
        rows = self.dalw.check_for_duplicate(word_strings)
        # print("rows", rows)

        existing_words = [row[0] for row in rows] if rows else []
        # print("existing", existing_words)
        self.result.emit(existing_words)

    def handle_insert_word(self):
        word = self.kwargs.get("word", None)
        if word is None:
            raise ValueError("word must be specified as kwarg")

        result = self.dalw.insert_word(word)
        id = result.lastrowid
        word.id = id

        self.result.emit([word])

    def handle_insert_words(self):
        # TODO change to insert many instead of LOOP
        print("here inserting")
        words = self.kwargs.get("words", None)
        if words is None:
            raise ValueError("words must be specified as kwarg")

        id_words = []
        for x in words:
            result = self.dalw.insert_word(x)
            id = result.lastrowid
            x.id = id
            id_words.append(x)
        print(id_words)
        self.result.emit(id_words)

    def handle_update_word(self):
        updates = self.kwargs.get("updates", None)
        id = self.kwargs.get("id", None)
        if updates is None or id is None:
            raise ValueError("word and id must be specified as kwarg")

        suc = self.dalw.update_word(id, updates)
        if suc.rowcount == 1:
            self.message.emit("Update Saved.")

    def handle_update_words(self):
        words = self.kwargs.get("words", None)
        if words is None:
            raise ValueError("words must be specified as kwarg")

        for word in words:
            id = word["id"]
            updates = word["updates"]
            # print(id, updates)
            suc = self.dalw.update_word(id, updates)
            if suc.rowcount == 1:
                self.message.emit(f"Update Saved for ID {id}.")

    def handle_delete_word(self):
        id = self.kwargs.get("id", None)
        if id is None:
            raise ValueError("id must be specified as kwarg")

        self.dalw.delete_word(id)
        self.message.emit("Word Deleted.")

    def handle_delete_words(self):
        ids = self.kwargs.get("ids", None)
        if ids is None:
            raise ValueError("ids must be specified as kwarg")

        self.dalw.delete_words(ids)
        plural = "s" if len(ids) > 1 else ""
        message = f"{len(ids)} Word{plural} Deleted."
        self.message.emit(message)

    def handle_pagination(self):
        page = self.kwargs.get("page", None)
        limit = self.kwargs.get("limit", 25)
        table_count_result = self.dalw.get_words_table_count()
        if table_count_result is None:
            self.error_occurred.emit("Table not created for Sentences")
        else:
            table_count_result = table_count_result.fetchone()[0]
            total_pages = math.ceil(table_count_result / limit)
            hasNextPage = total_pages > page
            hasPrevPage = page > 1
            result = self.dalw.get_words_paginate(page, limit)
            if result is not None:
                words = [
                    Word(word[1], word[3], word[2], word[4], word[5], word[0])
                    for word in result.fetchall()
                ]
                self.pagination.emit(
                    words,
                    table_count_result,
                    total_pages,
                    page,
                    hasPrevPage,
                    hasNextPage,
                )
            else:
                self.pagination.emit(
                    None,
                    table_count_result,
                    total_pages,
                    page,
                    hasPrevPage,
                    hasNextPage,
                )

    def handle_anki_export(self):

        result = self.dalw.get_anki_export_words()
        if result is not None:
            if result is not None:
                words = [
                    Word(
                        word[1],
                        word[3],
                        word[2],
                        word[4],
                        word[5],
                        word[0],
                        word[6],
                        word[7],
                        word[8],
                        word[9],
                    )
                    for word in result.fetchall()
                ]
            self.result.emit(words)
        else:
            words = []
            self.result.emit(words)
