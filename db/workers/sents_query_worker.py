import math
import sqlite3
import time

from PySide6.QtCore import QObject, Signal, Slot

from models.dictionary import Sentence

from ..dals import SentsDAL
from ..db_manager import DatabaseManager


class SentsQueryWorker(QObject):
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
        self.dals = SentsDAL(self.db_manager)
        try:
            match (self.operation):
                case "insert_sentence":
                    self.handle_insert_sent()

                case "insert_sentences":
                    self.handle_insert_sents()

                case "update_sentence":
                    self.handle_update_sent()

                case "update_sentences":
                    self.handle_update_sents()

                case "delete_sentence":
                    self.handle_delete_sent()

                case "delete_sentences":
                    self.handle_delete_sents()

                case "get_pagination_sentences":
                    self.handle_pagination()

        except sqlite3.OperationalError as e:
            if "no such table" in str(e):
                if (
                    self.operation == "get_pagination_sentences"
                    and self.retry_pagination < 2
                ):
                    time.sleep(10)
                    self.handle_pagination()
                    self.retry_pagination += 1
                else:
                    self.error_occurred.emit(f"An error occurred: {e}")

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
        result = self.dals.insert_word(sentence)
        id = result.lastrowid
        sentence.id = id
        self.result.emit([sentence])

    def handle_insert_sents(self):
        # TODO change to insert many instead of LOOP
        sentences = self.kwargs.get("sentences", None)
        if sentences is None:
            raise ValueError("sentences must be specified as kwarg")
        id_sentences = []
        for x in sentences:
            result = self.dals.insert_sentence(x)
            id = result.lastrowid
            x.id = id
            id_sentences.append(x)
        self.result.emit(id_sentences)

    def handle_update_sent(self):
        updates = self.kwargs.get("updates", None)
        id = self.kwargs.get("id", None)
        if updates is None or id is None:
            raise ValueError("updates and id must be specified as kwarg")
        self.dals.update_sentence(id, updates)

    def handle_update_sents(self):
        sentences = self.kwargs.get("sentences", None)
        if sentences is None:
            raise ValueError("updates specified as kwarg")

        # TODO - make rows and update at once?
        for sent in sentences:

            id = sent["id"]
            updates = sent["updates"]
            # print(id,updates)
            self.dals.update_sentence(id, updates)

    def handle_delete_sent(self):
        id = self.kwargs.get("id", None)
        if id is None:
            raise ValueError("id must be specified as kwarg")

        self.dals.delete_sentence(id)

        self.message.emit("Sentence Deleted.")

    def handle_delete_sents(self):
        ids = self.kwargs.get("ids", None)
        if ids is None:
            raise ValueError("id must be specified as kwarg")

        self.dals.delete_sentences(ids)
        plural = "s" if len(ids) > 1 else ""
        message = f"{len(ids)} Sentence{plural} Deleted."
        self.message.emit(message)

    def handle_pagination(self):
        page = self.kwargs.get("page", 1)
        limit = self.kwargs.get("limit", 25)
        table_count_result = self.dals.get_sentences_table_count()
        if table_count_result is None:
            self.error_occurred.emit("Table not created for Sentences")
        else:
            table_count_result = table_count_result.fetchone()[0]
            total_pages = math.ceil(table_count_result / limit)
            hasNextPage = total_pages > page
            hasPrevPage = page > 1
            result = self.dals.get_sentences_paginate(page, limit)
            if result is not None:
                sentences = [
                    Sentence(sent[1], sent[2], sent[3], sent[4], sent[5], sent[0])
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
