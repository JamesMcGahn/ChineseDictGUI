from PySide6.QtCore import (
    QMutex,
    QMutexLocker,
    QThread,
    QTimer,
    QWaitCondition,
    Signal,
    Slot,
)

from .lesson_scrape_worker_v2 import LessonScraperWorkerV2


class LessonScraperThread(QThread):
    done = Signal()
    send_words_sig = Signal(list)
    send_sents_sig = Signal(object)
    send_dialogue = Signal(object, object)
    lesson_done = Signal(str, str)
    request_token = Signal()
    send_token = Signal(str)

    def __init__(self, lesson_list, transcribe_lesson=True):
        super().__init__()
        self.lesson_list = lesson_list
        self.transcribe_lesson = transcribe_lesson
        self._mutex = QMutex()
        self._wait_condition = QWaitCondition()
        self._stop = False
        self._paused = False

    @Slot()
    def run(self):
        print("Starting Lesson Scraper Thread")
        self.lesson_list = [x for x in self.lesson_list if x]

        self.worker = LessonScraperWorkerV2(
            self.lesson_list,
            self._mutex,
            self._wait_condition,
            self,
            self.transcribe_lesson,
        )
        self.worker.moveToThread(self)

        self.worker.finished.connect(self.worker_finished)
        self.worker.send_sents_sig.connect(self.send_sents_sig)
        self.worker.send_words_sig.connect(self.send_words_sig)
        self.worker.send_dialogue.connect(self.send_dialogue)
        self.worker.lesson_done.connect(self.lesson_done)
        self.worker.request_token.connect(self.request_token)
        self.send_token.connect(self.worker.receive_token)
        QTimer.singleShot(0, self.worker.do_work)
        self.exec()

    @Slot(str)
    def receive_token(self, token):
        self.send_token.emit(token)

    def worker_finished(self):
        self.worker.deleteLater()
        self.done.emit()

    @Slot()
    def resume(self):
        with QMutexLocker(self._mutex):  # Automatic lock and unlock
            self._paused = False
            self._wait_condition.wakeOne()

    @Slot()
    def pause(self):
        with QMutexLocker(self._mutex):
            self._paused = True

    @Slot()
    def stop(self):
        """Stop the thread."""
        with QMutexLocker(self._mutex):
            self._stop = True
            self._paused = False
            self._wait_condition.wakeAll()
