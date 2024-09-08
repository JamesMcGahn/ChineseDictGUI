import math
import sqlite3

from PySide6.QtCore import QObject, Signal, Slot

from db.dals import SentsDAL
from models.dictionary import Sentence


class SentsQueryWorker(QObject):
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

    @Slot()
    def do_work(self):
        self.db_manager.connect()
        self.dals = SentsDAL(self.db_manager)
        try:
            match (self.operation):
                case "insert_sentence":
                    self.handle_insert_sent()

                case "insert_sentences":
                    self.handle_insert_sents()

                case "update_sentence":
                    self.handle_update_sent()

                case "delete_sentence":
                    self.handle_delete_sent()

                case "delete_sentences":
                    self.handle_delete_sents()

                case "get_pagination_sentences":
                    self.handle_pagination()

        except sqlite3.Error as e:
            print(e)
            self.db_manager.rollback_transaction()
            self.error_occurred.emit(f"An error occurred: {e}")
        except Exception as e:
            print(e)
        finally:
            self.db_manager.disconnect()
            self.finished.emit()

    def handle_insert_sent(self):
        sentence = self.kwargs.get("sentence", None)
        if sentence is None:
            raise ValueError("sentence must be specified as kwarg")
        self.db_manager.begin_transaction()
        result = self.dals.insert_word(sentence)
        id = result.lastrowid
        sentence.id = id
        self.db_manager.commit_transaction()
        self.result.emit([sentence])

    def handle_insert_sents(self):
        sentences = self.kwargs.get("sentences", None)
        if sentences is None:
            raise ValueError("sentences must be specified as kwarg")
        self.db_manager.begin_transaction()
        id_sentences = []
        for x in sentences:
            result = self.dals.insert_sentence(x)
            id = result.lastrowid
            x.id = id
            id_sentences.append(x)
        self.db_manager.commit_transaction()
        self.result.emit(id_sentences)

    def handle_update_sent(self):
        updates = self.kwargs.get("updates", None)
        id = self.kwargs.get("id", None)
        if updates is None or id is None:
            raise ValueError("updates and id must be specified as kwarg")
        self.db_manager.begin_transaction()
        self.dals.update_sentence(id, updates)
        self.db_manager.commit_transaction()

    def handle_delete_sent(self):
        id = self.kwargs.get("id", None)
        if id is None:
            raise ValueError("id must be specified as kwarg")
        self.db_manager.begin_transaction()
        self.dals.delete_sentence(id)
        self.db_manager.commit_transaction()
        self.message.emit("Sentence Deleted.")

    def handle_delete_sents(self):
        ids = self.kwargs.get("ids", None)
        if ids is None:
            raise ValueError("id must be specified as kwarg")

        self.db_manager.begin_transaction()
        for id in ids:
            self.dals.delete_sentence(id)
        self.db_manager.commit_transaction()
        self.message.emit(f" {len(ids)} Sentence{"s" if len(ids) > 1 else "" } Deleted.")

    def handle_pagination(self):
        page = self.kwargs.get("page", None)
        limit = self.kwargs.get("limit", 25)
        table_count_result = self.dals.get_sentences_table_count()
        table_count_result = table_count_result.fetchone()[0]
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