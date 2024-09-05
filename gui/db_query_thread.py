import math
import sqlite3

from db_query_worker import DBQueryWorker
from PySide6.QtCore import QThread, Signal, Slot
from sentsDAL import SentsDAL
from wordsDAL import WordsDAL

from dictionary import Sentence, Word


class DatabaseQueryThread(QThread):
    finished = Signal()
    result_ready = Signal((object,), (bool,))
    pagination = Signal(object, int, int, int, bool, bool)
    error_occurred = Signal(str)
    message = Signal(str)
    insertIds = Signal(list)

    def __init__(self, db_manager, operation, **kwargs):
        super().__init__()
        self.db_manager = db_manager
        self.operation = operation
        self.kwargs = kwargs

    def run(self):
        self.worker = DBQueryWorker(self.db_manager, self.operation, **self.kwargs)
        self.worker.moveToThread(self)
        self.worker.finished.connect(self.quit)
        self.worker.finished.connect(self.finished)

        self.worker.result_ready[bool].connect(self.res_ready)
        self.worker.pagination.connect(self.send_pagination)
        self.worker.error_occurred.connect(self.send_error)
        self.worker.message.connect(self.send_message)
        self.worker.insertIds.connect(self.send_insertIds)

        self.worker.do_work()

    def finished(self):
        self.worker.deleteLater()
        self.finished.emit()

    @Slot(object, int, int, int, bool, bool)
    def send_pagination(
        self, words, table_count_result, total_pages, page, hasPrevPage, hasNextPage
    ):
        self.pagination.emit(
            words, table_count_result, total_pages, page, hasPrevPage, hasNextPage
        )

    @Slot(list)
    def send_insertIds(self, ids):
        self.insertIds.emit(ids)

    @Slot(bool)
    def res_ready(self, res):
        self.result_ready[bool].emit(res)

    @Slot(str)
    def send_error(self, err):
        self.error_occurred.emit(err)

    @Slot(str)
    def send_message(self, msg):
        self.message.emit(msg)
