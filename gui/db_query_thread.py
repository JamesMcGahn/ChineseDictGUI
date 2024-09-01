import math
import sqlite3

from PySide6.QtCore import QThread, Signal
from sentsDAL import SentsDAL
from wordsDAL import WordsDAL

from dictionary import Sentence, Word


class DatabaseQueryThread(QThread):
    result_ready = Signal((object,), (bool,))
    pagination = Signal(object, int, int, int, bool, bool)
    error_occurred = Signal(str)
    message = Signal(str)

    def __init__(self, db_manager, operation, **kwargs):
        super().__init__()
        self.db_manager = db_manager
        self.operation = operation
        self.kwargs = kwargs

    def run(self):
        self.db_manager.connect()
        self.dalw = WordsDAL(self.db_manager)
        self.dals = SentsDAL(self.db_manager)
        try:
            match (self.operation):
                case "insert_word":
                    word = self.kwargs.get("word", None)
                    if word is None:
                        raise ValueError("word must be specified as kwarg")
                    self.db_manager.begin_transaction()
                    self.dalw.insert_word(word)
                    self.db_manager.commit_transaction()

                case "insert_words":
                    words = self.kwargs.get("words", None)
                    if words is None:
                        raise ValueError("words must be specified as kwarg")
                    self.db_manager.begin_transaction()
                    for x in words:
                        self.dalw.insert_word(x)
                    self.db_manager.commit_transaction()

                case "update_word":
                    updates = self.kwargs.get("updates", None)
                    id = self.kwargs.get("id", None)
                    if updates is None or id is None:
                        raise ValueError("word and id must be specified as kwarg")
                    self.db_manager.begin_transaction()
                    suc = self.dalw.update_word(id, updates)

                    if suc.rowcount == 1:
                        self.message.emit("Update Saved.")
                    self.db_manager.commit_transaction()

                case "delete_word":
                    id = self.kwargs.get("id", None)
                    if id is None:
                        raise ValueError("id must be specified as kwarg")
                    self.db_manager.begin_transaction()
                    self.dalw.delete_word(id)
                    self.db_manager.commit_transaction()

                case "get_pagination_words":
                    print("here")
                    page = self.kwargs.get("page", None)
                    limit = self.kwargs.get("limit", 25)
                    table_count_result = self.dalw.get_words_table_count()
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
                case "insert_sentence":
                    sentence = self.kwargs.get("sentence", None)
                    if sentence is None:
                        raise ValueError("sentence must be specified as kwarg")
                    self.db_manager.begin_transaction()
                    self.dals.insert_word(sentence)
                    self.db_manager.commit_transaction()

                case "insert_sentences":
                    sentences = self.kwargs.get("sentences", None)
                    if sentences is None:
                        raise ValueError("sentences must be specified as kwarg")
                    self.db_manager.begin_transaction()
                    for x in sentences:
                        self.dals.insert_sentence(x)
                    self.db_manager.commit_transaction()

                case "update_sentence":
                    updates = self.kwargs.get("updates", None)
                    id = self.kwargs.get("id", None)
                    if updates is None or id is None:
                        raise ValueError("updates and id must be specified as kwarg")
                    self.db_manager.begin_transaction()
                    self.dals.update_sentence(id, updates)
                    self.db_manager.commit_transaction()

                case "delete_sentence":
                    id = self.kwargs.get("id", None)
                    if id is None:
                        raise ValueError("id must be specified as kwarg")
                    self.db_manager.begin_transaction()
                    self.dals.delete_sentence(id)
                    self.db_manager.commit_transaction()

                case "get_pagination_sentences":
                    page = self.kwargs.get("page", None)
                    limit = self.kwargs.get("limit", 25)
                    table_count_result = self.dals.get_sentences_table_count()
                    table_count_result = table_count_result.fetchone()[0]
                    print(table_count_result)
                    total_pages = math.ceil(table_count_result / limit)
                    hasNextPage = total_pages > page
                    hasPrevPage = page > 1
                    result = self.dals.get_sentences_paginate(page, limit)
                    if result is not None:
                        sentences = [
                            Sentence(
                                sent[1], sent[2], sent[3], sent[4], sent[5], sent[0]
                            )
                            for sent in result.fetchall()
                        ]
                        self.pagination.emit(
                            sentences,
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
            self.result_ready[bool].emit(True)
        except sqlite3.Error as e:
            self.db_manager.rollback_transaction()
            self.error_occurred.emit(f"An error occurred: {e}")
        except Exception as e:
            print(e)
        finally:
            self.db_manager.disconnect()
