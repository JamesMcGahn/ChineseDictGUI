import math
import sqlite3
import time

from PySide6.QtCore import QObject, Signal, Slot

from models.dictionary import Word

from ..dals import WordsDAL


class WordsQueryWorker(QObject):
    finished = Signal()
    pagination = Signal(object, int, int, int, bool, bool)
    error_occurred = Signal(str)
    message = Signal(str)
    result = Signal(list)


    def __init__(self, db_manager, operation, **kwargs):
        super().__init__()
        self.db_manager = db_manager
        self.operation = operation
        self.kwargs = kwargs
        self.retry_pagination  = 0

    @Slot()
    def do_work(self):
        self.db_manager.connect()
        self.dalw = WordsDAL(self.db_manager)
        try:
            match (self.operation):
                case "insert_word":
                    self.handle_insert_word()

                case "insert_words":
                    self.handle_insert_words()

                case "update_word":
                    self.handle_update_word()

                case "delete_word":
                    self.handle_delete_word()

                case "delete_words":
                    self.handle_delete_words()

                case "get_pagination_words":
                    self.handle_pagination()
        except sqlite3.OperationalError as e:
            if 'no such table' in str(e):
                if self.operation == "get_pagination_words" and self.retry_pagination < 2:
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


    def handle_insert_word(self):
        word = self.kwargs.get("word", None)
        if word is None:
            raise ValueError("word must be specified as kwarg")
        self.db_manager.begin_transaction()
        result = self.dalw.insert_word(word)
        id = result.lastrowid
        word.id = id
        self.db_manager.commit_transaction()
        self.result.emit([word])

    def handle_insert_words(self):
        words = self.kwargs.get("words", None)
        if words is None:
            raise ValueError("words must be specified as kwarg")
        self.db_manager.begin_transaction()
        id_words = []
        for x in words:
            result = self.dalw.insert_word(x)
            id = result.lastrowid
            x.id = id
            id_words.append(x)
        self.db_manager.commit_transaction()
        self.result.emit(id_words)

    def handle_update_word(self):
        updates = self.kwargs.get("updates", None)
        id = self.kwargs.get("id", None)
        if updates is None or id is None:
            raise ValueError("word and id must be specified as kwarg")
        self.db_manager.begin_transaction()
        suc = self.dalw.update_word(id, updates)
        if suc.rowcount == 1:
            self.message.emit("Update Saved.")
        self.db_manager.commit_transaction()

    def handle_delete_word(self):
        id = self.kwargs.get("id", None)
        if id is None:
            raise ValueError("id must be specified as kwarg")
        self.db_manager.begin_transaction()
        self.dalw.delete_word(id)
        self.db_manager.commit_transaction()
        self.message.emit("Word Deleted.")

    def handle_delete_words(self):
        ids = self.kwargs.get("ids", None)
        if ids is None:
            raise ValueError("ids must be specified as kwarg")
        self.db_manager.begin_transaction()
        for id in ids:
            self.dalw.delete_word(id)
        self.db_manager.commit_transaction()
        self.message.emit(f" {len(ids)} Word{"s" if len(ids) > 1 else "" } Deleted.")

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