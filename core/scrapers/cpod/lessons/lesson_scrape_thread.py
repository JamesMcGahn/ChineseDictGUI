from PySide6.QtCore import QMutex, QMutexLocker, QThread, QWaitCondition, Signal, Slot

from keys import keys
from services.network import SessionManager

from .lesson_scrape_worker import LessonScraperWorker
from .web_scrape import WebScrape


class LessonScraperThread(QThread):
    finished = Signal()
    send_words_sig = Signal(list)
    send_sents_sig = Signal(object)
    send_dialogue = Signal(object, object)

    def __init__(self, lesson_list):
        super().__init__()
        self.lesson_list = lesson_list
        self._mutex = QMutex()
        self._wait_condition = QWaitCondition()
        self._stop = False
        self._paused = False

    @Slot()
    def run(self):
        print("starting thread")

        sess = SessionManager()
        # TODO remove keys.py file
        self.wb = WebScrape(sess, keys["url"])
        self.wb.init_driver()
        self.worker = LessonScraperWorker(
            self.wb, self.lesson_list, self._mutex, self._wait_condition, self
        )
        self.worker.moveToThread(self)

        self.worker.finished.connect(self.quit)
        self.worker.finished.connect(self.worker_finished)
        self.worker.send_sents_sig.connect(self.send_sents_sig)
        self.worker.send_words_sig.connect(self.send_words_sig)
        self.worker.send_dialogue.connect(self.send_dialogue)
        self.worker.do_work()

    def worker_finished(self):
        self.wb.close()
        self.worker.deleteLater()
        self.finished.emit()

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
