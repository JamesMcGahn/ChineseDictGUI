from PySide6.QtCore import QThread, Signal, Slot

from db.workers import LessonsQueryWorker, SentsQueryWorker, WordsQueryWorker


class DatabaseQueryThread(QThread):
    finished = Signal()
    pagination = Signal(object, int, int, int, bool, bool)
    error_occurred = Signal(str)
    message = Signal(str)
    result = Signal(list)

    def __init__(self, dtype, operation, **kwargs):
        super().__init__()

        self.operation = operation
        self.kwargs = kwargs

        if dtype in ["words", "sents", "lessons"]:
            self.dtype = dtype
        else:
            raise ValueError("dtype must be one of 'words' or 'sents'")

    def run(self):
        if self.dtype == "words":
            self.worker = WordsQueryWorker(self.operation, **self.kwargs)
        elif self.dtype == "sents":
            self.worker = SentsQueryWorker(self.operation, **self.kwargs)
        elif self.dtype == "lessons":
            self.worker = LessonsQueryWorker(self.operation, **self.kwargs)

        self.worker.moveToThread(self)
        self.worker.finished.connect(self.quit)
        self.worker.finished.connect(self.worker_finished)

        self.worker.pagination.connect(self.send_pagination)
        self.worker.error_occurred.connect(self.send_error)
        self.worker.message.connect(self.send_message)
        self.worker.result.connect(self.send_result)

        self.worker.do_work()

    def worker_finished(self):
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
    def send_result(self, ids):
        self.result.emit(ids)

    @Slot(str)
    def send_error(self, err):
        self.error_occurred.emit(err)

    @Slot(str)
    def send_message(self, msg):
        self.message.emit(msg)
